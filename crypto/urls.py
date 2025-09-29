from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CoinDetailView,
    CoinImportView,
    CryptoCoinListView,
    CryptoCoinViewSet,
    MarketStatisticsView,
    UserWishListViewSet,
)

router = DefaultRouter()
router.register(r"coins", CryptoCoinViewSet, basename="coin")
router.register(r"wishlist", UserWishListViewSet, basename="wishlist")

urlpatterns = [
    path("market_statistics/", MarketStatisticsView.as_view(), name="market-statistics"),
    path("crypto_coins/", CryptoCoinListView.as_view(), name="crypto-list"),
    path("crypto_coins/<int:pk>/", CoinDetailView.as_view(), name="coin-detail"),
    path("import-coin/", CoinImportView.as_view(), name="coin-import"),

    path("", include(router.urls)),
]
