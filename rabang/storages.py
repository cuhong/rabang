from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    querystring_auth = False
    default_acl = 'public-read'
    location = settings.MEDIAFILES_LOCATION


class StaticStorage(S3Boto3Storage):
    querystring_auth = False
    default_acl = 'public-read'
    location = settings.STATICFILES_LOCATION


class PrivateFileStorage(S3Boto3Storage):
    querystring_expire = 60
    querystring_auth = True
    default_acl = 'private'
    location = settings.PRIVATEFILE_LOCATION


class PublicFileStorage(S3Boto3Storage):
    querystring_auth = False
    default_acl = 'public-read'
    location = settings.PUBLICFILES_LOCATION

