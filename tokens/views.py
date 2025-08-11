from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from tokens.models import GamingToken, TokenUpdateRequest, TopToken
from tokens.serializers import (
    GamingTokenSerializer,
    TokenUpdateRequestSerializer,
    TopTokenSerializer,
)


class GamingTokenViewSet(viewsets.ModelViewSet):
    queryset = GamingToken.objects.all()
    serializer_class = GamingTokenSerializer


class TopTokenViewSet(viewsets.ModelViewSet):
    queryset = TopToken.objects.all()
    serializer_class = TopTokenSerializer


class TokenUpdateRequestViewSet(viewsets.ModelViewSet):
    queryset = TokenUpdateRequest.objects.all()
    serializer_class = TokenUpdateRequestSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_permissions(self):
        if self.action in ["accept", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return TokenUpdateRequest.objects.all()
        return TokenUpdateRequest.objects.filter(user=self.request.user)

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

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        try:
            update_request = self.get_object()
            token = update_request.top_token or update_request.gaming_token

            if not token:
                return Response(
                    {"error": "Invalid token request"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token.security_badge = True
            token.save()

            update_request.delete()
            return Response({"status": "Token update accepted"})

        except TokenUpdateRequest.DoesNotExist:
            return Response(
                {"error": "Request not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
