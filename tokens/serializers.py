from rest_framework import serializers
from tokens.models import GamingToken, TopToken


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
