# -*- coding: utf-8 -*-
from django.conf import settings
from django.test import TestCase
from django.test.client import RequestFactory

from api.models import PhotoVerificationRequest
from api.views import create_request
import json

from api.encryption.ssencrypt import generate_signed_message


class MiddleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_insert_data(self):
        data = {
            "EdX-ID": "76ee5aa9-9ed1-4a62-ae99-9479694422fb",
            "ExpectedName": "BoB Mechon",
            "PhotoID": "/media/photo_id/76ee5aa9-9ed1-4a62-ae99-9479694422fb",
            "PhotoIDKey": "qbwfRy2wDh/Dwix2eLpN/88RgKJW/YUkonTTczOclkgMzr8aSaUmjqxs0BxJKRHHHgM1lLU1Q1K5\nLfATeUUcXZmnTMqy3Sy1WjHPMzOrUmd4fNX1sPRJ6iMrthJm/eFP/CI5oNunZFQGUgD8GfXRntns\nhRd6bV6IHsUekyH0WEo=\n",
            "SendResponseTo": "https://localhost/verify_student/results_callback",
            "UserPhoto": "/media/face/76ee5aa9-9ed1-4a62-ae99-9479694422fb",
            "UserPhotoKey": "UhbmpdSCtjEfayz2JfNUdVcnq/NebNrzWDkf/wyr7wd8LCf37u0CKnH4QEfwjNJ2lid9NgFrlVEN\nZ15yLogZJ3FsjpbPt+ArfEftIZym5X58lUlLB8JuuVlspwi0s3wDXrlgX0KhfoXMuqvCf3XXE8H9\noLME5I8xuhx0CkaA3bQ=\n",
        }

        with self.settings(API_ACCESS_KEY="123", API_SECRET_KEY="asd"):
            _, _, signature = generate_signed_message(
                "POST",
                {"Content-Type": "application/json"},
                data,
                settings.API_ACCESS_KEY,
                settings.API_SECRET_KEY,
            )
            request = self.factory.post(
                "/api/create_request",
                data,
                HTTP_AUTHORIZATION=signature,
                content_type="application/json",
            )
            # request.body = json.dumps(data).encode()
            r = create_request(request)

            result = PhotoVerificationRequest.objects.first()
            self.assertIsNotNone(result)
            self.assertEqual(result.edx_id, data["EdX-ID"])
            self.assertEqual(result.expected_name, data["ExpectedName"])
            self.assertEqual(result.photoid, data["PhotoID"])
            self.assertEqual(result.photoid_key, data["PhotoIDKey"])
            self.assertEqual(result.response_to, data["SendResponseTo"])
            self.assertEqual(result.userphoto, data["UserPhoto"])
            self.assertEqual(result.userphoto_key, data["UserPhotoKey"])
            self.assertEqual(result.verified, 0)

    """
    def test_insert_invalid_key(self):
        data = {
            "EdX-ID": "76ee5aa9-9ed1-4a62-ae99-9479694422fb",
            "ExpectedName": "BoB Mechon",
            "PhotoID": "/media/photo_id/76ee5aa9-9ed1-4a62-ae99-9479694422fb",
            "PhotoIDKey": "qbwfRy2wDh/Dwix2eLpN/88RgKJW/YUkonTTczOclkgMzr8aSaUmjqxs0BxJKRHHHgM1lLU1Q1K5\nLfATeUUcXZmnTMqy3Sy1WjHPMzOrUmd4fNX1sPRJ6iMrthJm/eFP/CI5oNunZFQGUgD8GfXRntns\nhRd6bV6IHsUekyH0WEo=\n",
            "SendResponseTo": "https://localhost/verify_student/results_callback",
            "UserPhoto": "/media/face/76ee5aa9-9ed1-4a62-ae99-9479694422fb",
            "UserPhotoKey": "UhbmpdSCtjEfayz2JfNUdVcnq/NebNrzWDkf/wyr7wd8LCf37u0CKnH4QEfwjNJ2lid9NgFrlVEN\nZ15yLogZJ3FsjpbPt+ArfEftIZym5X58lUlLB8JuuVlspwi0s3wDXrlgX0KhfoXMuqvCf3XXE8H9\noLME5I8xuhx0CkaA3bQ=\n"
        }
        
        with self.settings(API_ACCESS_KEY='123', API_SECRET_KEY='asd'):
            _, _, signature = generate_signed_message('POST', {"Content-Type": "application/json"}, data, 9876543, settings.API_SECRET_KEY)
            request = self.factory.post('/api/create_request', {}, HTTP_AUTHORIZATION=signature)
            request.body = json.dumps(data).encode()
            r = create_request(request)

            result = PhotoVerificationRequest.objects.first()
            self.assertIsNone(result)"""
