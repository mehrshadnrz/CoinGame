from django.urls import path

from .views import (
    ContactMessageCreateView,
    SiteConfigUpdateView,
    SiteConfigView,
)

urlpatterns = [
    path("config/", SiteConfigView.as_view(), name="site-config"),
    path("config/update/", SiteConfigUpdateView.as_view(), name="site-config-update"),
    path('contact/', ContactMessageCreateView.as_view(), name='contact-message'),
]
