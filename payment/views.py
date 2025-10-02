from uuid import uuid4
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import PaymentIntent
from .serializers import PaymentIntentSerializer
from advertisement.models import AdvertisementPlan, Advertisement
from promotion.models import TokenPromotionPlan, TokenPromotionRequest
from config.models import SiteConfig
from .utils import verify_bsc_tx, get_token_info


class PaymentIntentViewSet(viewsets.GenericViewSet):
    serializer_class = PaymentIntentSerializer
    queryset = PaymentIntent.objects.all()

    def get_queryset(self):
        return PaymentIntent.objects.filter(user=self.request.user).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def create_intent(self, request):
        user = request.user
        plan_id = request.data.get("plan_id")
        plan_type = request.data.get("plan_type")

        if not plan_id or not plan_type:
            return Response({"detail": "plan_id and plan_type required"}, status=400)

        try:
            if plan_type == "ads":
                plan = AdvertisementPlan.objects.get(pk=plan_id)
            elif plan_type == "promotion":
                plan = TokenPromotionPlan.objects.get(pk=plan_id)
            else:
                return Response({"detail": "invalid plan_type"}, status=400)
        except (AdvertisementPlan.DoesNotExist, TokenPromotionPlan.DoesNotExist):
            return Response({"detail": "plan not found"}, status=404)

        config = SiteConfig.objects.filter().first()
        merchant_address = config.recipient_address
        if not merchant_address:
            return Response({"detail": "merchant address not configured"}, status=500)

        token_info = get_token_info(config.payment_token_address)

        intent = PaymentIntent.objects.create(
            user=user,
            plan_id=plan.id,
            plan_type=plan_type,
            amount=plan.cost,
            token_address=config.payment_token_address,
            token_symbol=token_info.get("symbol", None),
            merchant_address=merchant_address,
            nonce=uuid4().hex,
            expires_at=timezone.now() + timedelta(minutes=30),
        )

        serializer = self.get_serializer(intent)
        return Response(serializer.data, status=201)

    @action(detail=False, methods=["post"])
    def verify(self, request):
        """
        Called by frontend with {"intent_id": "...", "tx_hash": "...", "ad_id"?: "...", "promotion_id"?: "..."}
        """
        config = SiteConfig.objects.filter().first()
        merchant_address = config.recipient_address
        if not merchant_address:
            return Response({"detail": "merchant address not configured"}, status=500)

        token_info = get_token_info(config.payment_token_address)

        intent_id = request.data.get("intent_id")
        tx_hash = request.data.get("tx_hash")

        if not intent_id or not tx_hash:
            return Response({"detail": "intent_id and tx_hash required"}, status=400)

        try:
            intent = PaymentIntent.objects.get(pk=intent_id, user=request.user)
        except PaymentIntent.DoesNotExist:
            return Response({"detail": "intent not found"}, status=404)

        if intent.is_expired():
            intent.status = "expired"
            intent.save()
            return Response({"detail": "intent expired"}, status=400)

        # verify transaction on-chain
        info = verify_bsc_tx(tx_hash=tx_hash)

        if not info.get("ok", None):
            return Response(
                {"detail": "transaction not valid", "reason": info}, status=400
            )
        if (
            info.get("symbol", None) == token_info.get("symbol", None)
            or info.get("to", None) == merchant_address
            or info.get("amount", None) == intent.amount
        ):
            return Response(
                {"detail": "transaction not valid", "reason": info}, status=400
            )

        # mark intent paid
        intent.status = "paid"
        intent.tx_hash = tx_hash
        intent.save()

        # extend ad or promotion
        if intent.plan_type == "ads":
            ad_id = request.data.get("ad_id")
            if not ad_id:
                return Response({"detail": "ad_id required"}, status=400)
            plan = AdvertisementPlan.objects.get(pk=intent.plan_id)
            ad = Advertisement.objects.get(pk=ad_id, user=request.user)
            ad.expires_at = timezone.now() + timedelta(
                days=30 * plan.duration_in_months
            )
            ad.has_payment = True
            ad.save()
            return Response({"detail": "payment verified", "ad_id": ad.id})

        elif intent.plan_type == "promotion":
            promotion_id = request.data.get("promotion_id")
            if not promotion_id:
                return Response({"detail": "promotion_id required"}, status=400)
            plan = TokenPromotionPlan.objects.get(pk=intent.plan_id)
            promo = TokenPromotionRequest.objects.get(
                pk=promotion_id, user=request.user
            )
            promo.expires_at = timezone.now() + timedelta(
                days=30 * plan.duration_in_months
            )
            promo.has_payment = True
            promo.is_active = True
            promo.save()
            return Response({"detail": "payment verified", "promotion_id": promo.id})

        return Response({"detail": "unknown plan_type"}, status=400)
