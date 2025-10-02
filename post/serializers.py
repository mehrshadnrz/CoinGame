from rest_framework import serializers
from post.models import Post
from crypto.models import CryptoCoin


class CoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoCoin
        fields = ["id", "name", "symbol", "price", "rank"]


class PostSerializer(serializers.ModelSerializer):
    coins = CoinSerializer(many=True, read_only=True)
    coin_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CryptoCoin.objects.all(),
        source="coins",
        write_only=True
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "description",
            "status",
            "post_image",
            "publish_at",
            "read_time",
            "created_at",
            "updated_at",
            "coins",
            "coin_ids",
        ]
