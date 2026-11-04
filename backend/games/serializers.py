from rest_framework import serializers

from .models import Game, GameRelease, Platform

TOO_SHORT = 'Type at least 3 characters'
UNSUPPORTED_PLATFORM = 'Select a supported platform.'


class SearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(
        min_length=3,
        max_length=100,
        error_messages={'min_length': TOO_SHORT, 'blank': TOO_SHORT, 'required': TOO_SHORT},
    )
    page = serializers.IntegerField(min_value=1, default=1)
    platform = serializers.PrimaryKeyRelatedField(
        queryset=Platform.objects.filter(is_supported=True),
        required=False,
        error_messages={'does_not_exist': UNSUPPORTED_PLATFORM, 'incorrect_type': UNSUPPORTED_PLATFORM},
    )


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ['id', 'name', 'abbreviation', 'manufacturer', 'generation']


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
