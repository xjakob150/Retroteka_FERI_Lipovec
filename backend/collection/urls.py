from rest_framework.routers import SimpleRouter

from .views import CollectionViewSet, ItemViewSet, PublicCollectionViewSet

router = SimpleRouter()
router.register('collections', CollectionViewSet, basename='collection')
router.register('items', ItemViewSet, basename='item')
router.register('public/collections', PublicCollectionViewSet, basename='public-collection')

urlpatterns = router.urls
