import os
import shutil
import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from advertisement.models import Advertisement, AdvertisementPlan
from post.models import Post, Status

User = get_user_model()


def generate_test_image():
    image = Image.new("RGB", (100, 100), color="blue")
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return SimpleUploadedFile("test.jpg", buffer.getvalue(), content_type="image/jpeg")


class AdvertisementTests(APITestCase):
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
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="adminpass"
        )
        self.user = User.objects.create_user(
            username="user", email="user@test.com", password="userpass"
        )
        self.plan = AdvertisementPlan.objects.create(
            name="Basic", duration_in_months=1, cost_usd=100
        )

    def auth_client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def test_admin_can_create_plan(self):
        client = self.auth_client(self.admin)
        res = client.post(
            "/api/ad-plans/",
            {"name": "Premium", "duration_in_months": 6, "cost_usd": "500.00"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AdvertisementPlan.objects.count(), 2)

    def test_user_cannot_create_plan(self):
        client = self.auth_client(self.user)
        res = client.post(
            "/api/ad-plans/",
            {"name": "Premium", "duration_in_months": 6, "cost_usd": "500.00"},
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_create_advertisement(self):
        client = self.auth_client(self.user)
        res = client.post(
            "/api/ads/",
            {
                "plan": self.plan.id,
                "banner_image": generate_test_image(),
                "wide_banner_image": generate_test_image(),
                "banner_link": "http://example.com",
                "wide_banner_link": "http://example.com/wide",
                "description": "My first ad",
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        ad = Advertisement.objects.get()
        self.assertEqual(ad.user, self.user)

    def test_user_can_only_list_own_ads(self):
        other_user = User.objects.create_user("other", "other@test.com", "pass")
        Advertisement.objects.create(
            user=other_user,
            plan=self.plan,
            banner_image=generate_test_image(),
            wide_banner_image=generate_test_image(),
        )
        ad2 = Advertisement.objects.create(
            user=self.user,
            plan=self.plan,
            banner_image=generate_test_image(),
            wide_banner_image=generate_test_image(),
        )
        client = self.auth_client(self.user)
        res = client.get("/api/ads/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], ad2.id)

    def test_user_cannot_update_after_payment(self):
        ad = Advertisement.objects.create(
            user=self.user,
            plan=self.plan,
            banner_image=generate_test_image(),
            wide_banner_image=generate_test_image(),
            has_payment=True,
        )
        client = self.auth_client(self.user)
        res = client.patch(
            f"/api/ads/{ad.id}/",
            {"description": "New description"},
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_set_payment(self):
        ad = Advertisement.objects.create(
            user=self.user,
            plan=self.plan,
            banner_image=generate_test_image(),
            wide_banner_image=generate_test_image(),
        )
        client = self.auth_client(self.admin)
        res = client.post(
            f"/api/ads/{ad.id}/set_payment/",
            {"has_payment": True},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ad.refresh_from_db()
        self.assertTrue(ad.has_payment)

    def test_only_one_ad_can_be_displayed(self):
        ad1 = Advertisement.objects.create(
            user=self.user,
            plan=self.plan,
            banner_image=generate_test_image(),
            wide_banner_image=generate_test_image(),
        )
        ad2 = Advertisement.objects.create(
            user=self.user,
            plan=self.plan,
            banner_image=generate_test_image(),
            wide_banner_image=generate_test_image(),
        )
        client = self.auth_client(self.admin)
        res1 = client.post(
            f"/api/ads/{ad1.id}/set_display/",
            {"display_ad": True},
            format="json",
        )
        res2 = client.post(
            f"/api/ads/{ad2.id}/set_display/",
            {"display_ad": True},
            format="json",
        )
        ad1.refresh_from_db()
        ad2.refresh_from_db()
        self.assertFalse(ad1.display_ad)
        self.assertTrue(ad2.display_ad)
