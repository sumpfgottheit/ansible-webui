import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory


class TestAwRemoteUserBackend:
    def test_create_unknown_user_is_false(self):
        from aw.auth import AwRemoteUserBackend
        assert AwRemoteUserBackend.create_unknown_user is False


class TestAwRemoteUserMiddleware:
    def test_header_reads_from_settings(self, settings):
        from aw.auth import AwRemoteUserMiddleware
        settings.REMOTE_USER_HEADER = 'HTTP_X_CUSTOM_USER'
        middleware = AwRemoteUserMiddleware(get_response=lambda r: None)
        assert middleware.header == 'HTTP_X_CUSTOM_USER'


@pytest.mark.django_db
class TestHeaderLoginView:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_authenticated_user_redirects(self, settings):
        from aw.views.auth import header_login
        settings.REMOTE_USER_HEADER = 'HTTP_REMOTE_USER'

        request = self.factory.get('/a/login/')
        request.user = User.objects.create_user(username='proxy_user')

        response = header_login(request)

        assert response.status_code == 302

    def test_missing_header_returns_403(self, settings):
        from aw.views.auth import header_login
        settings.REMOTE_USER_HEADER = 'HTTP_REMOTE_USER'

        request = self.factory.get('/a/login/')
        request.user = AnonymousUser()

        response = header_login(request)

        assert response.status_code == 403
        assert b'missing' in response.content

    def test_unknown_user_returns_403(self, settings):
        from aw.views.auth import header_login
        settings.REMOTE_USER_HEADER = 'HTTP_REMOTE_USER'

        request = self.factory.get('/a/login/', HTTP_REMOTE_USER='nonexistent_user')
        request.user = AnonymousUser()

        response = header_login(request)

        assert response.status_code == 403
        assert b'does not exist' in response.content
