from rest_framework import viewsets
from tokens.models import GamingToken, TopToken
from tokens.serializers import GamingTokenSerializer, TopTokenSerializer


class GamingTokenViewSet(viewsets.ModelViewSet):
    queryset = GamingToken.objects.all()
    serializer_class = GamingTokenSerializer


class TopTokenViewSet(viewsets.ModelViewSet):
    queryset = TopToken.objects.all()
    serializer_class = TopTokenSerializer
