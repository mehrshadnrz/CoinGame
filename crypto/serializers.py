from django.utils import timezone
from rest_framework import serializers

from .models import (
    Category,
    CoinRating,
    CoinVote,
    CoinWishlist,
    CryptoCoin,
    MarketStatistics,
    CoinSecurityCheckRequest,
)


class MarketStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketStatistics
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class CryptoCoinSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )

    class Meta:
        model = CryptoCoin
        fields = "__all__"


class CoinDetailSerializer(serializers.Serializer):
    id = serializers.CharField()
    symbol = serializers.CharField()
    name = serializers.CharField()
    image = serializers.DictField(child=serializers.URLField(), required=False)
    description = serializers.DictField(child=serializers.CharField(), required=False)
    links = serializers.DictField(required=False)
    market_data = serializers.DictField(required=False)
    tickers = serializers.ListField(child=serializers.DictField(), required=False)
    community_data = serializers.DictField(required=False)
    developer_data = serializers.DictField(required=False)
    sparkline_in_7d = serializers.DictField(
        child=serializers.ListField(child=serializers.FloatField()), required=False
    )
    last_updated = serializers.DateTimeField()


class CoinVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinVote
        fields = ["id", "coin", "vote", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        user = self.context["request"].user
        coin = data["coin"]
        today = timezone.now().date()

        if CoinVote.objects.filter(
            user=user, coin=coin, created_at__date=today
        ).exists():
            raise serializers.ValidationError(
                "You have already voted today for this coin."
            )
        return data


class CoinRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinRating
        fields = ["id", "coin", "stars", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_stars(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Stars must be between 1 and 5.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        coin = validated_data["coin"]

        # If rating exists, update instead of creating a new one
        rating, created = CoinRating.objects.update_or_create(
            user=user,
            coin=coin,
            defaults={"stars": validated_data["stars"]},
        )
        return rating


class CoinWishlistSerializer(serializers.ModelSerializer):
    coin_detail = serializers.StringRelatedField(source="coin", read_only=True)

    class Meta:
        model = CoinWishlist
        fields = ["id", "coin", "coin_detail", "created_at"]
        read_only_fields = ["id", "created_at", "coin_detail"]

class CoinSecurityCheckRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinSecurityCheckRequest
        fields = [
            "id",
            "user",
            "coin",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
        ]

    def validate(self, data):
        coin = data.get("coin")

        if CoinSecurityCheckRequest.objects.filter(coin=coin).exists():
            raise serializers.ValidationError(
                {"error": "An update request for this coin already exists."}
            )
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        instance = super().create(validated_data)

        coin = instance.coin
        coin.security_badge = False
        coin.save()

        return instance
