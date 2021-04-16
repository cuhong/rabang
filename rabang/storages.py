import os

from django.conf import settings
from django.core.files.storage import Storage, default_storage, DefaultStorage
from storages.backends.s3boto3 import S3Boto3Storage

if settings.STAGE == 'local':
    class BaseStorage(DefaultStorage):
        pass
        # def url(self, name):
        #     return os.path.join(settings.MEDIA_URL, name)
        # # def url(self, name):
        # #     meta_backend_obj = self.meta_backend.get(path=name)
        # #     return self.get_original_storage(meta_backend_obj=meta_backend_obj).url(
        # #         meta_backend_obj['original_storage_path']
        # #     )


    class MediaStorage(BaseStorage):
        pass
        # def url(self, name):
        #     return os.path.join(settings.MEDIA_URL, name)


    class StaticStorage(BaseStorage):
        pass
        # def url(self, name):
        #     return os.path.join(settings.STATIC_URL, name)


    class PrivateFileStorage(BaseStorage):
        pass
        # def url(self, name):
        #     return os.path.join(settings.MEDIA_URL, name)

    class PublicFileStorage(BaseStorage):
        pass
        # def url(self, name):
        #     return os.path.join(settings.MEDIA_URL, name)
else:
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
