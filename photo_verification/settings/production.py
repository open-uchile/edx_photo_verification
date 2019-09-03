from .base import *

# Django configuration
SECRET_KEY = environ["SECRET_KEY"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "photo_verification",
    }
}

# EDX Configuration
API_ACCESS_KEY = environ["API_ACCESS_KEY"]
API_SECRET_KEY = environ["API_SECRET_KEY"]
LMS_BASE = environ["LMS_BASE"]
DECRYPTION_FILE_PATH = environ["DECRYPTION_FILE_PATH"]
