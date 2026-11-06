from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response
from rest_framework.views import APIView

from collection.ownership import owned_by

from .models import Platform
from .search import search_games
from .serializers import PlatformSerializer, SearchQuerySerializer, SearchResultSerializer


class PlatformListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PlatformSerializer
    queryset = Platform.objects.filter(is_supported=True).order_by('generation', 'name')


class GameSearchView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'search'

    def get(self, request):
        params = SearchQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        page = params.validated_data['page']
        games, total, saved_data = search_games(
            params.validated_data['q'], page, params.validated_data.get('platform'),
        )
        results = SearchResultSerializer(games, many=True).data
        if request.user.is_authenticated:
            # Samo prijavljeni dobijo, kje že imajo igro (US-10); gost tega polja ne dobi.
            owned = owned_by(request.user, games)
            for result in results:
                result['owned'] = owned.get(result['id'], [])
        return Response({
            'count': total,
            'page': page,
            'results': results,
            'saved_data': saved_data,
        })
