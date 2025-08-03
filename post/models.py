from django.db import models


class Status(models.TextChoices):
    DRAFT = "Draft"
    PUBLISHED = "Published"


class Post(models.Model):
    title = models.CharField(
        max_length=256,
        blank=False,
        null=False,
        verbose_name="Title",
    )
    description = models.TextField(
        blank=False,
        null=False,
        verbose_name="Description",
    )
    post_image = models.ImageField(
        upload_to="post_images/",
        blank=False,
        null=False,
        verbose_name="Post Image",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Status",
    )
    publish_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Published At",
    )
    read_time = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Read Time",
        help_text="Minute",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
