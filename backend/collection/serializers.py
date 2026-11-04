from django.db import IntegrityError, transaction
from rest_framework import serializers

from .models import Collection

DUPLICATE_NAME = 'You already have a collection with this name'


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

    def create(self, validated_data):
        try:
            with transaction.atomic():
                return Collection.objects.create(user=self.context['request'].user, **validated_data)
        except IntegrityError:
            # Sočasna zahteva z istim imenom je prešla preverjanje, omejitev v bazi pa jo je zavrnila.
            raise serializers.ValidationError({'name': [DUPLICATE_NAME]})
