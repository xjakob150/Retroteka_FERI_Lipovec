from django.db.models import Count, Prefetch, Q
from django.http import Http404
from django.utils import timezone
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from pricing.services import can_refresh_price, fetch_price

from .models import Collection, CollectionItem
from .permissions import MODERATION_ROLES, CanHideCollection, CanUnhideCollection, IsCollectionOwner, IsItemOwner
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
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
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
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return CollectionItem.objects.filter(collection__user=self.request.user).select_related('game', 'platform')

    def get_serializer_class(self):
        if self.action in ('retrieve', 'partial_update', 'refresh_price'):
            return ItemDetailSerializer
        return ItemSerializer

    def perform_create(self, serializer):
        fetch_price(serializer.save())

    def perform_update(self, serializer):
        item = serializer.save()
        if serializer.changed_edition:
            fetch_price(item)

    @action(detail=True, methods=['post'], url_path='refresh-price')
    def refresh_price(self, request, pk=None):
        item = self.get_object()
        if not can_refresh_price(item):
            return Response({'detail': 'Available again tomorrow'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        if fetch_price(item) is None:
            return Response(
                {'detail': 'The price cannot be refreshed right now'}, status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(self.get_serializer(item).data)


class PublicPageSerializer(serializers.Serializer):
    page = serializers.IntegerField(min_value=1, default=1)


class PublicCollectionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        collections = Collection.objects.filter(user__is_active=True)
        if user.is_authenticated and user.role in MODERATION_ROLES:
            collections = collections.filter(Q(is_public=True) | Q(is_hidden=True))
        else:
            collections = collections.filter(is_public=True, is_hidden=False)
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

    @action(detail=True, methods=['post'], permission_classes=[CanHideCollection])
    def hide(self, request, pk=None):
        collection = self.get_object()
        if collection.is_hidden:
            raise ValidationError({'detail': 'This collection is already hidden.'})
        collection.is_hidden = True
        collection.hidden_by = request.user
        collection.hidden_at = timezone.now()
        collection.save(update_fields=['is_hidden', 'hidden_by', 'hidden_at'])
        return Response(PublicCollectionSerializer(collection).data)

    @action(detail=True, methods=['post'], permission_classes=[CanUnhideCollection])
    def unhide(self, request, pk=None):
        collection = self.get_object()
        if not collection.is_hidden:
            raise ValidationError({'detail': 'This collection is not hidden.'})
        collection.is_hidden = False
        collection.hidden_by = None
        collection.hidden_at = None
        collection.save(update_fields=['is_hidden', 'hidden_by', 'hidden_at'])
        return Response(PublicCollectionSerializer(collection).data)
