from django.db.models import Count, Prefetch
from django.http import Http404
from rest_framework import mixins, serializers, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Collection, CollectionItem
from .permissions import MODERATION_ROLES, IsCollectionOwner, IsItemOwner
from .serializers import (
    CollectionDetailSerializer,
    CollectionListSerializer,
    CollectionSerializer,
    ItemDetailSerializer,
    ItemSerializer,
    PublicCollectionDetailSerializer,
    PublicCollectionSerializer,
)

PUBLIC_PAGE_SIZE = 20


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


class PublicPageSerializer(serializers.Serializer):
    page = serializers.IntegerField(min_value=1, default=1)


class PublicCollectionViewSet(viewsets.ReadOnlyModelViewSet):
    """Javne zbirke za vse, tudi goste; brez nakupnih cen in opomb (US-11)."""

    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        # Zbirke blokiranih uporabnikov izginejo z javnega seznama (US-24).
        collections = Collection.objects.filter(is_public=True, user__is_active=True)
        # Moderator in administrator vidita tudi skrite zbirke, da jih lahko razkrijeta (US-12).
        if not (user.is_authenticated and user.role in MODERATION_ROLES):
            collections = collections.filter(is_hidden=False)
        collections = collections.select_related('user').annotate(item_count=Count('items'))
        if self.action == 'retrieve':
            items = CollectionItem.objects.select_related('game', 'platform').order_by('game__title', 'id')
            collections = collections.prefetch_related(Prefetch('items', queryset=items, to_attr='items_by_title'))
        return collections.order_by('-created_at', '-id')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PublicCollectionDetailSerializer
        return PublicCollectionSerializer

    def get_object(self):
        # Zasebna, skrita, blokirana in neobstoječa zbirka so videti enako.
        try:
            return super().get_object()
        except Http404:
            raise NotFound('Collection not found')

    def list(self, request):
        params = PublicPageSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        page = params.validated_data['page']
        collections = self.get_queryset()
        offset = (page - 1) * PUBLIC_PAGE_SIZE
        return Response({
            'count': collections.count(),
            'page': page,
            'results': self.get_serializer(collections[offset:offset + PUBLIC_PAGE_SIZE], many=True).data,
        })
