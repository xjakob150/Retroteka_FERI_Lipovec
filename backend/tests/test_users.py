import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone

from collection.models import Collection
from games.models import Game

User = get_user_model()

pytestmark = pytest.mark.django_db


def make_user(username, role=User.Role.COLLECTOR):
    return User.objects.create_user(
        username=username, email=f'{username}@example.com', password='geslo-za-test', role=role,
    )


def change_url(user):
    return reverse('admin:users_user_change', args=[user.pk])


def post_user(client, user, **changes):
    data = {'role': user.role, 'is_active': 'on' if user.is_active else '', **changes}
    return client.post(change_url(user), data)


@pytest.fixture
def superuser():
    call_command('createsuperuser', interactive=False, username='glavni', email='glavni@example.com', verbosity=0)
    return User.objects.get(username='glavni')


@pytest.fixture
def admin_client(client):
    client.force_login(make_user('ana', User.Role.ADMIN))
    return client


def test_new_user_is_collector_without_admin_access():
    user = make_user('marko')
    assert user.role == User.Role.COLLECTOR
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.parametrize('role, is_staff', [
    (User.Role.COLLECTOR, False),
    (User.Role.MODERATOR, False),
    (User.Role.ADMIN, True),
])
def test_save_syncs_is_staff_with_role(role, is_staff):
    user = make_user('marko', User.Role.ADMIN if role != User.Role.ADMIN else User.Role.COLLECTOR)
    user.role = role
    user.save()
    user.refresh_from_db()
    assert user.is_staff is is_staff


def test_save_with_update_fields_also_syncs_is_staff():
    user = make_user('marko')
    user.role = User.Role.ADMIN
    user.save(update_fields=['role'])
    user.refresh_from_db()
    assert user.is_staff is True


def test_createsuperuser_creates_admin_role(superuser):
    assert superuser.role == User.Role.ADMIN
    assert superuser.is_staff is True
    assert superuser.is_superuser is True


@pytest.mark.parametrize('username, email', [
    ('JAKOB', 'drugi@example.com'),
    ('drugi', 'JAKOB@EXAMPLE.COM'),
])
def test_username_and_email_are_unique_regardless_of_case(username, email):
    User.objects.create_user(username='jakob', email='jakob@example.com')
    with pytest.raises(IntegrityError):
        User.objects.create_user(username=username, email=email)


def test_email_is_required():
    with pytest.raises(ValidationError) as error:
        User(username='marko', password='x').full_clean()
    assert 'email' in error.value.message_dict


def test_administrator_opens_user_admin(admin_client):
    assert admin_client.get(reverse('admin:users_user_changelist')).status_code == 200


@pytest.mark.parametrize('role', [User.Role.COLLECTOR, User.Role.MODERATOR])
def test_other_roles_cannot_open_admin(client, role):
    client.force_login(make_user('marko', role))
    response = client.get(reverse('admin:users_user_changelist'))
    assert response.status_code == 302
    assert '/login/' in response.url


def test_administrator_changes_role_and_blocks_other_user(admin_client):
    marko = make_user('marko')
    assert post_user(admin_client, marko, role=User.Role.MODERATOR, is_active='').status_code == 302
    marko.refresh_from_db()
    assert marko.role == User.Role.MODERATOR
    assert marko.is_active is False


def test_administrator_edit_ignores_other_fields(admin_client):
    marko = make_user('marko')
    password = marko.password
    post_user(admin_client, marko, username='novo', email='novo@example.com', is_superuser='on', password='x')
    marko.refresh_from_db()
    assert marko.username == 'marko'
    assert marko.email == 'marko@example.com'
    assert marko.is_superuser is False
    assert marko.password == password


def test_user_page_has_no_password(admin_client):
    marko = make_user('marko')
    content = admin_client.get(change_url(marko)).content.decode()
    assert 'name="password"' not in content
    assert marko.password not in content
    password_form = admin_client.get(f'{change_url(marko)[:-7]}password/', follow=True).content.decode()
    assert 'name="password1"' not in password_form


def test_administrator_cannot_change_own_role_or_block_self(client):
    ana = make_user('ana', User.Role.ADMIN)
    client.force_login(ana)
    post_user(client, ana, role=User.Role.COLLECTOR, is_active='')
    ana.refresh_from_db()
    assert ana.role == User.Role.ADMIN
    assert ana.is_active is True


def test_administrator_cannot_change_superuser(admin_client, superuser):
    post_user(admin_client, superuser, role=User.Role.COLLECTOR, is_active='')
    superuser.refresh_from_db()
    assert superuser.role == User.Role.ADMIN
    assert superuser.is_active is True


def test_users_cannot_be_added_or_deleted_in_admin(admin_client):
    marko = make_user('marko')
    assert admin_client.get(reverse('admin:users_user_add')).status_code == 403
    assert admin_client.post(reverse('admin:users_user_delete', args=[marko.pk]), {'post': 'yes'}).status_code == 403
    assert User.objects.filter(pk=marko.pk).exists()


def test_administrator_cannot_open_collections_in_admin(admin_client):
    collection = Collection.objects.create(user=make_user('marko'), name='PS2')
    assert admin_client.get(reverse('admin:collection_collection_changelist')).status_code == 403
    assert admin_client.get(reverse('admin:collection_collection_change', args=[collection.pk])).status_code == 403


def test_superuser_only_views_collections_and_games(client, superuser):
    client.force_login(superuser)
    collection = Collection.objects.create(user=make_user('marko'), name='PS2')
    game = Game.objects.create(igdb_id=1, title='Gran Turismo 4', synced_at=timezone.now())
    url = reverse('admin:collection_collection_change', args=[collection.pk])
    assert client.get(url).status_code == 200
    assert client.get(reverse('admin:games_game_change', args=[game.pk])).status_code == 200
    assert client.post(url, {'name': 'Novo'}).status_code == 403
    assert client.post(reverse('admin:collection_collection_delete', args=[collection.pk]), {'post': 'yes'}).status_code == 403
    collection.refresh_from_db()
    assert collection.name == 'PS2'
