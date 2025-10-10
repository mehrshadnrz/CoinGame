from rest_framework import serializers
from .models import (
    MarketSnapshot, Top20IndexPoint, FearGreedReading,
    AltseasonReading, AverageRsiReading
)


class MarketSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketSnapshot
        fields = [
            "fetched_at","source_ts","market_cap","market_cap_pct_24h",
            "vol_24h","vol_24h_pct_24h","active_cryptos","active_exchanges",
            "active_market_pairs","btc_dominance","eth_dominance",
        ]


class Top20IndexPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Top20IndexPoint
        fields = ["ts", "index_value", "pct_change_24h"]


class FearGreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = FearGreedReading
        fields = ["ts", "value", "classification"]


class AltseasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AltseasonReading
        fields = ["ts", "percentage", "is_altseason"]


class AverageRsiSerializer(serializers.ModelSerializer):
    class Meta:
        model = AverageRsiReading
        fields = ["ts", "avg_rsi"]
