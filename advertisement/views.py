from django.utils.timezone import now
from rest_framework import permissions, viewsets

from advertisement.models import Advertisement, AdvertisementPlan
from advertisement.serializers import (
    AdvertisementPlanSerializer,
    AdvertisementSerializer,
)


class AdvertisementPlanViewSet(viewsets.ModelViewSet):
    queryset = AdvertisementPlan.objects.all().order_by("-created_at")
    serializer_class = AdvertisementPlanSerializer
    permission_classes = [permissions.IsAdminUser]


class AdvertisementViewSet(viewsets.ModelViewSet):
    serializer_class = AdvertisementSerializer

    def get_queryset(self):
        qs = Advertisement.objects.all().order_by("-created_at")
        if self.action == "list" and not self.request.user.is_staff:
            qs = qs.filter(expires_at__gt=now())
        return qs

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
