# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.decorators import method_decorator

from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import ListView, View
from django.contrib.auth.decorators import login_required

from api.models import PhotoVerificationRequest

import json
import requests

# Create your views here.
class PhotoValidationListView(ListView):
    model = PhotoVerificationRequest
    queryset = PhotoVerificationRequest.objects.filter(
        verified=PhotoVerificationRequest.UNDEFINED
    )
    template_name = "interface/request_list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PhotoValidationListView, self).get_context_data(**kwargs)
        for item in context["photoverificationrequest_list"]:
            print(item)
        return context


class PhotoValidationSendResponse(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Send the validation request.
            We can authenticate with EdX using a valid API_ACCESS_KEY
        """
        # Het the photo we are validating
        photo = PhotoVerificationRequest.objects.get(id=request.POST.get("id"))

        if photo.verified != PhotoVerificationRequest.UNDEFINED:
            # We cant update an already verified image
            raise ValidationError("You can't verify an already processed item")

        message = self.send_verification(request, photo)
        if not message:
            return redirect("interface_index")
        raise Exception("Error processing verification: {}".format(message))

    def send_verification(self, request, photo):
        headers = {
            "Authorization": "SSI {}:SECRET_KEY".format(settings.API_ACCESS_KEY),
            "Content-Type": "application/json",
        }
        data = {"EdX-ID": photo.edx_id, "Result": "", "Reason": [], "MessageType": ""}
        if request.POST.get("result") == "PASS":
            photo.verified = PhotoVerificationRequest.VERIFIED
            data["Result"] = "PASS"
            data["MessageType"] = "approved"
        elif request.POST.get("result") == "FAIL":
            photo.verified = PhotoVerificationRequest.INVALID
            data["Result"] = "FAIL"
            data["MessageType"] = "error"
            error_types = ("userPhotoReasons", "photoIdReasons", "generalReasons")
            for error in error_types:
                if request.POST.get(error, "").strip() != "":
                    data["Reason"].append({error: request.POST.get(error).strip()})
        else:
            # We are not using "SYSTEM FAIL" message right now
            raise Exception(
                "Wrong result type {}".format(request.POST.get("result", None))
            )

        # Send request to the LMS
        result = requests.post(
            photo.response_to, data=json.dumps(data), headers=headers
        )
        if result.status_code == 200:
            photo.invalid_message = json.dumps(data["Reason"])
            photo.save()
            return ""
        else:
            # Error found, return the message
            return result.text
