from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tokens.views import GamingTokenViewSet, TopTokenViewSet, TokenUpdateRequestViewSet

router = DefaultRouter()
router.register(r'gaming-tokens', GamingTokenViewSet, basename='gaming-token')
router.register(r'top-tokens', TopTokenViewSet, basename='top-token')
router.register(r'update-requests', TokenUpdateRequestViewSet, basename='token-update-request')

urlpatterns = [
    path('', include(router.urls)),
]
