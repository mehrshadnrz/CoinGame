from django.db import models
from rest_framework import serializers

from tokens.models import GamingToken, TokenUpdateRequest, TopToken


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
