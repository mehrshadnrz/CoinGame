from rest_framework import serializers

from .models import CryptoCoins, MarketStatistics


class MarketStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketStatistics
        fields = "__all__"


class CryptoCoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoCoins
        fields = "__all__"
