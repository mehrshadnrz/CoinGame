from django.conf import settings
from django.db import models
from django.utils import timezone
from uuid import uuid4

class PaymentIntent(models.Model):
    STATUS_CHOICES = (("pending", "pending"), ("paid", "paid"), ("expired", "expired"))
    SERVICE_CHOICES = (("ads", "ads"), ("promotion", "promotion"))

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment_intents",
    )
    plan_id = models.PositiveIntegerField()
    plan_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # blockchain info
    merchant_address = models.CharField(max_length=256)
    token_address = models.CharField(max_length=256, blank=True, null=True)
    token_symbol = models.CharField(max_length=64, blank=True, null=True)

    nonce = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    tx_hash = models.CharField(max_length=100, blank=True, null=True)

    def is_expired(self):
        return timezone.now() > self.expires_at
