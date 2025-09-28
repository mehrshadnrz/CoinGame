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
    sparkline_in_7d = serializers.DictField(child=serializers.ListField(child=serializers.FloatField()), required=False)
    last_updated = serializers.DateTimeField()

