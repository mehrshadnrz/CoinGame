from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("tokens.urls")),
    path("auth/", include("user.urls")),
    path("api/", include("post.urls")),
    path("api/", include("advertisement.urls")),
]
