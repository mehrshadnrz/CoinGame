from rest_framework import generics, permissions

from .models import CryptoCoins, MarketStatistics
from .serializers import CryptoCoinSerializer, MarketStatisticsSerializer


class MarketStatisticsView(generics.RetrieveAPIView):
    serializer_class = MarketStatisticsSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return MarketStatistics.objects.first()


class CryptoCoinListView(generics.ListAPIView):
    serializer_class = CryptoCoinSerializer

    def get_queryset(self):
        queryset = CryptoCoins.objects.all()
        category = self.request.query_params.get("category")
        if category in ["gaming", "top"]:
            queryset = queryset.filter(category=category)
        return queryset
