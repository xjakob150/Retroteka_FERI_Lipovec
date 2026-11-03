from rest_framework import serializers

from .models import Game, GameRelease

TOO_SHORT = 'Type at least 3 characters'


class SearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(
        min_length=3,
        max_length=100,
        error_messages={'min_length': TOO_SHORT, 'blank': TOO_SHORT, 'required': TOO_SHORT},
    )
    page = serializers.IntegerField(min_value=1, default=1)


class ReleaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='platform.id')
    name = serializers.CharField(source='platform.name')
    abbreviation = serializers.CharField(source='platform.abbreviation')

    class Meta:
        model = GameRelease
        fields = ['id', 'name', 'abbreviation', 'release_year']


class SearchResultSerializer(serializers.ModelSerializer):
    platforms = ReleaseSerializer(source='releases', many=True)

    class Meta:
        model = Game
        fields = ['id', 'title', 'cover_url', 'release_year', 'genres', 'platforms']
