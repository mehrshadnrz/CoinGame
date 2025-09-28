from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, CryptoCoins, MarketStatistics
from .serializers import (
    CategorySerializer,
    CoinDetailSerializer,
    CryptoCoinSerializer,
    MarketStatisticsSerializer,
)
from .services import fetch_coin_detail


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

        queryset = CryptoCoins.objects.all().order_by("rank")
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
    """
    GET /api/coins/detail/<int:pk>/

    Example:
      /api/coins/detail/1/
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, *args, **kwargs):
        # Step 1: Find coin in DB
        coin_obj = get_object_or_404(CryptoCoins, pk=pk)

        # Step 2: Request detail from CoinGecko (using name/id, not DB id)
        # CoinGecko ids are lowercase and hyphenated (e.g., 'bitcoin', 'ethereum')
        coin_id = coin_obj.name.lower().replace(" ", "-")
        detail = fetch_coin_detail(coin_id)

        if not detail:
            return Response(
                {"detail": "Coin detail not available"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Step 3: Serialize response
        detail_dict = (
            detail.to_dict() if hasattr(detail, "to_dict") else detail.__dict__
        )
        serializer = CoinDetailSerializer(detail_dict)
        return Response(serializer.data, status=status.HTTP_200_OK)
