from django.contrib import admin
from .models import MarketStatistics, Category, CryptoCoin


@admin.register(MarketStatistics)
class MarketStatisticsAdmin(admin.ModelAdmin):
    list_display = (
        "cryptos",
        "exchanges",
        "market_cap",
        "vol_24h",
        "dominance",
        "fear_and_greed",
    )
    readonly_fields = ("cryptos", "exchanges", "market_cap", "market_cap_percent",
                       "vol_24h", "vol_24h_percent", "dominance", "fear_and_greed")

    def has_add_permission(self, request):
        """Prevent multiple MarketStatistics entries"""
        return not MarketStatistics.objects.exists()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(CryptoCoin)
class CryptoCoinAdmin(admin.ModelAdmin):
    list_display = (
        "rank",
        "name",
        "symbol",
        "price",
        "percent_change_1h",
        "percent_change_24h",
        "percent_change_7d",
        "market_cap",
        "volume_24h",
        "circulating_supply",
        "category",
        "last_updated",
    )
    list_filter = ("category", "promoted", "security_badge")
    search_fields = ("name", "symbol")
    ordering = ("rank",)
    readonly_fields = ("last_updated", "sparkline_in_7d")

    fieldsets = (
        (None, {
            "fields": (
                "rank", "name", "symbol", "price",
                "percent_change_1h", "percent_change_24h", "percent_change_7d",
                "market_cap", "volume_24h", "circulating_supply",
                "category", "promoted", "security_badge",
                "last_updated", "sparkline_in_7d",
            )
        }),
    )
