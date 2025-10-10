from decimal import Decimal
from django.db import models


class MarketSnapshot(models.Model):
    """Global market box (keep history)."""
    fetched_at = models.DateTimeField(auto_now_add=True, db_index=True)
    source_ts = models.DateTimeField(null=True, blank=True)

    market_cap = models.DecimalField(max_digits=30, decimal_places=2)
    market_cap_pct_24h = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal("0"))
    vol_24h = models.DecimalField(max_digits=30, decimal_places=2)
    vol_24h_pct_24h = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal("0"))

    active_cryptos = models.IntegerField(null=True, blank=True)
    active_exchanges = models.IntegerField(null=True, blank=True)
    active_market_pairs = models.IntegerField(null=True, blank=True)

    btc_dominance = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0"))
    eth_dominance = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0"))

    class Meta:
        ordering = ["-fetched_at"]


class Top20IndexPoint(models.Model):
    """Cap-weighted “CMC20” we compute (for sparkline)."""
    ts = models.DateTimeField(auto_now_add=True, db_index=True)
    index_value = models.DecimalField(max_digits=18, decimal_places=4)
    pct_change_24h = models.DecimalField(max_digits=8, decimal_places=4)

    class Meta:
        ordering = ["-ts"]


class FearGreedReading(models.Model):
    """From /v3/fear-and-greed/latest or historical."""
    ts = models.DateTimeField(db_index=True)   # CMC timestamp
    fetched_at = models.DateTimeField(auto_now_add=True)
    value = models.PositiveSmallIntegerField()  # 0..100
    classification = models.CharField(max_length=32)

    class Meta:
        ordering = ["-ts"]
        unique_together = ("ts", "value")


class AltseasonReading(models.Model):
    """% of top 50 alts beating BTC over last 90d (your rule)."""
    ts = models.DateTimeField(auto_now_add=True, db_index=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)  # 0..100
    is_altseason = models.BooleanField(default=False)

    class Meta:
        ordering = ["-ts"]


class AverageRsiReading(models.Model):
    """Average RSI(14) of top-N basket (ex-stables)."""
    ts = models.DateTimeField(auto_now_add=True, db_index=True)
    avg_rsi = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ["-ts"]
