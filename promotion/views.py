from rest_framework import permissions, viewsets

from promotion.models import TokenPromotionPlan, TokenPromotionRequest
from promotion.serializers import TokenPromotionPlanSerializer, TokenPromotionRequestSerializer


class TokenPromotionPlanViewSet(viewsets.ModelViewSet):
    """
    CRUD for promotion plans.
    - Public: list/retrieve (to show available plans to users).
    - Admin: create/update/delete.
    """

    queryset = TokenPromotionPlan.objects.all().order_by("cost")
    serializer_class = TokenPromotionPlanSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class TokenPromotionRequestViewSet(viewsets.ModelViewSet):
    """
    Promotion requests created by users.
    - User: create/list/retrieve their own requests.
    - Admin: list all requests, mark payment, etc.
    """

    queryset = TokenPromotionRequest.objects.all().order_by("-created_at")
    serializer_class = TokenPromotionRequestSerializer

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
