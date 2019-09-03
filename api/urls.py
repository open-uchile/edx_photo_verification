from django.conf.urls import url

from . import views

urlpatterns = [url("create_request", views.create_request, name="create_request")]
