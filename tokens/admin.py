from django.contrib import admin
from .models import GamingToken, TopToken, TokenUpdateRequest


# TODO: Add RANK, USER SCORE, FINAL SCORE,
@admin.register(GamingToken)
class GamingTokenAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "symbol",
        "promoted",
        "security_badge",
        "trading_view_symbol",
        "token_icon",
        "network",
        "pool_address",
        "updated_at",
    )
    list_filter = (
        "promoted",
        "security_badge",
    )
    search_fields = (
        "name",
        "symbol",
        "trading_view_symbol",
        "network",
        "base_token",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "symbol",
                    "promoted",
                    "security_badge",
                    "trading_view_symbol",
                    "token_icon",
                )
            },
        ),
        (
            "Token Info",
            {
                "fields": (
                    "network",
                    "pool_address",
                    "base_token",
                    "quote_token",
                    "about_token",
                )
            },
        ),
        (
            "Links",
            {
                "fields": (
                    "trading_guide_url",
                    "news_url",
                    "telegram_url",
                    "twitter_url",
                    "website_url",
                    "token_contract_url",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


# TODO: Add RANK
@admin.register(TopToken)
class TopTokenAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "symbol",
        "binance_symbol",
        "token_type",
        "promoted",
        "security_badge",
        "trading_view_symbol",
        "coingecko_id",
        "token_icon",
    )
    list_filter = (
        "promoted",
        "security_badge",
        "token_type",
    )
    search_fields = (
        "name",
        "symbol",
        "binance_symbol",
        "trading_view_symbol",
        "coingecko_id",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "symbol",
                    "promoted",
                    "security_badge",
                    "trading_view_symbol",
                    "token_icon",
                )
            },
        ),
        (
            "Identifiers",
            {
                "fields": (
                    "binance_symbol",
                    "coingecko_id",
                    "token_type",
                )
            },
        ),
        (
            "Token Info",
            {
                "fields": (
                    "network",
                    "about_token",
                )
            },
        ),
        (
            "Links",
            {
                "fields": (
                    "trading_guide_url",
                    "news_url",
                    "telegram_url",
                    "twitter_url",
                    "website_url",
                    "token_contract_url",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(TokenUpdateRequest)
class TokenUpdateRequestAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "top_token",
        "gaming_token",
        "created_at",
    ]
    readonly_fields = (
        "user",
        "top_token",
        "gaming_token",
        "created_at",
    )
    search_fields = [
        "top_token__name",
        "gaming_token__name",
    ]
