from django.db import models
from rest_framework import serializers

from tokens.models import (
    TokenKind,
    GamingToken,
    TokenListingRequest,
    TokenUpdateRequest,
    TopToken,
    TokenPromotionPlan,
    TokenPromotionRequest,
)


class GamingTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = GamingToken
        fields = [
            "id",
            "name",
            "symbol",
            "promoted",
            "security_badge",
            "trading_view_symbol",
            "token_icon",
            "network",
            "pool_address",
            "about_token",
            "base_token",
            "quote_token",
            "trading_guide_url",
            "news_url",
            "telegram_url",
            "twitter_url",
            "website_url",
            "token_contract_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class TopTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopToken
        fields = [
            "id",
            "name",
            "symbol",
            "promoted",
            "security_badge",
            "trading_view_symbol",
            "token_icon",
            "network",
            "token_type",
            "about_token",
            "trading_guide_url",
            "news_url",
            "telegram_url",
            "twitter_url",
            "website_url",
            "token_contract_url",
            "binance_symbol",
            "coingecko_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class TokenUpdateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenUpdateRequest
        fields = [
            "id",
            "user",
            "top_token",
            "gaming_token",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
        ]

    def validate(self, data):
        top_token = data.get("top_token")
        gaming_token = data.get("gaming_token")

        if bool(top_token) == bool(gaming_token):
            raise serializers.ValidationError(
                "Exactly one of top_token or gaming_token must be set."
            )
        if top_token:
            if TokenUpdateRequest.objects.filter(top_token=top_token).exists():
                raise serializers.ValidationError(
                    {"top_token": "An update request for this token already exists."}
                )
        elif gaming_token:
            if TokenUpdateRequest.objects.filter(gaming_token=gaming_token).exists():
                raise serializers.ValidationError(
                    {"gaming_token": "An update request for this token already exists."}
                )
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        try:
            instance = super().create(validated_data)
        except models.IntegrityError as e:
            if "unique_top_token_request" in str(e):
                raise serializers.ValidationError(
                    {"top_token": "An update request for this token already exists."}
                ) from e
            elif "unique_gaming_token_request" in str(e):
                raise serializers.ValidationError(
                    {"gaming_token": "An update request for this token already exists."}
                ) from e
            raise

        token = instance.top_token or instance.gaming_token
        token.security_badge = False
        token.save()

        return instance


class TokenListingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenListingRequest
        fields = [
            "id",
            "user",
            "kind",
            "name",
            "symbol",
            "trading_view_symbol",
            "token_icon",
            "about_token",
            "network",
            "pool_address",
            "base_token",
            "quote_token",
            "binance_symbol",
            "token_type",
            "coingecko_id",
            "trading_guide_url",
            "news_url",
            "telegram_url",
            "twitter_url",
            "website_url",
            "token_contract_url",
            "status",
            "admin_note",
            "processed_by",
            "processed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "user",
            "status",
            "admin_note",
            "processed_by",
            "processed_at",
            "created_at",
            "updated_at",
        )

    def _get_value(self, attrs, name):
        """Helper: prefer attrs value, fall back to instance value (for updates)."""
        if name in attrs:
            return attrs.get(name)
        if self.instance is not None:
            return getattr(self.instance, name)
        return None

    def validate(self, attrs):
        """
        Enforce:
        - token with same symbol must not already exist in production
        - required fields depending on kind ('top' or 'gaming')
        """
        # Merge relevant fields from incoming attrs and instance
        kind = self._get_value(attrs, "kind")
        symbol = self._get_value(attrs, "symbol")
        name = self._get_value(attrs, "name")

        if symbol:
            if (
                TopToken.objects.filter(symbol__iexact=symbol).exists()
                or GamingToken.objects.filter(symbol__iexact=symbol).exists()
            ):
                raise serializers.ValidationError(
                    {"symbol": "A token with this symbol already exists."}
                )

        if name:
            if (
                TopToken.objects.filter(name__iexact=name).exists()
                or GamingToken.objects.filter(name__iexact=name).exists()
            ):
                raise serializers.ValidationError(
                    {"name": "A token with this name already exists."}
                )

        match kind:
            case None:
                raise serializers.ValidationError({"kind": "Token kind is required."})
            case TokenKind.GAMING_TOKEN:
                pool_address = self._get_value(attrs, "pool_address")
                network = self._get_value(attrs, "network")
                if not pool_address or str(pool_address).strip() == "":
                    raise serializers.ValidationError(
                        {"pool_address": "pool_address is required for gaming tokens."}
                    )
                if not network or str(network).strip() == "":
                    raise serializers.ValidationError(
                        {"network": "network is required for gaming tokens."}
                    )
            case TokenKind.TOP_TOKEN:
                binance_symbol = self._get_value(attrs, "binance_symbol")
                token_type = self._get_value(attrs, "token_type")
                coingecko_id = self._get_value(attrs, "coingecko_id")
                if not binance_symbol or str(binance_symbol).strip() == "":
                    raise serializers.ValidationError(
                        {"binance_symbol": "binance_symbol is required for top tokens."}
                    )
                if not token_type or str(token_type).strip() == "":
                    raise serializers.ValidationError(
                        {"token_type": "token_type is required for top tokens."}
                    )
                if not coingecko_id or str(coingecko_id).strip() == "":
                    raise serializers.ValidationError(
                        {"coingecko_id": "coingecko_id is required for top tokens."}
                    )
            case _:
                raise serializers.ValidationError(
                    {"kind": "Invalid token kind. Use 'TOP_TOKEN' or 'GAMING_TOKEN'."}
                )

        return attrs

    def create(self, validated_data):
        request = self.context.get("request", None)
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user
        return super().create(validated_data)


class TokenPromotionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenPromotionPlan
        fields = [
            "id",
            "name",
            "duration_in_months",
            "cost_usd",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class TokenPromotionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenPromotionRequest
        fields = [
            "id",
            "user",
            "plan",
            "top_token",
            "gaming_token",
            "has_payment",
            "expires_at",
            "created_at",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "user",
            "expires_at",
            "created_at",
            "is_active",
        ]

    def validate(self, data):
        top_token = data.get("top_token")
        gaming_token = data.get("gaming_token")
        if bool(top_token) == bool(gaming_token):
            raise serializers.ValidationError(
                "Exactly one of top_token or gaming_token must be set."
            )
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user
        return super().create(validated_data)
