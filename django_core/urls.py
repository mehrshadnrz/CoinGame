from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("config.urls")),
    path("auth/", include("user.urls")),
    path("api/", include("post.urls")),
    path("api/", include("advertisement.urls")),
    path("api/", include("crypto.urls")),
    path("api/", include("payment.urls")),
    path("api/", include("promotion.urls")),
    # SWAGGER
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
