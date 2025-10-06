from django.contrib import admin
from .models import SiteConfig, AboutUs, ContactMessage

@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteConfig.objects.exists()

@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not AboutUs.objects.exists()

admin.site.register(ContactMessage)
