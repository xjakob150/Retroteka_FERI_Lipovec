from django.db import IntegrityError, transaction
from rest_framework import serializers

from games.models import Game, Platform

from .models import Collection, CollectionItem

DUPLICATE_NAME = 'You already have a collection with this name'
HIDDEN_CANNOT_BE_PUBLIC = 'A collection hidden by a moderator cannot be made public.'


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
