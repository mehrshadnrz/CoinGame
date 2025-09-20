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


class CryptoCoins(models.Model):
    CATEGORY_CHOICES = [
        ("gaming", "Gaming"),
        ("top", "Top"),
    ]

    rank = models.PositiveIntegerField()
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    percent_change_1h = models.DecimalField(max_digits=6, decimal_places=2, help_text="Change in %")
    percent_change_24h = models.DecimalField(max_digits=6, decimal_places=2, help_text="Change in %")
    percent_change_7d = models.DecimalField(max_digits=6, decimal_places=2, help_text="Change in %")
    market_cap = models.CharField(max_length=20)  # keep string to store values like "2.28T"
    volume_24h = models.CharField(max_length=20)
    circulating_supply = models.CharField(max_length=30)

    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True,
        help_text="Crypto category (Gaming or Top)",
    )

    class Meta:
        ordering = ["rank"]

    def __str__(self):
        return f"{self.rank}. {self.name} ({self.symbol})"

