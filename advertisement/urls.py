from rest_framework.routers import DefaultRouter
from advertisement.views import AdvertisementViewSet, AdvertisementPlanViewSet

router = DefaultRouter()
router.register(r"ads", AdvertisementViewSet, basename="advertisement")
router.register(r"ad-plans", AdvertisementPlanViewSet, basename="advertisement-plan")

urlpatterns = router.urls
