from pathlib import Path
from dotenv import load_dotenv, dotenv_values
import os


load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-x=-zje230)4rie$8^*cguah_0o^scs)mp&maq+q&f19l_jez-7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "user",
    "10.12.12.5",
    "0.0.0.0"
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'daphne',  # Add Daphne here
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'userService',  # userService app
    'rest_framework',  # django_rest_framework
	'rest_framework.authtoken',  # django_rest_framework
	'channels',  # django_channels
	'corsheaders',  # django_cors_headers
    'crispy_forms',
    'crispy_bootstrap4',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'userService.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'userService.wsgi.application'
ASGI_APPLICATION = 'userService.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# # Debug database environment variables
# print("=== Database Environment Variables ===")
# print(f"DB_NAME: {os.environ.get('DB_NAME')}")
# print(f"DB_USER: {os.environ.get('DB_USER')}")
# print(f"DB_PASSWORD: {os.environ.get('DB_PASSWORD')}")
# print(f"DB_HOST: {os.environ.get('DB_HOST')}")
# print(f"DB_PORT: {os.environ.get('DB_PORT')}")
# print("================================")

# # Validate required environment variables
# required_db_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT']
# missing_vars = [var for var in required_db_vars if not os.environ.get(var)]
# if missing_vars:
#     print("❌ Missing required database environment variables:")
#     for var in missing_vars:
#         print(f"   - {var}")
#     raise Exception("Missing required database configuration")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# # Debug final configuration
# db_config = DATABASES['default']
# print("\n=== Final Database Configuration ===")
# print(f"ENGINE: {db_config['ENGINE']}")
# print(f"NAME: {db_config['NAME']}")
# print(f"USER: {db_config['USER']}")
# print(f"PASSWORD: {'*' * len(str(db_config['PASSWORD'])) if db_config['PASSWORD'] else 'None'}")
# print(f"HOST: {db_config['HOST']}")
# print(f"PORT: {db_config['PORT']}")
# print("================================")

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Django Authentication Backends
# https://docs.djangoproject.com/en/5.1/ref/settings/#authentication-backends

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Settings
CORS_ORIGIN_ALLOW_ALL = True  # Development only

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://localhost:5173",
    "http://10.12.12.5:5173",
    "https://10.12.12.5:5173",
    "http://localhost",
    "https://localhost",
    "http://10.12.12.5",
    "https://10.12.12.5"
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]