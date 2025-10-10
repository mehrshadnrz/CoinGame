from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import (
    MarketSnapshot, Top20IndexPoint, FearGreedReading,
    AltseasonReading, AverageRsiReading
)
from .serializers import (
    MarketSnapshotSerializer, Top20IndexPointSerializer, FearGreedSerializer,
    AltseasonSerializer, AverageRsiSerializer
)
from .services import update_dashboard

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

CACHE_1M  = 60
CACHE_5M  = 300
CACHE_15M = 900


@extend_schema(tags=["Boxes"], summary="Force refresh boxes", request=None,
               examples=[OpenApiExample("Refresh (light)", value={"compute_heavy": False})])
class DashboardUpdateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        heavy = bool(request.data.get("compute_heavy", False))
        data = update_dashboard(compute_heavy=heavy)
        return Response({"ok": True, "updated": list(data.keys())})


@extend_schema(tags=["Boxes"], summary="Global Market box (latest)")
@method_decorator(cache_page(CACHE_1M), name="get")
class MarketCapView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        obj = MarketSnapshot.objects.first()
        if not obj:
            return Response({"detail": "No data"}, status=status.HTTP_404_NOT_FOUND)
        return Response(MarketSnapshotSerializer(obj).data)


@extend_schema(
    tags=["Boxes"], summary="CMC20 (Top-20 index)",
    parameters=[OpenApiParameter(name="limit", description="Sparkline points (latest first)", required=False, type=int)]
)
@method_decorator(cache_page(CACHE_1M), name="get")
class CMC20View(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get("limit", 120))
        latest = Top20IndexPoint.objects.first()
        points = Top20IndexPoint.objects.all()[:limit]
        return Response({
            "latest": Top20IndexPointSerializer(latest).data if latest else None,
            "sparkline": Top20IndexPointSerializer(points, many=True).data,
        })


@extend_schema(tags=["Boxes"], summary="Fear & Greed (latest)")
@method_decorator(cache_page(CACHE_5M), name="get")
class FearGreedView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        obj = FearGreedReading.objects.first()
        if not obj:
            return Response({"detail": "No data"}, status=status.HTTP_404_NOT_FOUND)
        return Response(FearGreedSerializer(obj).data)


@extend_schema(tags=["Boxes"], summary="Altcoin Season (last computed)")
@method_decorator(cache_page(CACHE_15M), name="get")
class AltseasonView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        obj = AltseasonReading.objects.first()
        if not obj:
            return Response({"detail": "No data"}, status=status.HTTP_404_NOT_FOUND)
        return Response(AltseasonSerializer(obj).data)


@extend_schema(tags=["Boxes"], summary="Average Crypto RSI (last computed)")
@method_decorator(cache_page(CACHE_15M), name="get")
class AverageRsiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        obj = AverageRsiReading.objects.first()
        if not obj:
            return Response({"detail": "No data"}, status=status.HTTP_404_NOT_FOUND)
        return Response(AverageRsiSerializer(obj).data)


@extend_schema(tags=["Boxes"], summary="All boxes (aggregated)")
@method_decorator(cache_page(CACHE_1M), name="get")
class DashboardAggregateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        res = {}
        ms  = MarketSnapshot.objects.first()
        t20 = Top20IndexPoint.objects.first()
        fg  = FearGreedReading.objects.first()
        alt = AltseasonReading.objects.first()
        rsi = AverageRsiReading.objects.first()

        res["market_cap"]     = MarketSnapshotSerializer(ms).data if ms else None
        res["cmc20"]          = Top20IndexPointSerializer(t20).data if t20 else None
        res["fear_greed"]     = FearGreedSerializer(fg).data if fg else None
        res["altcoin_season"] = AltseasonSerializer(alt).data if alt else None
        res["average_rsi"]    = AverageRsiSerializer(rsi).data if rsi else None

        return Response(res)
