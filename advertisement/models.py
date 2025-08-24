from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class AdvertisementPlan(models.Model):
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
    cost_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        blank=False,
        verbose_name=_("Cost (USD)"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.duration_in_months} months / ${self.cost_usd})"


class Advertisement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="advertisements",
        verbose_name="User",
    )
    plan = models.ForeignKey(
        AdvertisementPlan,
        on_delete=models.CASCADE,
        related_name="ads",
        null=False,
        blank=False,
        verbose_name=_("Advertisement Plan"),
    )
    banner_image = models.ImageField(
        upload_to="ads/banners/",
        verbose_name=_("Banner Image"),
        null=False,
        blank=False,
    )
    wide_banner_image = models.ImageField(
        upload_to="ads/wide_banners/",
        verbose_name=_("Wide Banner Image"),
        null=False,
        blank=False,
    )
    banner_link = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Banner Link"),
    )
    wide_banner_link = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Wide Banner Link"),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
    )
    has_payment = models.BooleanField(default=False, verbose_name=_("Has payment"))
    display_ad = models.BooleanField(
        default=False, verbose_name=_("Selected for Display")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True, editable=False)

    @property
    def is_active(self):
        return self.expires_at is None or self.expires_at > now()

    def save(self, *args, **kwargs):
        if not self.expires_at and self.plan:
            self.expires_at = (self.created_at or now()) + timedelta(
                days=30 * self.plan.duration_in_months
            )

        if self.display_ad:
            Advertisement.objects.exclude(pk=self.pk).update(display_ad=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ad #{self.id} ({self.plan.name})"
