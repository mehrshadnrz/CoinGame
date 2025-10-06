from django.urls import path

from .views import (
    ContactMessageCreateView,
    SiteConfigUpdateView,
    SiteConfigView,
    AboutUsView,
)

urlpatterns = [
    path("config/", SiteConfigView.as_view(), name="site-config"),
    path("about_us/", AboutUsView.as_view(), name="about-us"),
    path("config/update/", SiteConfigUpdateView.as_view(), name="site-config-update"),
    path("contact/", ContactMessageCreateView.as_view(), name="contact-message"),
]
