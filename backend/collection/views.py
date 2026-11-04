from rest_framework import mixins, viewsets

from .models import Collection
from .permissions import IsCollectionOwner
from .serializers import CollectionSerializer


class CollectionViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = CollectionSerializer
    permission_classes = [IsCollectionOwner]

    def get_queryset(self):
        # Vsa dejanja vidijo samo zbirke prijavljenega uporabnika, zato je tuja zbirka 404.
        return Collection.objects.filter(user=self.request.user)
