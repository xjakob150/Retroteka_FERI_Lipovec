from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.utils import aware_utcnow

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user('marko', 'marko@example.com', 'dolgo-geslo-1')


def authenticate(token):
    request = APIRequestFactory().get('/', HTTP_AUTHORIZATION=f'Bearer {token}')
    return JWTAuthentication().authenticate(request)


def lifetime(token):
    return timedelta(seconds=token['exp'] - token['iat'])


def test_token_lifetimes_match_adr_0009(user):
    refresh = RefreshToken.for_user(user)
    assert lifetime(refresh) == timedelta(days=7)
    assert lifetime(refresh.access_token) == timedelta(minutes=15)


def test_access_token_loads_current_user_from_database(user):
    token = RefreshToken.for_user(user).access_token
    user.role = User.Role.MODERATOR
    user.save()
    authenticated_user, _ = authenticate(token)
    assert authenticated_user == user
    assert authenticated_user.role == User.Role.MODERATOR


def test_blocked_user_with_valid_access_token_is_rejected(user):
    token = RefreshToken.for_user(user).access_token
    user.is_active = False
    user.save()
    with pytest.raises(AuthenticationFailed):
        authenticate(token)


def login(username='marko', password='dolgo-geslo-1'):
    return APIClient().post(reverse('login'), {'username': username, 'password': password}, format='json')


@pytest.mark.parametrize('username', ['marko', 'MARKO', 'Marko'])
def test_login_returns_tokens_and_user_regardless_of_username_case(user, username):
    response = login(username)
    assert response.status_code == 200
    assert set(response.data) == {'access', 'refresh', 'user'}
    assert response.data['user']['username'] == 'marko'
    assert authenticate(response.data['access'])[0] == user


@pytest.mark.parametrize('username, password', [
    ('marko', 'napacno-geslo'),
    ('neznan', 'dolgo-geslo-1'),
])
def test_wrong_details_give_one_message(user, username, password):
    response = login(username, password)
    assert response.status_code == 401
    assert response.data == {'detail': 'Invalid username or password'}


def test_blocked_user_cannot_log_in(user):
    user.is_active = False
    user.save()
    response = login()
    assert response.status_code == 401
    assert response.data == {'detail': 'Invalid username or password'}


@pytest.mark.parametrize('missing', ['username', 'password'])
def test_login_requires_both_fields(missing):
    data = {'username': 'marko', 'password': 'dolgo-geslo-1'}
    del data[missing]
    response = APIClient().post(reverse('login'), data, format='json')
    assert response.status_code == 400
    assert missing in response.data


def test_login_records_last_login(user):
    assert user.last_login is None
    login()
    user.refresh_from_db()
    assert user.last_login is not None


def refresh(token):
    return APIClient().post(reverse('refresh'), {'refresh': str(token)}, format='json')


def test_refresh_returns_new_access_token_for_same_user_without_rotation(user):
    response = refresh(RefreshToken.for_user(user))
    assert response.status_code == 200
    assert set(response.data) == {'access'}
    assert str(AccessToken(response.data['access'])['user_id']) == str(user.id)


def test_refresh_token_older_than_7_days_is_rejected(user):
    token = RefreshToken.for_user(user)
    token.set_exp(from_time=aware_utcnow() - timedelta(days=7, seconds=1))
    assert refresh(token).status_code == 401


def test_refresh_does_not_extend_the_7_days(user):
    token = RefreshToken.for_user(user)
    expires_at = token['exp']
    refresh(token)
    assert RefreshToken(str(token))['exp'] == expires_at


def test_blocked_user_cannot_refresh(user):
    token = RefreshToken.for_user(user)
    user.is_active = False
    user.save()
    assert refresh(token).status_code == 401


def test_deleted_user_cannot_refresh(user):
    token = RefreshToken.for_user(user)
    user.delete()
    assert refresh(token).status_code == 401


def test_malformed_refresh_token_is_rejected():
    assert refresh('ni-zeton').status_code == 401


def test_access_token_cannot_be_used_to_refresh(user):
    assert refresh(RefreshToken.for_user(user).access_token).status_code == 401


def test_refresh_requires_token():
    assert APIClient().post(reverse('refresh'), {}, format='json').status_code == 400


def logout(token):
    return APIClient().post(reverse('logout'), {'refresh': str(token)}, format='json')


def test_logout_without_access_token_revokes_refresh_token(user):
    token = RefreshToken.for_user(user)
    assert logout(token).status_code == 204
    assert refresh(token).status_code == 401


def test_logout_revokes_only_this_device(user):
    this_device, other_device = RefreshToken.for_user(user), RefreshToken.for_user(user)
    logout(this_device)
    assert refresh(other_device).status_code == 200


def test_repeated_logout_succeeds(user):
    token = RefreshToken.for_user(user)
    logout(token)
    assert logout(token).status_code == 204


def test_logout_with_expired_token_succeeds(user):
    token = RefreshToken.for_user(user)
    token.set_exp(from_time=aware_utcnow() - timedelta(days=8))
    assert logout(token).status_code == 204


def test_logout_with_malformed_token_succeeds():
    assert logout('ni-zeton').status_code == 204


def test_logout_requires_token():
    assert APIClient().post(reverse('logout'), {}, format='json').status_code == 400


def test_tokens_from_login_can_be_revoked(user):
    token = login().data['refresh']
    logout(token)
    assert refresh(token).status_code == 401


def test_issued_tokens_are_not_exposed_in_admin(client):
    superuser = User.objects.create_superuser('glavni', 'glavni@example.com', 'dolgo-geslo-1')
    client.force_login(superuser)
    assert client.get('/admin/token_blacklist/outstandingtoken/').status_code != 200
    assert 'token_blacklist' not in client.get(reverse('admin:index')).content.decode()


def me(token=None):
    client = APIClient()
    if token:
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client.get(reverse('me'))


def test_me_returns_current_user(user):
    response = me(RefreshToken.for_user(user).access_token)
    assert response.status_code == 200
    assert response.data == {'id': user.id, 'username': 'marko', 'email': 'marko@example.com', 'role': 'collector'}


def test_me_shows_new_role_with_old_token(user):
    token = RefreshToken.for_user(user).access_token
    user.role = User.Role.MODERATOR
    user.save()
    assert me(token).data['role'] == 'moderator'


def test_me_rejects_blocked_user_with_valid_token(user):
    token = RefreshToken.for_user(user).access_token
    user.is_active = False
    user.save()
    assert me(token).status_code == 401


def test_me_requires_token():
    assert me().status_code == 401


def test_me_rejects_refresh_token_and_malformed_token(user):
    assert me(RefreshToken.for_user(user)).status_code == 401
    assert me('ni-zeton').status_code == 401


def test_me_rejects_expired_access_token(user):
    token = RefreshToken.for_user(user).access_token
    token.set_exp(from_time=aware_utcnow() - timedelta(minutes=16))
    assert me(token).status_code == 401
