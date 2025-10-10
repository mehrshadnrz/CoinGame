from django.contrib import admin
from .models import (
    MarketSnapshot,
    Top20IndexPoint,
    FearGreedReading,
    AltseasonReading,
    AverageRsiReading,
)

@admin.register(MarketSnapshot)
class MarketSnapshotAdmin(admin.ModelAdmin):
    date_hierarchy = "fetched_at"
    list_display = (
        "fetched_at",
        "market_cap_short",
        "market_cap_pct_24h",
        "vol_24h_short",
        "vol_24h_pct_24h",
        "btc_dominance",
        "eth_dominance",
        "active_cryptos",
        "active_exchanges",
    )
    list_filter = ("active_exchanges",)
    search_fields = ()
    readonly_fields = (
        "fetched_at",
        "source_ts",
        "market_cap",
        "market_cap_pct_24h",
        "vol_24h",
        "vol_24h_pct_24h",
        "active_cryptos",
        "active_exchanges",
        "active_market_pairs",
        "btc_dominance",
        "eth_dominance",
    )

    def market_cap_short(self, obj):
        return f"{int(obj.market_cap):,}"
    market_cap_short.short_description = "Market Cap"

    def vol_24h_short(self, obj):
        return f"{int(obj.vol_24h):,}"
    vol_24h_short.short_description = "Vol 24h"


@admin.register(Top20IndexPoint)
class Top20IndexPointAdmin(admin.ModelAdmin):
    date_hierarchy = "ts"
    list_display = ("ts", "index_value", "pct_change_24h")
    ordering = ("-ts",)
    readonly_fields = ("ts", "index_value", "pct_change_24h")


@admin.register(FearGreedReading)
class FearGreedReadingAdmin(admin.ModelAdmin):
    date_hierarchy = "ts"
    list_display = ("ts", "value", "classification", "fetched_at")
    ordering = ("-ts",)
    readonly_fields = ("ts", "fetched_at", "value", "classification")
    list_filter = ("classification",)


@admin.register(AltseasonReading)
class AltseasonReadingAdmin(admin.ModelAdmin):
    date_hierarchy = "ts"
    list_display = ("ts", "percentage", "is_altseason")
    list_filter = ("is_altseason",)
    ordering = ("-ts",)
    readonly_fields = ("ts", "percentage", "is_altseason")


@admin.register(AverageRsiReading)
class AverageRsiReadingAdmin(admin.ModelAdmin):
    date_hierarchy = "ts"
    list_display = ("ts", "avg_rsi")
    ordering = ("-ts",)
    readonly_fields = ("ts", "avg_rsi")
