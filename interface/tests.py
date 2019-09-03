# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from collections import namedtuple
from unittest.mock import Mock, patch

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase
from django.test.client import RequestFactory

from api.models import PhotoVerificationRequest
from api.views import create_request
from interface.views import PhotoValidationSendResponse


# Create your tests here.
class InterfaceSubmitTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.photo = PhotoVerificationRequest.objects.create(
            edx_id="76ee5aa9-9ed1-4a62-ae99-9479694422fb",
            expected_name="One Test",
            photoid="1",
            photoid_key="2",
            userphoto="3",
            userphoto_key="4",
            response_to="/dummy",
            verified=0,
        )
        self.user = self.user = User.objects.create_user(
            username="jacob", email="jacob@jacob.jacob", password="top_secret"
        )

    @patch("requests.post")
    def test_send_responce_success(self, post):
        with self.settings(API_ACCESS_KEY="123"):
            post.return_value = namedtuple("Request", ["status_code"])(200)
            data = {"id": self.photo.id, "result": "PASS"}
            request = self.factory.post("/interface/submit_responce", data)
            request.user = self.user
            response = PhotoValidationSendResponse.as_view()(request)
            self.assertEqual(response.content, b"")
            self.assertEqual(response.status_code, 302)

            self.assertEqual(post.call_args[0][0], self.photo.response_to)
            self.assertEqual(
                post.call_args[1]["headers"],
                {
                    "Authorization": "SSI 123:SECRET_KEY",
                    "Content-Type": "application/json",
                },
            )
            self.assertDictEqual(
                json.loads(post.call_args[1]["data"]),
                {
                    "EdX-ID": "76ee5aa9-9ed1-4a62-ae99-9479694422fb",
                    "Result": "PASS",
                    "Reason": [],
                    "MessageType": "approved",
                },
            )

            reloaded = PhotoVerificationRequest.objects.get(id=self.photo.id)
            self.assertEqual(reloaded.verified, PhotoVerificationRequest.VERIFIED)

    @patch("requests.post")
    def test_send_responce_require_login(self, post):
        with self.settings(API_ACCESS_KEY="123"):
            post.return_value = namedtuple("Request", ["status_code"])(200)
            data = {"id": self.photo.id, "result": "PASS"}
            request = self.factory.post("/interface/submit_responce", data)
            request.user = AnonymousUser()
            response = PhotoValidationSendResponse.as_view()(request)
            self.assertEqual(
                response.url, "/accounts/login/?next=/interface/submit_responce"
            )
            self.assertEqual(response.status_code, 302)

    @patch("requests.post")
    def test_send_responce_unsuccessful(self, post):
        post.return_value = namedtuple("Request", ["status_code"])(200)
        data = {"id": self.photo.id, "result": "FAIL"}
        request = self.factory.post("/interface/submit_responce", data)
        request.user = self.user
        response = PhotoValidationSendResponse.as_view()(request)
        self.assertEqual(response.content, b"")
        self.assertEqual(response.status_code, 302)

        self.assertEqual(post.call_args[0][0], self.photo.response_to)
        self.assertDictEqual(
            json.loads(post.call_args[1]["data"]),
            {
                "EdX-ID": "76ee5aa9-9ed1-4a62-ae99-9479694422fb",
                "Result": "FAIL",
                "Reason": [],
                "MessageType": "error",
            },
        )

        reloaded = PhotoVerificationRequest.objects.get(id=self.photo.id)
        self.assertEqual(reloaded.verified, PhotoVerificationRequest.INVALID)

    @patch("requests.post")
    def test_send_responce_unsuccessful_with_messages(self, post):
        post.return_value = namedtuple("Request", ["status_code"])(200)
        data = {
            "id": self.photo.id,
            "result": "FAIL",
            "userPhotoReasons": "Error 1",
            "photoIdReasons": "Error 2",
            "generalReasons": "Error 3",
        }
        request = self.factory.post("/interface/submit_responce", data)
        request.user = self.user
        response = PhotoValidationSendResponse.as_view()(request)
        self.assertEqual(response.content, b"")
        self.assertEqual(response.status_code, 302)

        error_list = [
            {"userPhotoReasons": "Error 1"},
            {"photoIdReasons": "Error 2"},
            {"generalReasons": "Error 3"},
        ]
        self.assertEqual(post.call_args[0][0], self.photo.response_to)
        self.assertDictEqual(
            json.loads(post.call_args[1]["data"]),
            {
                "EdX-ID": "76ee5aa9-9ed1-4a62-ae99-9479694422fb",
                "Result": "FAIL",
                "MessageType": "error",
                "Reason": error_list,
            },
        )

        reloaded = PhotoVerificationRequest.objects.get(id=self.photo.id)
        self.assertEqual(json.loads(reloaded.invalid_message), error_list)
        self.assertEqual(reloaded.verified, PhotoVerificationRequest.INVALID)

    @patch("requests.post")
    def test_send_responce_invalid_backend(self, post):
        post.return_value = namedtuple("Request", ["status_code", "text"])(
            500, "response"
        )
        data = {"id": self.photo.id, "result": "PASS"}
        request = self.factory.post("/interface/submit_responce", data)
        request.user = self.user
        self.assertRaises(Exception, PhotoValidationSendResponse.as_view(), request)

        reloaded = PhotoVerificationRequest.objects.get(id=self.photo.id)
        self.assertEqual(reloaded.verified, PhotoVerificationRequest.UNDEFINED)

    def test_send_responce_already_submitted_verification(self):
        self.photo.verified = 1
        self.photo.save()
        data = {"id": self.photo.id, "result": "PASS"}
        request = self.factory.post("/interface/submit_responce", data)
        request.user = self.user
        self.assertRaises(Exception, PhotoValidationSendResponse.as_view(), request)

    @patch("requests.post")
    def test_send_responce_unknown_type(self, post):
        post.return_value = 3
        data = {"id": self.photo.id, "result": "unkwnown"}
        request = self.factory.post("/interface/submit_responce", data)
        request.user = self.user
        self.assertRaises(Exception, PhotoValidationSendResponse.as_view(), request)
