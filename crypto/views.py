from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, CoinWishlist, CryptoCoin, MarketStatistics, CoinSecurityCheckRequest
from .serializers import (
    CategorySerializer,
    CoinDetailSerializer,
    CoinRatingSerializer,
    CoinVoteSerializer,
    CoinWishlistSerializer,
    CryptoCoinSerializer,
    MarketStatisticsSerializer,
    CoinSecurityCheckRequestSerializer,
)
from .services import fetch_coin_detail, import_coin
from post.serializers import PostSerializer


class MarketStatisticsView(generics.RetrieveAPIView):
    serializer_class = MarketStatisticsSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return MarketStatistics.objects.first()


class CryptoCoinListView(APIView):
    """
    POST endpoint:
    {
        "category": 1,   # optional
        "page": 1        # optional (default = 1)
    }
    """

    PAGE_SIZE = 50

    def post(self, request, *args, **kwargs):
        category_id = request.data.get("category")
        page = int(request.data.get("page", 1))

        queryset = CryptoCoin.objects.all().order_by("rank")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        total_count = queryset.count()

        # Pagination by slicing
        start = (page - 1) * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        coins = queryset[start:end]

        coins_serializer = CryptoCoinSerializer(coins, many=True)

        categories = Category.objects.all()
        categories_serializer = CategorySerializer(categories, many=True)

        return Response(
            {
                "categories": categories_serializer.data,
                "coins": {
                    "count": total_count,
                    "page": page,
                    "page_size": self.PAGE_SIZE,
                    "results": coins_serializer.data,
                },
            },
            status=status.HTTP_200_OK,
        )


class CoinDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, *args, **kwargs):
        coin_obj = get_object_or_404(CryptoCoin, pk=pk)

        detail = fetch_coin_detail(coin_obj.coingecko_id)
        if detail and hasattr(detail, "to_dict"):
            detail = detail.to_dict()

        if not detail:
            return Response(
                {"detail": "Coin detail not available"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CoinDetailSerializer(detail)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CoinImportView(APIView):
    """
    POST /import-coin/
    {
        "symbol": "BTC"
    }
    """

    def post(self, request):
        user = request.user
        symbol = request.data.get("symbol")
        category = request.data.get("category")

        coin, log = import_coin(
            user,
            symbol=symbol,
            category=category,
        )

        if not coin:
            return Response(
                {
                    "error": "Coin not found",
                    "request_id": log.id if log else None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "coin": CryptoCoinSerializer(coin).data,
                "import_request_id": log.id,
                "status": log.status,
            },
            status=status.HTTP_201_CREATED,
        )


class CryptoCoinViewSet(viewsets.ModelViewSet):
    queryset = CryptoCoin.objects.all()
    serializer_class = CryptoCoinSerializer

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def vote(self, request, pk=None):
        coin = self.get_object()
        serializer = CoinVoteSerializer(
            data={**request.data, "coin": coin.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, coin=coin)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], permission_classes=[permissions.AllowAny])
    def vote_stats(self, request, pk=None):
        coin = self.get_object()
        bullish_count = coin.votes.filter(vote="bullish").count()
        bearish_count = coin.votes.filter(vote="bearish").count()
        return Response({"bullish": bullish_count, "bearish": bearish_count})

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def rate(self, request, pk=None):
        coin = self.get_object()
        user = request.user
        rating_instance = coin.ratings.filter(user=user).first()
        if rating_instance:
            serializer = CoinRatingSerializer(
                rating_instance,
                data={**request.data, "coin": coin.id},
                context={"request": request},
                partial=True,
            )
        else:
            serializer = CoinRatingSerializer(
                data={**request.data, "coin": coin.id},
                context={"request": request},
            )
        serializer.is_valid(raise_exception=True)
        rating = serializer.save(user=user, coin=coin)
        return Response(
            CoinRatingSerializer(rating).data,
            status=status.HTTP_200_OK if rating_instance else status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], permission_classes=[permissions.AllowAny])
    def rating_stats(self, request, pk=None):
        coin = self.get_object()
        ratings = coin.ratings.all()
        count = ratings.count()
        avg = ratings.aggregate(models.Avg("stars"))["stars__avg"] or 0
        try:
            my_rating = coin.ratings.get(user=request.user)
        except Exception:
            my_rating = None
        return Response({"average": round(avg, 2), "count": count, "my_rating": my_rating})


    @action(detail=True, methods=["get"], permission_classes=[permissions.AllowAny])
    def related_posts(self, request, pk=None):
        coin = self.get_object()
        posts = coin.posts.all().order_by("-publish_at")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserWishListViewSet(viewsets.ModelViewSet):
    queryset = CryptoCoin.objects.all()
    serializer_class = CryptoCoinSerializer

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def add_to_wishlist(self, request, pk=None):
        coin = self.get_object()
        wishlist, created = CoinWishlist.objects.get_or_create(
            user=request.user, coin=coin
        )
        if not created:
            return Response(
                {"detail": "Already in wishlist."}, status=status.HTTP_200_OK
            )
        return Response(
            CoinWishlistSerializer(wishlist).data, status=status.HTTP_201_CREATED
        )

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def remove_from_wishlist(self, request, pk=None):
        coin = self.get_object()
        deleted, _ = CoinWishlist.objects.filter(user=request.user, coin=coin).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Not in wishlist."}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def my_wishlist(self, request):
        wishlist = CoinWishlist.objects.filter(user=request.user).select_related("coin")
        serializer = CoinWishlistSerializer(wishlist, many=True)
        return Response(serializer.data)


class TokenUpdateRequestViewSet(viewsets.ModelViewSet):
    queryset = CoinSecurityCheckRequest.objects.all()
    serializer_class = CoinSecurityCheckRequestSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return CoinSecurityCheckRequest.objects.all()
        return CoinSecurityCheckRequest.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
