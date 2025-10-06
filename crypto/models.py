from django.conf import settings
from django.db import models
from django.utils import timezone


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
    coingecko_id = models.CharField(max_length=100)
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

    trading_view_name = models.CharField(max_length=256, null=True, blank=True)

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


class CoinVote(models.Model):
    VOTE_CHOICES = [
        ("bullish", "Bullish"),
        ("bearish", "Bearish"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coin_votes"
    )
    coin = models.ForeignKey(CryptoCoin, on_delete=models.CASCADE, related_name="votes")
    vote = models.CharField(max_length=10, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "coin", "created_at")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # Enforce only one vote per day per user per coin
        today = timezone.now().date()
        if CoinVote.objects.filter(
            user=self.user, coin=self.coin, created_at__date=today
        ).exists():
            raise ValueError("You can only vote once per day for this coin.")
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.user} voted {self.vote} on {self.coin} ({self.created_at.date()})"
        )


class CoinRating(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coin_ratings"
    )
    coin = models.ForeignKey(
        CryptoCoin, on_delete=models.CASCADE, related_name="ratings"
    )
    stars = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "coin")  # only one rating per user per coin

    def __str__(self):
        return f"{self.user} rated {self.coin} {self.stars}⭐"


class CoinWishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coin_wishlist"
    )
    coin = models.ForeignKey(
        CryptoCoin, on_delete=models.CASCADE, related_name="wishlisted_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "coin")  # prevent duplicates
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} wishlisted {self.coin}"


class CoinSecurityCheckRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="token_update_requests",
        verbose_name="User",
    )
    coin = models.OneToOneField(
        CryptoCoin,
        on_delete=models.CASCADE,
        related_name="token_update_request",
        verbose_name="Coin",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SecurityRequest({self.coin}) by {self.user}"

    class Meta:
        verbose_name = "Security Request"
        verbose_name_plural = "Security Requests"
