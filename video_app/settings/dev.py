from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAUTL_FROM_EMAIL = "admin@example.com"

try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass
