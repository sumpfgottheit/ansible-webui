from django.conf import settings
from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.middleware import RemoteUserMiddleware


class AwRemoteUserBackend(RemoteUserBackend):
    create_unknown_user = False


class AwRemoteUserMiddleware(RemoteUserMiddleware):
    @property
    def header(self) -> str:
        return settings.REMOTE_USER_HEADER
