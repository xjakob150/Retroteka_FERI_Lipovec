from django.db import IntegrityError, transaction
from rest_framework import serializers

from games.models import Game, GameRelease, Platform
from pricing.services import clear_price_checks

from .models import Collection, CollectionItem

DUPLICATE_NAME = 'You already have a collection with this name'
HIDDEN_CANNOT_BE_PUBLIC = 'A collection hidden by a moderator cannot be made public.'
NOT_OWN_COLLECTION = 'Select one of your collections.'
NOT_RELEASED_ON_PLATFORM = 'Select a platform the game was released on.'
UNKNOWN_GAME = 'Select a game from the search results.'
# Sprememba katerega koli od teh polj naredi iz izvoda drugo izdajo, zato stare cene ne veljajo več (ADR-0013).
PRICE_FIELDS = ('platform', 'region', 'condition')


def required(field):
    message = f'{field} is required'
    return {'required': message, 'null': message, 'blank': message}


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'name', 'description', 'is_public', 'is_hidden', 'created_at']
        read_only_fields = ['id', 'is_hidden', 'created_at']

    def validate_name(self, value):
        collections = Collection.objects.filter(user=self.context['request'].user, name__iexact=value)
        if self.instance is not None:
            collections = collections.exclude(pk=self.instance.pk)
        if collections.exists():
            raise serializers.ValidationError(DUPLICATE_NAME)
        return value

    def validate_is_public(self, value):
        # Skrito zbirko lahko znova objavi samo moderator (US-12); ista vrednost ali umik v zasebno je dovoljen.
        collection = self.instance
        if collection is not None and collection.is_hidden and value and not collection.is_public:
            raise serializers.ValidationError(HIDDEN_CANNOT_BE_PUBLIC)
        return value

    def create(self, validated_data):
        try:
            with transaction.atomic():
                return Collection.objects.create(user=self.context['request'].user, **validated_data)
        except IntegrityError:
            # Sočasna zahteva z istim imenom je prešla preverjanje, omejitev v bazi pa jo je zavrnila.
            raise serializers.ValidationError({'name': [DUPLICATE_NAME]})

    def update(self, instance, validated_data):
        try:
            with transaction.atomic():
                return super().update(instance, validated_data)
        except IntegrityError:
            raise serializers.ValidationError({'name': [DUPLICATE_NAME]})


class CollectionListSerializer(CollectionSerializer):
    item_count = serializers.IntegerField(read_only=True)
    covers = serializers.SerializerMethodField()

    class Meta(CollectionSerializer.Meta):
        fields = CollectionSerializer.Meta.fields + ['item_count', 'covers']

    def get_covers(self, collection):
        # Naslovnice prvih petih izvodov po naslovu; ista igra se lahko ponovi, ker je vsak izvod svoj zapis.
        return [item.game.cover_url for item in collection.items_by_title[:5]]


class ItemGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'title', 'cover_url']


class ItemPlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ['id', 'name', 'abbreviation']


class CollectionItemSerializer(serializers.ModelSerializer):
    game = ItemGameSerializer(read_only=True)
    platform = ItemPlatformSerializer(read_only=True)
    region_label = serializers.CharField(source='get_region_display', read_only=True)
    condition_label = serializers.CharField(source='get_condition_display', read_only=True)

    class Meta:
        model = CollectionItem
        fields = [
            'id', 'game', 'platform', 'region', 'region_label', 'condition', 'condition_label', 'purchase_price',
        ]


class CollectionDetailSerializer(CollectionSerializer):
    item_count = serializers.IntegerField(read_only=True)
    items = CollectionItemSerializer(source='items_by_title', many=True, read_only=True)

    class Meta(CollectionSerializer.Meta):
        fields = CollectionSerializer.Meta.fields + ['item_count', 'items']


class ItemSerializer(serializers.ModelSerializer):
    """Zapis izvoda; odgovor ima igro in platformo v enaki obliki kot seznam izvodov v zbirki."""

    class Meta:
        model = CollectionItem
        fields = [
            'id', 'collection', 'game', 'platform', 'region', 'condition', 'purchase_price', 'notes',
            'estimated_price', 'price_checked_at', 'created_at',
        ]
        read_only_fields = ['id', 'estimated_price', 'price_checked_at', 'created_at']
        extra_kwargs = {
            'collection': {'error_messages': {
                **required('Collection'), 'does_not_exist': NOT_OWN_COLLECTION, 'incorrect_type': NOT_OWN_COLLECTION,
            }},
            'game': {'error_messages': {
                **required('Game'), 'does_not_exist': UNKNOWN_GAME, 'incorrect_type': UNKNOWN_GAME,
            }},
            'platform': {'error_messages': {
                **required('Platform'),
                'does_not_exist': NOT_RELEASED_ON_PLATFORM,
                'incorrect_type': NOT_RELEASED_ON_PLATFORM,
            }},
            # Prazen niz pride do validate_<polje>, ki vrne sporočilo "... is required" namesto "not a valid choice".
            'region': {'allow_blank': True, 'error_messages': required('Region')},
            'condition': {'allow_blank': True, 'error_messages': required('Condition')},
            'notes': {'max_length': 1000},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Igre obstoječega izvoda ni mogoče zamenjati (US-09); napačna igra se popravi z novim izvodom.
        if self.instance is not None:
            self.fields['game'].read_only = True

    def validate_collection(self, collection):
        # Tuja zbirka dobi isto sporočilo kot neobstoječa, da se ne izve, da obstaja.
        if collection.user_id != self.context['request'].user.id:
            raise serializers.ValidationError(NOT_OWN_COLLECTION)
        return collection

    def validate_region(self, value):
        if not value:
            raise serializers.ValidationError(required('Region')['required'])
        return value

    def validate_condition(self, value):
        if not value:
            raise serializers.ValidationError(required('Condition')['required'])
        return value

    def validate(self, attrs):
        game = attrs.get('game', getattr(self.instance, 'game', None))
        platform = attrs.get('platform', getattr(self.instance, 'platform', None))
        if not GameRelease.objects.filter(game=game, platform=platform, platform__is_supported=True).exists():
            raise serializers.ValidationError({'platform': [NOT_RELEASED_ON_PLATFORM]})
        return attrs

    def update(self, item, validated_data):
        changes_edition = any(
            field in validated_data and validated_data[field] != getattr(item, field) for field in PRICE_FIELDS
        )
        with transaction.atomic():
            item = super().update(item, validated_data)
            if changes_edition:
                clear_price_checks(item)
        return item

    def to_representation(self, item):
        data = CollectionItemSerializer(item).data
        data.update({
            'collection': item.collection_id,
            'notes': item.notes,
            'estimated_price': None if item.estimated_price is None else str(item.estimated_price),
            'price_checked_at': item.price_checked_at,
            'created_at': item.created_at,
        })
        return data


class ItemDetailSerializer(ItemSerializer):
    """Izvod z vsem, kar prikaže stran izvoda: opis igre in platforme, na katerih je izšla."""

    def to_representation(self, item):
        data = super().to_representation(item)
        game = item.game
        releases = game.releases.filter(platform__is_supported=True).select_related('platform').order_by(
            'platform__generation', 'platform__name',
        )
        data['game'].update({
            'release_year': game.release_year,
            'genres': game.genres,
            'summary': game.summary,
            'platforms': [
                {
                    'id': release.platform.id,
                    'name': release.platform.name,
                    'abbreviation': release.platform.abbreviation,
                    'release_year': release.release_year,
                }
                for release in releases
            ],
        })
        return data


class PublicItemSerializer(serializers.ModelSerializer):
    """Izvod v javni zbirki: brez nakupne cene in opomb (US-11)."""

    game = ItemGameSerializer(read_only=True)
    platform = ItemPlatformSerializer(read_only=True)
    region_label = serializers.CharField(source='get_region_display', read_only=True)
    condition_label = serializers.CharField(source='get_condition_display', read_only=True)

    class Meta:
        model = CollectionItem
        fields = ['id', 'game', 'platform', 'region', 'region_label', 'condition', 'condition_label']
        read_only_fields = fields


class PublicCollectionSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='user.username', read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'name', 'description', 'owner', 'item_count', 'is_hidden', 'created_at']
        read_only_fields = fields


class PublicCollectionDetailSerializer(PublicCollectionSerializer):
    items = PublicItemSerializer(source='items_by_title', many=True, read_only=True)

    class Meta(PublicCollectionSerializer.Meta):
        fields = PublicCollectionSerializer.Meta.fields + ['items']
        read_only_fields = fields
