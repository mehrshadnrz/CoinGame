from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payment.views import PaymentIntentViewSet

router = DefaultRouter()
router.register(r'payment-intents', PaymentIntentViewSet, basename='payment-intents')

urlpatterns = [
    path("", include(router.urls)),
]
