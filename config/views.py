# configs/views.py
from rest_framework import generics, permissions

from .models import ContactMessage, SiteConfig, AboutUs
from .serializers import (
    ContactMessageSerializer,
    SiteConfigSerializer,
    AboutUsSerializer,
)


class SiteConfigView(generics.RetrieveAPIView):
    """
    Public endpoint to fetch site configs.
    Always returns the single row.
    """

    serializer_class = SiteConfigSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return SiteConfig.objects.first()


class AboutUsView(generics.RetrieveAPIView):
    serializer_class = AboutUsSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return AboutUs.objects.first()


class SiteConfigUpdateView(generics.UpdateAPIView):
    serializer_class = SiteConfigSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        return SiteConfig.objects.first()


class ContactMessageCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]
