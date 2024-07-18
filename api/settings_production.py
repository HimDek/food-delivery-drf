from pathlib import Path
from .settings_base import INSTALLED_APPS
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('PRODUCTION_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

INSTALLED_APPS.remove('django.contrib.admin')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True
    },
]


ROOT_URLCONF = 'api.urls_production'