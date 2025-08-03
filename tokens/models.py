from django.db import models
from django.conf import settings


class TokenTypes(models.TextChoices):
    TOP_TOKEN = "TOP_TOKEN", "Top Token"
    GAME_RELATED_TOKEN = "GAME_RELATED_TOKEN", "Game Related Token"


class CoinToken(models.Model):
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        unique=True,
        verbose_name="Name",
    )
    symbol = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        unique=True,
        verbose_name="Symbol",
    )
    promoted = models.BooleanField(
        default=False,
        null=False,
        blank=False,
        verbose_name="Promoted",
    )
    security_badge = models.BooleanField(
        default=False,
        null=False,
        blank=False,
        verbose_name="Security Badge",
    )
    trading_view_symbol = models.CharField(
        max_length=10,
        null=False,
        blank=False,
        verbose_name="TradingView Symbol",
    )
    token_icon = models.ImageField(
        upload_to="token_icons/",
        blank=True,
        null=True,
        verbose_name="Token Icon",
    )
    about_token = models.TextField(
        blank=True,
        null=True,
        verbose_name="About Token",
    )

    # LINKS
    trading_guide_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Trading Guide URL",
    )
    news_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="News URL",
    )
    telegram_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Telegram URL",
    )
    twitter_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Twitter URL",
    )
    website_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Website URL",
    )
    token_contract_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Token Contract URL",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class GamingToken(CoinToken):
    network = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name="Network",
    )
    pool_address = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        verbose_name="Pool address",
    )
    base_token = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name="Base Token",
    )
    quote_token = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name="Quote Token",
    )

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    class Meta:
        verbose_name = "Gaming Token"
        verbose_name_plural = "Gaming Tokens"


class TopToken(CoinToken):
    binance_symbol = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        unique=True,
        verbose_name="Binance Symbol",
    )
    token_type = models.CharField(
        max_length=32,
        choices=TokenTypes,
        null=False,
        blank=False,
        verbose_name="Type",
    )
    coingecko_id = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        unique=True,
        verbose_name="CoinGecko ID",
    )
    network = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Network",
    )

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    class Meta:
        verbose_name = "Top Token"
        verbose_name_plural = "Top Tokens"


class TokenUpdateRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name="User",
    )

    # Only one of these should be set
    top_token = models.ForeignKey(
        TopToken,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Top Token",
    )
    gaming_token = models.ForeignKey(
        GamingToken,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Gamin Token",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["top_token"],
                condition=models.Q(top_token__isnull=False),
                name="unique_top_token_request",
            ),
            models.UniqueConstraint(
                fields=["gaming_token"],
                condition=models.Q(gaming_token__isnull=False),
                name="unique_gaming_token_request",
            ),
            models.CheckConstraint(
                check=models.Q(top_token__isnull=False, gaming_token__isnull=True)
                | models.Q(top_token__isnull=True, gaming_token__isnull=False),
                name="exactly_one_token_set",
            ),
        ]

    def __str__(self):
        token = self.top_token or self.gaming_token
        return f"UpdateRequest({token}) by {self.user}"
