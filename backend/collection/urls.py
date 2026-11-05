from rest_framework.routers import SimpleRouter

from .views import CollectionViewSet, ItemViewSet

router = SimpleRouter()
router.register('collections', CollectionViewSet, basename='collection')
router.register('items', ItemViewSet, basename='item')

urlpatterns = router.urls
