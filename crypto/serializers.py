from rest_framework import serializers

from .models import Category, CryptoCoins, MarketStatistics


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
        model = CryptoCoins
        fields = "__all__"
