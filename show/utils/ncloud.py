import base64
import hashlib
import hmac
import time

from django.conf import settings


class NcloudError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def get_timestamp():
    timestamp = str(int(time.time() * 1000))
    return timestamp


def get_ncloud_live_station_signature(method, uri):
    if method not in ["GET", "POST"]:
        raise NcloudError(f"{method}는 허용되지 않습니다.")
    timestamp = get_timestamp()
    access_key = settings.NCLOUD_ACCESS
    _secret_key = settings.NCLOUD_SECRET
    secret_key = bytes(_secret_key, 'UTF-8')
    message = method + " " + uri + "\n" + timestamp + "\n" + access_key
    message = bytes(message, 'UTF-8')
    signing_key = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
    return timestamp, signing_key


