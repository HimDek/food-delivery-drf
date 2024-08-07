import os
from .settings_base import INSTALLED_APPS

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
