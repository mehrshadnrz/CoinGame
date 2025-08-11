from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class TokenKind(models.TextChoices):
    TOP_TOKEN = "TOP_TOKEN", "Top Token"
    GAMING_TOKEN = "GAMING_TOKEN", "Gaming Token"


class TopTokenTypes(models.TextChoices):
    TOP_TOKEN = "TOP_TOKEN", "Top Token"
    GAME_RELATED_TOKEN = "GAME_RELATED_TOKEN", "Game Related Token"


class ListingStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


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

    created_at = models.DateTimeField(auto_now_add=True)
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
        choices=TopTokenTypes,
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
        related_name="token_update_requests",
        verbose_name="User",
    )

    # Only one of these should be set
    top_token = models.ForeignKey(
        TopToken,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="token_update_requests",
        verbose_name="Top Token",
    )
    gaming_token = models.ForeignKey(
        GamingToken,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="token_update_requests",
        verbose_name="Gamin Token",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        token = self.top_token or self.gaming_token
        return f"UpdateRequest({token}) by {self.user}"

    class Meta:
        verbose_name = "Token Update Request"
        verbose_name_plural = "Token Update Requests"
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


class TokenListingRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="listing_requests",
        verbose_name="User",
    )
    kind = models.CharField(
        max_length=32,
        choices=TokenKind,
        null=False,
        blank=False,
        verbose_name="Token Kind",
    )

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
    network = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name="Network",
    )

    # Gaming Token fields
    pool_address = models.CharField(
        max_length=256,
        null=True,
        blank=True,
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

    # Top Token fields
    binance_symbol = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        unique=True,
        verbose_name="Binance Symbol",
    )
    token_type = models.CharField(
        max_length=32,
        choices=TopTokenTypes,
        null=True,
        blank=True,
        verbose_name="Type",
    )
    coingecko_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        unique=True,
        verbose_name="CoinGecko ID",
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

    # status & admin metadata
    status = models.CharField(
        max_length=10,
        choices=ListingStatus.choices,
        default=ListingStatus.PENDING,
        null=False,
        blank=False,
        verbose_name="Status",
    )
    admin_note = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="processed_listing_requests",
        verbose_name="Processed By",
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_processed(
        self,
        processor_user,
        approved: bool,
        admin_note: str | None = None,
    ) -> None:
        self.status = ListingStatus.APPROVED if approved else ListingStatus.REJECTED
        self.admin_note = admin_note
        self.processed_by = processor_user
        self.processed_at = timezone.now()
        self.save()

    def clean(self):
        def has_value(v):
            return v is not None and str(v).strip() != ""

        match self.kind:
            case TokenKind.GAMING_TOKEN:
                if not has_value(self.pool_address):
                    raise ValidationError(
                        {"pool_address": "pool_address is required for gaming tokens."}
                    )
                if not has_value(self.network):
                    raise ValidationError(
                        {"network": "network is required for gaming tokens."}
                    )
            case TokenKind.TOP_TOKEN:
                if not has_value(self.binance_symbol):
                    raise ValidationError(
                        {"binance_symbol": "binance_symbol is required for top tokens."}
                    )
                if not has_value(self.token_type):
                    raise ValidationError(
                        {"token_type": "token_type is required for top tokens."}
                    )
                if not has_value(self.coingecko_id):
                    raise ValidationError(
                        {"coingecko_id": "coingecko_id is required for top tokens."}
                    )
            case _:
                raise ValidationError(
                        {"kind": "Invalid token kind. Use 'TOP_TOKEN' or 'GAMING_TOKEN'."}
                    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Token Listing Request"
        verbose_name_plural = "Token Listing Requests"
        constraints = [
            models.CheckConstraint(
                check=(
                    # when kind is 'gaming' require non-null/non-empty pool_address and network
                    (
                        Q(kind=TokenKind.GAMING_TOKEN)
                        & Q(pool_address__isnull=False)
                        & ~Q(pool_address="")
                        & Q(network__isnull=False)
                        & ~Q(network="")
                    )
                    |
                    # when kind is 'top' require non-null/non-empty binance_symbol, token_type, coingecko_id
                    (
                        Q(kind=TokenKind.TOP_TOKEN)
                        & Q(binance_symbol__isnull=False)
                        & ~Q(binance_symbol="")
                        & Q(token_type__isnull=False)
                        & ~Q(token_type="")
                        & Q(coingecko_id__isnull=False)
                        & ~Q(coingecko_id="")
                    )
                ),
                name="token_listing_request_kind_required_fields",
            ),
        ]
