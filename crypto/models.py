from django.conf import settings
from django.db import models


class MarketStatistics(models.Model):
    cryptos = models.CharField(max_length=255)
    exchanges = models.IntegerField()
    market_cap = models.CharField(max_length=255)
    market_cap_percent = models.CharField(max_length=255)
    vol_24h = models.CharField(max_length=255)
    vol_24h_percent = models.CharField(max_length=255)
    dominance = models.CharField(max_length=255)
    fear_and_greed = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.pk and MarketStatistics.objects.exists():
            raise Exception("Only one MarketStatistics instance allowed.")
        return super().save(*args, **kwargs)

    def __str__(self):
        return "Market Statistics"


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class CryptoCoin(models.Model):
    coingecko_id = models.CharField(
        max_length=100, unique=True, help_text="CoinGecko API ID (e.g. 'bitcoin')"
    )
    rank = models.PositiveIntegerField(null=True, blank=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=32)
    price = models.DecimalField(max_digits=20, decimal_places=2)

    percent_change_1h = models.DecimalField(
        max_digits=6, decimal_places=2, help_text="Change in %"
    )
    percent_change_24h = models.DecimalField(
        max_digits=6, decimal_places=2, help_text="Change in %"
    )
    percent_change_7d = models.DecimalField(
        max_digits=6, decimal_places=2, help_text="Change in %"
    )

    market_cap = models.CharField(max_length=20)
    volume_24h = models.CharField(max_length=20)
    circulating_supply = models.CharField(max_length=30)

    sparkline_in_7d = models.JSONField(null=True, blank=True)

    promoted = models.BooleanField(default=False)
    security_badge = models.BooleanField(default=True)

    category = models.ForeignKey(
        Category,
        related_name="coins",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["rank"]

    def __str__(self):
        return f"{self.rank}. {self.name} ({self.symbol})"


class CoinImportRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coin_imports"
    )
    symbol = models.CharField(max_length=50, null=True, blank=True)
    chain = models.CharField(max_length=20, null=True, blank=True)
    pool_address = models.CharField(max_length=100, null=True, blank=True)

    created_coin = models.ForeignKey(
        CryptoCoin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="import_requests",
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("success", "Success"),
            ("failed", "Failed"),
        ],
        default="failed",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.user} imported {self.symbol or self.pool_address} ({self.source})"
        )
