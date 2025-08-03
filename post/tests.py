import os
import shutil
import tempfile
from io import BytesIO
from PIL import Image

from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework import status

from post.models import Post, Status


def generate_test_image():
    image = Image.new("RGB", (100, 100), color="blue")
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return SimpleUploadedFile("test.jpg", buffer.getvalue(), content_type="image/jpeg")


class PostAPITestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._temp_media = tempfile.mkdtemp()
        cls.override = override_settings(MEDIA_ROOT=cls._temp_media)
        cls.override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.override.disable()
        shutil.rmtree(cls._temp_media, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.post_data = {
            "title": "Test Post",
            "description": "This is a test post.",
            "status": Status.PUBLISHED,
            "publish_at": timezone.now(),
            "post_image": generate_test_image(),
            "read_time": 1,
        }

    def test_create_post(self):
        response = self.client.post("/api/posts/", self.post_data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.first().title, "Test Post")

    def test_get_post_list(self):
        Post.objects.create(**self.post_data)
        response = self.client.get("/api/posts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_post(self):
        post = Post.objects.create(**self.post_data)
        url = f"/api/posts/{post.id}/"
        updated_data = {
            "title": "Updated Title",
            "description": "Updated Description",
            "status": Status.DRAFT,
            "publish_at": timezone.now(),
            "post_image": generate_test_image(),
        }
        response = self.client.put(url, updated_data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, "Updated Title")

    def test_delete_post(self):
        post = Post.objects.create(**self.post_data)
        url = f"/api/posts/{post.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=post.id).exists())
