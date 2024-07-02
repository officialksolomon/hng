import os

from .base import *  # noqa: F403  # noqa: F403

DEBUG = False
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
ALLOWED_HOSTS = [ "hng.pythonanywhere.com"]

# Database Configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USERNAME"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST_ADDRESS"),
    }
}

# HTTPS Settings (if not using a web server like Nginx or Apache)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = 465
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
# EMAIL_USE_TLS = True
EMAIL_USE_SSL = True
DEFAULT_EMAIL_USERNAME = os.getenv("DEFAULT_EMAIL_USERNAME")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")


# Media files (user-uploaded content)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
