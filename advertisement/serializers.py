from rest_framework import serializers

from advertisement.models import Advertisement, AdvertisementPlan


class AdvertisementPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvertisementPlan
        fields = "__all__"


class AdvertisementSerializer(serializers.ModelSerializer):
    plan_detail = AdvertisementPlanSerializer(source="plan", read_only=True)
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = Advertisement
        fields = "__all__"
        read_only_fields = [
            "user",
            "has_payment",
            "display_ad",
            "expires_at",
            "created_at",
            "is_active",
        ]
