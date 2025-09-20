from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, CryptoCoins, MarketStatistics
from .serializers import (
    CategorySerializer,
    CryptoCoinSerializer,
    MarketStatisticsSerializer,
)


class MarketStatisticsView(generics.RetrieveAPIView):
    serializer_class = MarketStatisticsSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return MarketStatistics.objects.first()


# class CryptoCoinListView(APIView):
#     """
#     POST endpoint:
#     {
#         "category": 1   # optional
#     }
#     Response includes paginated coins + categories
#     """

#     def post(self, request, *args, **kwargs):
#         category_id = request.data.get("category")

#         queryset = CryptoCoins.objects.all()
#         if category_id:
#             queryset = queryset.filter(category_id=category_id)

#         paginator = PageNumberPagination()
#         paginator.page_size = 50
#         page = paginator.paginate_queryset(queryset, request)
#         coins_serializer = CryptoCoinSerializer(page, many=True)

#         categories = Category.objects.all()
#         categories_serializer = CategorySerializer(categories, many=True)

#         return Response(
#             {
#                 "categories": categories_serializer.data,
#                 "coins": {
#                     "count": paginator.page.paginator.count,
#                     "next": paginator.get_next_link(),
#                     "previous": paginator.get_previous_link(),
#                     "results": coins_serializer.data,
#                 },
#             }
#         )


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

        queryset = CryptoCoins.objects.all()
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

        return Response({
            "categories": categories_serializer.data,
            "coins": {
                "count": total_count,
                "page": page,
                "page_size": self.PAGE_SIZE,
                "results": coins_serializer.data,
            }
        }, status=status.HTTP_200_OK)
