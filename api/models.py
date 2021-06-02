# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from urllib import request

import base64
import logging
log = logging.getLogger(__name__)

from .encryption.ssencrypt import rsa_decrypt, decode_and_decrypt


class PhotoVerificationRequest(models.Model):
    UNDEFINED = 0
    VERIFIED = 1
    INVALID = 2
    VERIFIED_STATUS = (
        (UNDEFINED, "Undefined"),
        (VERIFIED, "Verified"),
        (INVALID, "Invalid"),
    )
    edx_id = models.TextField()
    expected_name = models.TextField()
    photoid = models.TextField()
    photoid_key = models.TextField()
    userphoto = models.TextField()
    userphoto_key = models.TextField()
    response_to = models.TextField()
    verified = models.IntegerField(choices=VERIFIED_STATUS, default=UNDEFINED)
    invalid_message = models.TextField(default="", blank=True)

    @property
    def photo_id(self):
        aes_key = rsa_decrypt(
            base64.b64decode(self.photoid_key),
            open(settings.DECRYPTION_FILE_PATH, "r").read(),
        )
        base_url = settings.LMS_BASE
        url = base_url + self.photoid
        try:
            data = request.urlopen(request.Request(url)).read()
            result = decode_and_decrypt(data, aes_key)
            return base64.b64encode(result).decode("utf-8")
        except Exception as e:
            log.exception("Error loading photo_id {} ({})".format(self.id, url))
            return ""

    @property
    def photo_user(self):
        aes_key = rsa_decrypt(
            base64.b64decode(self.userphoto_key),
            open(settings.DECRYPTION_FILE_PATH, "r").read(),
        )
        base_url = settings.LMS_BASE
        url = base_url + self.userphoto
        try:
            data = request.urlopen(request.Request(url)).read()
            result = decode_and_decrypt(data, aes_key)
            return base64.b64encode(result).decode("utf-8")
        except Exception as e:
            log.exception("Error loading photo_user {} ({})".format(self.id, url))
            return ""
