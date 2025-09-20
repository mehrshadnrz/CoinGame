from django.urls import path

from .views import MarketStatisticsView, CryptoCoinListView

urlpatterns = [
    path("market_statistics/", MarketStatisticsView.as_view(), name="market-statistics"),
    path("crypto_coins/", CryptoCoinListView.as_view(), name="crypto-list"),
]
