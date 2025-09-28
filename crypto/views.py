from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Category,
    CryptoCoin,
    MarketStatistics,
)
from .serializers import (
    CategorySerializer,
    CoinDetailSerializer,
    CryptoCoinSerializer,
    MarketStatisticsSerializer,
)
from .services import fetch_coin_detail, import_coin


class MarketStatisticsView(generics.RetrieveAPIView):
    serializer_class = MarketStatisticsSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return MarketStatistics.objects.first()


class CryptoCoinListView(APIView):
    """
    POST endpoint:
    {
        "category": 1,   # optional
        "page": 1        # optional (default = 1)
    }
    """

    PAGE_SIZE = 50

    def post(self, request, *args, **kwargs):
        category_id = request.data.get("category")
        page = int(request.data.get("page", 1))

        queryset = CryptoCoin.objects.all().order_by("rank")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        total_count = queryset.count()

        # Pagination by slicing
        start = (page - 1) * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        coins = queryset[start:end]

        coins_serializer = CryptoCoinSerializer(coins, many=True)

        categories = Category.objects.all()
        categories_serializer = CategorySerializer(categories, many=True)

        return Response(
            {
                "categories": categories_serializer.data,
                "coins": {
                    "count": total_count,
                    "page": page,
                    "page_size": self.PAGE_SIZE,
                    "results": coins_serializer.data,
                },
            },
            status=status.HTTP_200_OK,
        )


class CoinDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, *args, **kwargs):
        coin_obj = get_object_or_404(CryptoCoin, pk=pk)

        detail = fetch_coin_detail(coin_obj.coingecko_id)
        if detail and hasattr(detail, "to_dict"):
            detail = detail.to_dict()

        if not detail:
            return Response(
                {"detail": "Coin detail not available"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CoinDetailSerializer(detail)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CoinImportView(APIView):
    """
    POST /import-coin/
    {
        "symbol": "BTC"
    }
    """

    def post(self, request):
        user = request.user
        symbol = request.data.get("symbol")
        category = request.data.get("category")

        coin, log = import_coin(
            user,
            symbol=symbol,
            category=category,
        )

        if not coin:
            return Response(
                {
                    "error": "Coin not found",
                    "request_id": log.id if log else None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "coin": CryptoCoinSerializer(coin).data,
                "import_request_id": log.id,
                "status": log.status,
            },
            status=status.HTTP_201_CREATED,
        )
