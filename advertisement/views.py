from drf_spectacular.utils import OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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
            qs = qs.filter(user=self.request.user)
        return qs

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @extend_schema(
        description="Admin: Set payment status for this advertisement.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "has_payment": {"type": "boolean", "example": True},
                },
                "required": ["has_payment"],
            }
        },
        responses={
            200: OpenApiResponse(
                description="Payment updated",
                response={
                    "application/json": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "example": 12},
                            "has_payment": {"type": "boolean", "example": True},
                        },
                    }
                },
            ),
            400: OpenApiResponse(description="Missing required field"),
        },
    )
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def set_payment(self, request, pk=None):
        ad = self.get_object()
        has_payment = request.data.get("has_payment")

        if has_payment is None:
            return Response(
                {"error": "has_payment field is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ad.has_payment = bool(has_payment)
        ad.save()
        return Response({"id": ad.id, "has_payment": ad.has_payment})

    @extend_schema(
        description="Admin: Select this ad for display on site. Only one ad can be active at a time.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "display_ad": {"type": "boolean", "example": True},
                },
                "required": ["display_ad"],
            }
        },
        responses={
            200: OpenApiResponse(
                description="Display status updated",
                response={
                    "application/json": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "example": 12},
                            "display_ad": {"type": "boolean", "example": True},
                        },
                    }
                },
            ),
            400: OpenApiResponse(description="Missing required field"),
        },
    )
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def set_display(self, request, pk=None):
        """Admin: select this ad for display"""
        ad = self.get_object()
        display_ad = request.data.get("display_ad")

        if display_ad is None:
            return Response(
                {"error": "display_ad field is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ad.display_ad = bool(display_ad)
        ad.save()
        return Response({"id": ad.id, "display_ad": ad.display_ad})
