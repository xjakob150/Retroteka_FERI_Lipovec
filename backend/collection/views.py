from django.db.models import Count, Prefetch
from rest_framework import mixins, viewsets

from .models import Collection, CollectionItem
from .permissions import IsCollectionOwner, IsItemOwner
from .serializers import (
    CollectionDetailSerializer,
    CollectionListSerializer,
    CollectionSerializer,
    ItemDetailSerializer,
    ItemSerializer,
)


class CollectionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsCollectionOwner]
    # Urejanje je samo delno (PATCH); PUT bi zahteval vsa polja.
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

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


class ItemViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsItemOwner]
    # Urejanje in premik sta delna (PATCH); PUT bi zahteval vsa polja.
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        # Samo izvodi v zbirkah prijavljenega uporabnika, zato je tuj izvod 404.
        return CollectionItem.objects.filter(collection__user=self.request.user).select_related('game', 'platform')

    def get_serializer_class(self):
        if self.action in ('retrieve', 'partial_update'):
            return ItemDetailSerializer
        return ItemSerializer
