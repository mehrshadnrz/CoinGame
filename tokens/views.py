from django.db import IntegrityError, transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from tokens.models import (
    GamingToken,
    ListingStatus,
    TokenKind,
    TokenListingRequest,
    TokenUpdateRequest,
    TopToken,
)
from tokens.serializers import (
    GamingTokenSerializer,
    TokenListingRequestSerializer,
    TokenUpdateRequestSerializer,
    TopTokenSerializer,
)


class GamingTokenViewSet(viewsets.ModelViewSet):
    queryset = GamingToken.objects.all()
    serializer_class = GamingTokenSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class TopTokenViewSet(viewsets.ModelViewSet):
    queryset = TopToken.objects.all()
    serializer_class = TopTokenSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


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

    @extend_schema(
        description="Accept a token update request. This will apply the update and delete the request.",
        request=None,
        responses={
            200: OpenApiResponse(
                description="Update request accepted",
                response={
                    "application/json": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "example": "Token update accepted",
                            }
                        },
                    }
                },
            ),
            400: OpenApiResponse(description="Invalid token request"),
            404: OpenApiResponse(description="Request not found"),
        },
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


class TokenListingRequestViewSet(viewsets.ModelViewSet):
    """
    Users:
      - create listing requests
      - list / retrieve their own requests
      - update / delete their own requests ONLY if status == PENDING

    Staff/Admin:
      - list all requests
      - retrieve any request
      - approve / reject requests via the custom actions

    Admins are NOT allowed to update or delete requests (except via approve/reject).
    """

    queryset = TokenListingRequest.objects.all().order_by("-created_at")
    serializer_class = TokenListingRequestSerializer

    def get_permissions(self):
        if self.action in ("approve", "reject"):
            return [permissions.IsAdminUser()]

        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        description="Approve a token listing request. Admin only.",
        request=None,
        responses={
            200: OpenApiResponse(
                description="Request approved and token created",
                response={
                    "application/json": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string", "example": "Approved"},
                            "token_id": {"type": "integer", "example": 42},
                        },
                    }
                },
            ),
            400: OpenApiResponse(
                description="Request already processed or token exists"
            ),
            500: OpenApiResponse(description="Integrity error while creating token"),
        },
    )
    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        req = self.get_object()
        if req.status != ListingStatus.PENDING:
            return Response(
                {"detail": "Request already processed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                if (
                    TopToken.objects.filter(symbol__iexact=req.symbol).exists()
                    or GamingToken.objects.filter(symbol__iexact=req.symbol).exists()
                ):
                    req.mark_processed(
                        request.user,
                        approved=False,
                        admin_note="Token already exists at approval time.",
                    )
                    return Response(
                        {"detail": "Token already exists in production."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                match req.kind:
                    case TokenKind.TOP_TOKEN:
                        token = TopToken.objects.create(
                            name=req.name,
                            symbol=req.symbol,
                            trading_view_symbol=req.trading_view_symbol,
                            token_icon=req.token_icon,
                            about_token=req.about_token or "",
                            network=req.network or None,
                            binance_symbol=req.binance_symbol or "",
                            token_type=req.token_type or None,
                            coingecko_id=req.coingecko_id or "",
                            promoted=False,
                            security_badge=True,
                            trading_guide_url=req.trading_guide_url,
                            news_url=req.news_url,
                            telegram_url=req.telegram_url,
                            twitter_url=req.twitter_url,
                            website_url=req.website_url,
                            token_contract_url=req.token_contract_url,
                        )
                    case TokenKind.GAMING_TOKEN:
                        token = GamingToken.objects.create(
                            name=req.name,
                            symbol=req.symbol,
                            trading_view_symbol=req.trading_view_symbol,
                            token_icon=req.token_icon,
                            about_token=req.about_token or "",
                            network=req.network or "",
                            pool_address=req.pool_address or "",
                            base_token=req.base_token or "",
                            quote_token=req.quote_token or "",
                            promoted=False,
                            security_badge=True,
                            trading_guide_url=req.trading_guide_url,
                            news_url=req.news_url,
                            telegram_url=req.telegram_url,
                            twitter_url=req.twitter_url,
                            website_url=req.website_url,
                            token_contract_url=req.token_contract_url,
                        )
                    case _:
                        raise IntegrityError

                req.mark_processed(
                    request.user,
                    approved=True,
                    admin_note=f"Created token id={token.id}",
                )
                return Response(
                    {"detail": "Approved", "token_id": token.id},
                    status=status.HTTP_200_OK,
                )

        except IntegrityError:
            req.mark_processed(
                request.user,
                approved=False,
                admin_note="IntegrityError during creation.",
            )
            return Response(
                {"detail": "Failed to create token due to IntegrityError."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        description="Reject a token listing request. Admin only.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "admin_note": {
                        "type": "string",
                        "example": "Token does not meet requirements",
                    }
                },
                "required": ["admin_note"],
            }
        },
        responses={
            200: OpenApiResponse(
                description="Request rejected",
                response={
                    "application/json": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string", "example": "Rejected"}
                        },
                    }
                },
            ),
            400: OpenApiResponse(description="Request already processed"),
        },
    )
    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        req = self.get_object()
        if req.status != ListingStatus.PENDING:
            return Response(
                {"detail": "Request already processed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        admin_note = request.data.get("admin_note")
        icon = req.token_icon
        req.mark_processed(request.user, approved=False, admin_note=admin_note)

        if icon:
            try:
                storage = icon.storage
                if storage.exists(icon.name):
                    storage.delete(icon.name)
            except Exception:
                pass

        return Response({"detail": "Rejected"}, status=status.HTTP_200_OK)

    def _deny_if_not_owner_or_pending(self, request, obj):
        if request.user.is_staff:
            return Response(
                {"detail": "Admins cannot update or delete requests."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if obj.user_id != request.user.id:
            return Response(
                {"detail": "You do not own this request."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if obj.status != ListingStatus.PENDING:
            return Response(
                {"detail": "Only requests with status PENDING can be modified."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return None

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        deny = self._deny_if_not_owner_or_pending(request, obj)
        if deny is not None:
            return deny
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        deny = self._deny_if_not_owner_or_pending(request, obj)
        if deny is not None:
            return deny
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        deny = self._deny_if_not_owner_or_pending(request, obj)
        if deny is not None:
            return deny

        icon = obj.token_icon
        try:
            response = super().destroy(request, *args, **kwargs)
        except Exception:
            return Response(
                {"detail": "Failed to delete request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if icon:
            try:
                storage = icon.storage
                if storage.exists(icon.name):
                    storage.delete(icon.name)
            except Exception:
                pass

        return response
