from django.urls import include, path
from rest_framework.routers import DefaultRouter

from promotion.views import TokenPromotionPlanViewSet, TokenPromotionRequestViewSet

router = DefaultRouter()
router.register(
    r"promotion-plans", TokenPromotionPlanViewSet, basename="promotion-plan"
)
router.register(
    r"promotion-requests", TokenPromotionRequestViewSet, basename="promotion-request"
)

urlpatterns = [
    path("", include(router.urls)),
]
