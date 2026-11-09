from rest_framework import serializers

from .models import PriceCheck


class PriceCheckSerializer(serializers.ModelSerializer):
    source_label = serializers.CharField(source='get_source_display', read_only=True)

    class Meta:
        model = PriceCheck
        fields = ['id', 'checked_at', 'price', 'listing_count', 'source', 'source_label']
