# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import PhotoVerificationRequest
from .encryption.ssencrypt import has_valid_signature

import json


@csrf_exempt
def create_request(request):
    # TODO: Check authorization
    headers = {
        "Content-Type": request.META.get("CONTENT_TYPE"),
        "Date": request.META.get("HTTP_DATE"),
        "Authorization": request.META.get("HTTP_AUTHORIZATION"),
    }
    # Only authorize by public ACCESS_KEY for now
    # if not has_valid_signature('POST', headers, request.POST, settings.API_ACCESS_KEY, settings.API_SECRET_KEY):
    pub_key = request.META.get("HTTP_AUTHORIZATION").split(":")[0][4:]
    if pub_key != settings.API_ACCESS_KEY:
        return HttpResponse("Unauthorized", status=401)

    body = json.loads(request.body.decode("utf-8"))
    PhotoVerificationRequest.objects.create(
        edx_id=body.get("EdX-ID"),
        expected_name=body.get("ExpectedName"),
        photoid=body.get("PhotoID"),
        photoid_key=body.get("PhotoIDKey"),
        userphoto=body.get("UserPhoto"),
        userphoto_key=body.get("UserPhotoKey"),
        response_to=body.get("SendResponseTo"),
    )

    return HttpResponse("")
