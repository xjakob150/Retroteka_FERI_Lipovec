from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from users.serializers import RegisterSerializer

User = get_user_model()

pytestmark = pytest.mark.django_db

PASSWORD = 'dolgo-geslo-1'


def register(**changes):
    data = {
        'username': 'marko',
        'email': 'marko@example.com',
        'password': PASSWORD,
        'password_confirm': PASSWORD,
        **changes,
    }
    return APIClient().post(reverse('register'), data, format='json')


def assert_rejected(response, field, message=None):
    assert response.status_code == 400
    assert field in response.data
    if message:
        assert response.data[field] == [message]


def test_register_creates_collector_and_returns_tokens_and_user():
    response = register()
    assert response.status_code == 201
    user = User.objects.get(username='marko')
    assert user.role == User.Role.COLLECTOR
    assert response.data['user'] == {
        'id': user.id, 'username': 'marko', 'email': 'marko@example.com', 'role': 'collector',
    }
    assert set(response.data) == {'access', 'refresh', 'user'}


def test_tokens_belong_to_new_user_and_hold_no_role():
    response = register()
    user = User.objects.get(username='marko')
    access = AccessToken(response.data['access'])
    assert str(access['user_id']) == str(user.id)
    assert 'role' not in access.payload
    assert str(RefreshToken(response.data['refresh'])['user_id']) == str(user.id)


def test_password_is_hashed_and_never_returned():
    response = register()
    user = User.objects.get(username='marko')
    assert user.check_password(PASSWORD)
    assert user.password != PASSWORD
    assert PASSWORD not in response.content.decode()
    assert user.password not in response.content.decode()


@pytest.mark.parametrize('extra', [
    {'role': 'admin'},
    {'is_staff': True},
    {'is_superuser': True},
])
def test_client_cannot_choose_privileges(extra):
    assert register(**extra).status_code == 201
    user = User.objects.get(username='marko')
    assert user.role == User.Role.COLLECTOR
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.parametrize('field', ['username', 'email', 'password', 'password_confirm'])
def test_required_fields(field):
    response = APIClient().post(reverse('register'), {
        name: value for name, value in {
            'username': 'marko',
            'email': 'marko@example.com',
            'password': PASSWORD,
            'password_confirm': PASSWORD,
        }.items() if name != field
    }, format='json')
    assert_rejected(response, field)
    assert not User.objects.exists()


def test_passwords_must_match():
    assert_rejected(register(password_confirm='drugo-geslo-1'), 'password_confirm', 'Passwords do not match')
    assert not User.objects.exists()


@pytest.mark.parametrize('username', ['marko', 'MARKO', 'Marko'])
def test_username_taken_regardless_of_case(username):
    register()
    assert_rejected(register(username=username, email='drugi@example.com'), 'username', 'Username is already taken')


@pytest.mark.parametrize('email', ['marko@example.com', 'MARKO@EXAMPLE.COM'])
def test_email_registered_regardless_of_case(email):
    register()
    assert_rejected(register(username='drugi', email=email), 'email', 'Email is already registered')


@pytest.mark.parametrize('field, changes, message', [
    ('username', {'email': 'drugi@example.com'}, 'Username is already taken'),
    ('email', {'username': 'drugi'}, 'Email is already registered'),
])
def test_concurrent_duplicate_rejected_by_database_returns_same_message(field, changes, message):
    register()
    with patch.object(RegisterSerializer, f'validate_{field}', lambda self, value: value):
        assert_rejected(register(**changes), field, message)


@pytest.mark.parametrize('password', ['kratko1', '12345678'])
def test_weak_password_is_rejected_with_reason(password):
    response = register(password=password, password_confirm=password)
    assert_rejected(response, 'password')
    assert response.data['password'][0]
    assert not User.objects.exists()


def test_common_password_is_accepted():
    assert register(password='password', password_confirm='password').status_code == 201


def test_invalid_email_is_rejected():
    assert_rejected(register(email='ni-naslov'), 'email')
