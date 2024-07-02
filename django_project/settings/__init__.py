# ruff: noqa
import os

from .base import *

if os.environ.get("ENV_NAME") == "production":
    from .production import *
else:
    from .development import *
