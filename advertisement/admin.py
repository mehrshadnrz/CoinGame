from django.contrib import admin
from advertisement.models import Advertisement, AdvertisementPlan


@admin.register(AdvertisementPlan)
class AdvertisementPlanAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "duration_in_months", "cost_usd", "created_at")
    search_fields = ("name",)
    list_filter = ("duration_in_months",)


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ("id", "plan", "banner_link", "wide_banner_link", "created_at")
    search_fields = ("description",)
    list_filter = ("plan", "created_at")
