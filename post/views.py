from rest_framework import viewsets, permissions, decorators, response, status
from .models import Post
from .serializers import PostSerializer
from crypto.models import CryptoCoin


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-publish_at")
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "coin_posts"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @decorators.action(
        detail=False,
        methods=["get"],
        url_path="coin/(?P<coin_id>[^/.]+)",
    )
    def coin_posts(self, request, coin_id=None):
        """
        Returns all posts related to a given coin.
        Example: GET /posts/coin/42/
        """
        try:
            coin = CryptoCoin.objects.get(pk=coin_id)
        except CryptoCoin.DoesNotExist:
            return response.Response(
                {"detail": "Coin not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        posts = Post.objects.filter(coins=coin).order_by("-publish_at")
        serializer = self.get_serializer(posts, many=True)
        return response.Response(serializer.data)
