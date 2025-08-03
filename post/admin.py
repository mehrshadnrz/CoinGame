from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "status",
        "publish_at",
        "read_time",
    ]
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    search_fields = ["title"]
    list_filter = ["status"]
    ordering = ["-publish_at"]
