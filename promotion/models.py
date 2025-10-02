from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from crypto.models import CryptoCoin


class TokenPromotionPlan(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        null=False,
        blank=False,
        verbose_name=_("Plan Name"),
    )
    duration_in_months = models.PositiveIntegerField(
        null=False,
        blank=False,
        verbose_name=_("Ad Duration (Months)"),
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        blank=False,
        verbose_name=_("Cost"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.duration_in_months} months / ${self.cost})"

    class Meta:
        verbose_name = "Token Promotion Plan"
        verbose_name_plural = "Token Promotion Plans"


class TokenPromotionRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="token_promotion_requests",
        verbose_name="User",
    )
    plan = models.ForeignKey(
        TokenPromotionPlan,
        on_delete=models.CASCADE,
        related_name="token_promotion_requests",
        null=False,
        blank=False,
        verbose_name=_("Token Promotion Plan"),
    )

    coin = models.ForeignKey(
        CryptoCoin,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="token_promotion_requests",
        verbose_name="Top Token",
    )

    has_payment = models.BooleanField(default=False, verbose_name=_("Has payment"))
    is_active = models.BooleanField(default=False)
    expires_at = models.DateTimeField(blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Promotion Request({self.coin}) by {self.user}"

    def save(self, *args, **kwargs):
        if not self.expires_at and self.plan:
            self.expires_at = (self.created_at or now()) + timedelta(
                days=30 * self.plan.duration_in_months
            )
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Token Promotion Request"
        verbose_name_plural = "Token Promotion Requests"
