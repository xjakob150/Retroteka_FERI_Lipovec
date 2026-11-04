from rest_framework.routers import SimpleRouter

from .views import CollectionViewSet

router = SimpleRouter()
router.register('collections', CollectionViewSet, basename='collection')

urlpatterns = router.urls
