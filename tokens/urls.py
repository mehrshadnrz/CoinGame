from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tokens.views import (
    GamingTokenViewSet,
    TokenListingRequestViewSet,
    TokenUpdateRequestViewSet,
    TopTokenViewSet,
)

router = DefaultRouter()
router.register(r'gaming-tokens', GamingTokenViewSet, basename='gaming-token')
router.register(r'top-tokens', TopTokenViewSet, basename='top-token')
router.register(r'update-requests', TokenUpdateRequestViewSet, basename='token-update-request')
router.register(r"token-listing-requests", TokenListingRequestViewSet, basename="token-listing-request")

urlpatterns = [
    path('', include(router.urls)),
]
