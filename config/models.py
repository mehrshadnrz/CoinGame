from django.db import models


class SiteConfig(models.Model):
    payment_token_address = models.TextField(blank=True, null=True)
    recipient_address = models.TextField(blank=True, null=True)

    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    telegram_url = models.URLField(blank=True, null=True)
    discord_url = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk and SiteConfig.objects.exists():
            raise Exception("Only one SiteConfig instance allowed.")
        return super().save(*args, **kwargs)

    def __str__(self):
        return "Site Configuration"


class AboutUs(models.Model):
    header = models.TextField(
        blank=False,
        null=False,
    )
    body = models.TextField(
        blank=True,
        null=True,
    )
    picture = models.ImageField(
        upload_to="about_us_image/",
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        if not self.pk and AboutUs.objects.exists():
            raise Exception("Only one AboutUs instance allowed.")
        return super().save(*args, **kwargs)

    def __str__(self):
        return "About Us"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ‒ {self.subject or 'No Subject'}"

