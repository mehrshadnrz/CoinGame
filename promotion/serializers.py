from rest_framework import serializers
from promotion.models import TokenPromotionPlan, TokenPromotionRequest


class TokenPromotionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenPromotionPlan
        fields = [
            "id",
            "name",
            "duration_in_months",
            "cost",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class TokenPromotionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenPromotionRequest
        fields = [
            "id",
            "user",
            "plan",
            "coin",
            "has_payment",
            "expires_at",
            "created_at",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "user",
            "expires_at",
            "created_at",
            "is_active",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user
        return super().create(validated_data)
