import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from collection.models import Collection

User = get_user_model()

pytestmark = pytest.mark.django_db

URL = '/api/collections/'


def make_user(username='marko', role=User.Role.COLLECTOR):
    return User.objects.create_user(username, f'{username}@example.com', 'dolgo-geslo-1', role=role)


def client_for(user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(user).access_token}')
    return client


def create(owner, **data):
    return client_for(owner).post(URL, data, format='json')


def test_url_name():
    assert reverse('collection-list') == URL


def test_collector_creates_private_collection():
    user = make_user()
    response = create(user, name='PS2', description='Moje igre')
    assert response.status_code == 201
    collection = Collection.objects.get()
    assert collection.user == user
    assert response.data == {
        'id': collection.id,
        'name': 'PS2',
        'description': 'Moje igre',
        'is_public': False,
        'is_hidden': False,
        'created_at': response.data['created_at'],
    }


def test_collection_is_public_when_selected():
    response = create(make_user(), name='For sale', is_public=True)
    assert response.status_code == 201
    assert response.data['is_public'] is True


def test_owner_comes_from_login_not_request():
    user, other = make_user(), make_user('ana')
    create(user, name='PS2', user=other.id, is_hidden=True)
    collection = Collection.objects.get()
    assert (collection.user, collection.is_hidden) == (user, False)


def test_duplicate_name_is_rejected_with_message():
    user = make_user()
    create(user, name='PS2')
    response = create(user, name='ps2')
    assert response.status_code == 400
    assert response.data == {'name': ['You already have a collection with this name']}


def test_invalid_name_is_rejected():
    response = create(make_user(), name='')
    assert response.status_code == 400
    assert 'name' in response.data
    assert not Collection.objects.exists()


@pytest.mark.parametrize('role', [User.Role.MODERATOR, User.Role.ADMIN])
def test_moderator_and_admin_can_create_own_collection(role):
    assert create(make_user(role=role), name='PS2').status_code == 201


def test_guest_cannot_create_collection():
    response = APIClient().post(URL, {'name': 'PS2'}, format='json')
    assert response.status_code == 401
    assert not Collection.objects.exists()


def test_blocked_user_cannot_create_collection():
    user = make_user()
    client = client_for(user)
    user.is_active = False
    user.save()
    assert client.post(URL, {'name': 'PS2'}, format='json').status_code == 401


def test_listing_is_not_available_yet():
    assert client_for(make_user()).get(URL).status_code == 405
