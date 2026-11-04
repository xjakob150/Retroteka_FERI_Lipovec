from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from collection.models import Collection
from collection.serializers import CollectionSerializer

pytestmark = pytest.mark.django_db


def make_user(username='marko'):
    return get_user_model().objects.create_user(username, f'{username}@example.com', 'dolgo-geslo-1')


def serializer(owner, **data):
    return CollectionSerializer(data=data, context={'request': SimpleNamespace(user=owner)})


def errors(owner, **data):
    form = serializer(owner, **data)
    assert not form.is_valid()
    return form.errors


def test_valid_collection_is_created_for_user_and_private_by_default():
    user = make_user()
    form = serializer(user, name='PS2', description='Moje igre za PS2')
    assert form.is_valid(), form.errors
    collection = form.save()
    assert (collection.user, collection.name, collection.is_public, collection.is_hidden) == (user, 'PS2', False, False)


@pytest.mark.parametrize('name', ['x', 'x' * 100])
def test_name_from_1_to_100_characters_is_valid(name):
    assert serializer(make_user(), name=name).is_valid()


@pytest.mark.parametrize('data, field', [
    ({}, 'name'),
    ({'name': ''}, 'name'),
    ({'name': '   '}, 'name'),
    ({'name': 'x' * 101}, 'name'),
    ({'name': 'PS2', 'description': 'x' * 501}, 'description'),
])
def test_invalid_name_or_description_is_rejected(data, field):
    assert field in errors(make_user(), **data)


def test_description_up_to_500_characters_and_empty_description_are_valid():
    user = make_user()
    assert serializer(user, name='A', description='x' * 500).is_valid()
    assert serializer(user, name='B', description='').is_valid()


def test_name_is_trimmed():
    form = serializer(make_user(), name='  PS2  ')
    assert form.is_valid()
    assert form.validated_data['name'] == 'PS2'


@pytest.mark.parametrize('name', ['PS2', 'ps2', ' Ps2 '])
def test_duplicate_name_regardless_of_case_is_rejected(name):
    user = make_user()
    Collection.objects.create(user=user, name='PS2')
    assert errors(user, name=name) == {'name': ['You already have a collection with this name']}


def test_other_users_can_use_the_same_name():
    Collection.objects.create(user=make_user('ana'), name='PS2')
    assert serializer(make_user(), name='PS2').is_valid()


def test_concurrent_duplicate_rejected_by_database_gives_same_message():
    user = make_user()
    Collection.objects.create(user=user, name='PS2')
    form = serializer(user, name='ps2')
    with patch.object(CollectionSerializer, 'validate_name', lambda self, value: value):
        assert form.is_valid()
        with pytest.raises(Exception) as error:
            form.save()
    assert error.value.detail == {'name': ['You already have a collection with this name']}


def test_read_only_fields_are_ignored():
    user = make_user()
    moderator = make_user('moderator')
    form = serializer(user, name='PS2', is_hidden=True, id=999, created_at='2000-01-01T00:00:00Z', user=moderator.id)
    assert form.is_valid()
    collection = form.save()
    assert collection.is_hidden is False
    assert collection.id != 999
    assert collection.user == user
