from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('PRODUCTION_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


INSTALLED_APPS = INSTALLED_APPS.remove('django.contrib.admin')


TEMPLATES = []