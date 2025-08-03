from rest_framework import serializers
from post.models import Post


class PostSerializer(serializers.ModelSerializer):
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
        ]
