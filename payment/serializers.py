from rest_framework import serializers
from .models import PaymentIntent

class PaymentIntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentIntent
        fields = "__all__"
        read_only_fields = ("id", "created_at", "status", "tx_hash", "user")

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user
        return super().create(validated_data)
