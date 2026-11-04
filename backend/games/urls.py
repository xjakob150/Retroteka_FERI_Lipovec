from django.urls import path

from .views import GameSearchView, PlatformListView

urlpatterns = [
    path('platforms/', PlatformListView.as_view(), name='platform-list'),
    path('search/', GameSearchView.as_view(), name='game-search'),
]
