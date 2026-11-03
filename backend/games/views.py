from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response
from rest_framework.views import APIView

from .search import search_games
from .serializers import SearchQuerySerializer, SearchResultSerializer


class GameSearchView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'search'

    def get(self, request):
        params = SearchQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        page = params.validated_data['page']
        games, total, saved_data = search_games(params.validated_data['q'], page)
        return Response({
            'count': total,
            'page': page,
            'results': SearchResultSerializer(games, many=True).data,
            'saved_data': saved_data,
        })
