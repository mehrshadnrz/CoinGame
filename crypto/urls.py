from django.urls import path

from .views import MarketStatisticsView, CryptoCoinListView,  CoinDetailView, CoinImportView

urlpatterns = [
    path("market_statistics/", MarketStatisticsView.as_view(), name="market-statistics"),
    path("crypto_coins/", CryptoCoinListView.as_view(), name="crypto-list"),
    path("crypto_coins/<int:pk>/", CoinDetailView.as_view(), name="coin_detail"),
    path("import-coin/", CoinImportView.as_view(), name="coin-import"),
]
