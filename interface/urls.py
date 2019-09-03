from django.conf.urls import url, include
from django.contrib import admin

from .views import *

urlpatterns = [
    url(r"^$", PhotoValidationListView.as_view(), name="interface_index"),
    url(
        r"^submit_response$",
        PhotoValidationSendResponse.as_view(),
        name="submit_response",
    ),
]
