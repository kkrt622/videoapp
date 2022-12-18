from .settings_common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

try:
    from .settings_local import *  # noqa: F401,F403
except ImportError:
    pass
