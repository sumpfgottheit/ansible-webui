from os import environ
from sys import exit as sys_exit

from requests import Session

BASE_URL = 'http://127.0.0.1:8000'
ADMIN_USER = environ['AW_ADMIN']

_meta_key = environ.get('AW_REMOTE_USER_HEADER', 'HTTP_REMOTE_USER')
# Convert Django META key (HTTP_REMOTE_USER) to HTTP header name (Remote-User)
if _meta_key.startswith('HTTP_'):
    HTTP_HEADER = _meta_key[5:].replace('_', '-').title()
else:
    HTTP_HEADER = _meta_key.replace('_', '-').title()


def _session_with_user(username: str) -> Session:
    s = Session()
    s.headers[HTTP_HEADER] = username
    return s


def test_missing_header():
    print('TESTING: missing header -> 403')
    resp = Session().get(f'{BASE_URL}/a/login/', allow_redirects=False)
    assert resp.status_code == 403, f'Expected 403, got {resp.status_code}'
    assert b'missing' in resp.content, f'Expected "missing" in body, got: {resp.content}'
    print('  OK')


def test_unknown_user():
    print('TESTING: unknown user in header -> 403')
    s = _session_with_user('__no_such_user__')
    resp = s.get(f'{BASE_URL}/a/login/', allow_redirects=False)
    assert resp.status_code == 403, f'Expected 403, got {resp.status_code}'
    assert b'does not exist' in resp.content, f'Expected "does not exist" in body, got: {resp.content}'
    print('  OK')


def test_known_user_redirects():
    print(f'TESTING: known user "{ADMIN_USER}" in header -> redirect to /ui')
    s = _session_with_user(ADMIN_USER)
    resp = s.get(f'{BASE_URL}/a/login/', allow_redirects=False)
    assert resp.status_code == 302, f'Expected 302, got {resp.status_code}'
    location = resp.headers.get('Location', '')
    assert '/ui' in location, f'Expected redirect to /ui, got Location: {location}'
    print('  OK')


def test_frontend_info_flags():
    print(f'TESTING: frontend/info with valid header -> can_logout=false, can_change_password=false')
    s = _session_with_user(ADMIN_USER)
    resp = s.get(f'{BASE_URL}/api/frontend/info', allow_redirects=False)
    assert resp.status_code == 200, f'Expected 200, got {resp.status_code}'
    data = resp.json()
    assert data.get('authenticated') is True, f'Expected authenticated=true, got: {data}'
    assert data.get('can_logout') is False, f'Expected can_logout=false, got: {data}'
    assert data.get('can_change_password') is False, f'Expected can_change_password=false, got: {data}'
    print('  OK')


def test_frontend_info_unauthenticated():
    print('TESTING: frontend/info without header -> authenticated=false')
    resp = Session().get(f'{BASE_URL}/api/frontend/info', allow_redirects=False)
    assert resp.status_code == 200, f'Expected 200, got {resp.status_code}'
    data = resp.json()
    assert data.get('authenticated') is False, f'Expected authenticated=false, got: {data}'
    print('  OK')


def main():
    failed = False
    tests = [
        test_missing_header,
        test_unknown_user,
        test_known_user_redirects,
        test_frontend_info_flags,
        test_frontend_info_unauthenticated,
    ]
    for test in tests:
        try:
            test()
        except AssertionError as err:
            print(f'  FAIL: {err}')
            failed = True

    if failed:
        sys_exit(1)


if __name__ == '__main__':
    main()
