from django.db.models import Count, Prefetch
from rest_framework import mixins, viewsets

from .models import Collection, CollectionItem
from .permissions import IsCollectionOwner
from .serializers import CollectionDetailSerializer, CollectionListSerializer, CollectionSerializer


class CollectionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsCollectionOwner]

    def get_queryset(self):
        # Vsa dejanja vidijo samo zbirke prijavljenega uporabnika, zato je tuja zbirka 404.
        collections = Collection.objects.filter(user=self.request.user)
        if self.action in ('list', 'retrieve'):
            items = CollectionItem.objects.select_related('game', 'platform').order_by('game__title', 'id')
            collections = collections.annotate(item_count=Count('items')).prefetch_related(
                Prefetch('items', queryset=items, to_attr='items_by_title'),
            )
        return collections.order_by('created_at', 'id')

    def get_serializer_class(self):
        if self.action == 'list':
            return CollectionListSerializer
        if self.action == 'retrieve':
            return CollectionDetailSerializer
        return CollectionSerializer
