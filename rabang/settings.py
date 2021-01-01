import importlib
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


def get_env():
    for stage in ['local', 'development', 'production']:
        module_name = f"rabang.env.{stage}"
        found = importlib.util.find_spec(module_name)
        if found:
            return importlib.import_module(module_name)
    raise ImproperlyConfigured('환경설정 파일을 찾을 수 없습니다.')

env = get_env()

STAGE = env.STAGE

BASE_DIR = env.BASE_DIR

SECRET_KEY = env.SECRET_KEY

DEBUG = env.DEBUG

ALLOWED_HOSTS = env.ALLOWED_HOSTS

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'simple_history',
    'ordered_model',
    'solo',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'sequences.apps.SequencesConfig',
    'seller.apps.SellerConfig',
    'common.apps.CommonConfig',
    'product.apps.ProductConfig',
    'account.apps.AccountConfig',
    'broadcast.apps.BroadcastConfig',
    'payment.apps.PaymentConfig',
    'mall.apps.MallConfig',
    'chat.apps.ChatConfig'
]

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication'
    ]
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rabang.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'rabang.wsgi.application'
ASGI_APPLICATION = 'rabang.asgi.application'

CHANNEL_LAYERS = env.CHANNEL_LAYERS

DATABASES = env.DATABASES
CACHES = env.CACHES

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

AUTH_USER_MODEL = 'account.User'

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'templates', 'static'), ]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

AWS_ACCESS_KEY_ID = env.AWS_S3_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = env.AWS_S3_SECRET_ACCESS_KEY
DEFAULT_FILE_STORAGE = 'rabang.storages.MediaStorage'
STATICFILES_STORAGE = 'rabang.storages.StaticStorage'
AWS_STORAGE_BUCKET_NAME = "rabang-s3"
AWS_LOCATION = 'ap-northeast-2'
AWS_DEFAULT_ACL = None
if STAGE == 'production':
    MEDIAFILES_LOCATION = 'media'
    STATICFILES_LOCATION = 'static'
    PRIVATEFILE_LOCATION = 'private'
    PUBLICFILES_LOCATION = 'public'
elif STAGE == 'development':
    MEDIAFILES_LOCATION = 'dev/media'
    STATICFILES_LOCATION = 'dev/static'
    PRIVATEFILE_LOCATION = 'dev/private'
    PUBLICFILES_LOCATION = 'dev/public'
elif STAGE == 'local':
    MEDIAFILES_LOCATION = 'local/media'
    STATICFILES_LOCATION = 'local/static'
    PRIVATEFILE_LOCATION = 'local/private'
    PUBLICFILES_LOCATION = 'local/public'


SOLO_CACHE = 'default'
