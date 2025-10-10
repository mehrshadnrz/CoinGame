from django.urls import path
from .views import (
    DashboardUpdateView, DashboardAggregateView,
    MarketCapView, CMC20View, FearGreedView,
    AltseasonView, AverageRsiView,
)

app_name = "marketglobal"

urlpatterns = [
    path("boxes/update/", DashboardUpdateView.as_view(), name="boxes-update"),
    path("boxes/dashboard/", DashboardAggregateView.as_view(), name="boxes-dashboard"),

    path("boxes/marketcap/", MarketCapView.as_view(), name="boxes-marketcap"),
    path("boxes/cmc20/", CMC20View.as_view(), name="boxes-cmc20"),
    path("boxes/fear-greed/", FearGreedView.as_view(), name="boxes-fear-greed"),
    path("boxes/altseason/", AltseasonView.as_view(), name="boxes-altseason"),
    path("boxes/average-rsi/", AverageRsiView.as_view(), name="boxes-average-rsi"),
]
