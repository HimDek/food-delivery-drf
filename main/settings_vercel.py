from pathlib import Path
from .settings_base import INSTALLED_APPS
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = [".vercel.app", "now.sh"]

INSTALLED_APPS.remove('django.contrib.admin')
INSTALLED_APPS.remove('django.contrib.messages')
INSTALLED_APPS.remove('django.contrib.staticfiles')

ROOT_URLCONF = 'main.urls_vercel'