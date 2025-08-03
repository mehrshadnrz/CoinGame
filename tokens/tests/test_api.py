from django.contrib.auth import get_user_model
from django.db import utils
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tokens.models import GamingToken, TokenTypes, TokenUpdateRequest, TopToken

User = get_user_model()


class GamingTokenAPITest(APITestCase):
    def setUp(self):
        self.token_data = {
            "name": "MyGameToken",
            "symbol": "MGT",
            "promoted": True,
            "security_badge": False,
            "trading_view_symbol": "MGTUSD",
            "network": "Ethereum",
            "pool_address": "0x123456789",
        }
        self.url = "/api/gaming-tokens/"

    def test_create_gaming_token(self):
        response = self.client.post(self.url, self.token_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GamingToken.objects.count(), 1)
        self.assertEqual(GamingToken.objects.first().name, "MyGameToken")

    def test_get_gaming_tokens_list(self):
        GamingToken.objects.create(**self.token_data)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_single_gaming_token(self):
        token = GamingToken.objects.create(**self.token_data)
        response = self.client.get(f"{self.url}{token.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["symbol"], "MGT")

    def test_update_gaming_token(self):
        token = GamingToken.objects.create(**self.token_data)
        updated_data = self.token_data.copy()
        updated_data["name"] = "UpdatedGameToken"
        response = self.client.put(
            f"{self.url}{token.id}/",
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "UpdatedGameToken")

    def test_delete_gaming_token(self):
        token = GamingToken.objects.create(**self.token_data)
        response = self.client.delete(f"{self.url}{token.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(GamingToken.objects.count(), 0)


class TopTokenAPITest(APITestCase):
    def setUp(self):
        self.token_data = {
            "name": "TopCoin",
            "symbol": "TPC",
            "promoted": True,
            "security_badge": True,
            "trading_view_symbol": "TPCUSD",
            "binance_symbol": "TOPCOINUSDT",
            "token_type": TokenTypes.TOP_TOKEN,
            "coingecko_id": "topcoin",
        }
        self.url = "/api/top-tokens/"

    def test_create_top_token(self):
        response = self.client.post(self.url, self.token_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TopToken.objects.count(), 1)
        self.assertEqual(TopToken.objects.first().symbol, "TPC")

    def test_get_top_token_list(self):
        TopToken.objects.create(**self.token_data)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_single_top_token(self):
        token = TopToken.objects.create(**self.token_data)
        response = self.client.get(f"{self.url}{token.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["coingecko_id"], "topcoin")

    def test_update_gaming_token(self):
        token = TopToken.objects.create(**self.token_data)
        updated_data = self.token_data.copy()
        updated_data["name"] = "UpdatedTopCoin"
        response = self.client.put(
            f"{self.url}{token.id}/",
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "UpdatedTopCoin")

    def test_delete_gaming_token(self):
        token = TopToken.objects.create(**self.token_data)
        response = self.client.delete(f"{self.url}{token.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(GamingToken.objects.count(), 0)


class TokenUpdateRequestTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1",
            password="password",
            is_staff=False,
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="password",
            is_staff=False,
        )
        self.admin = User.objects.create_user(
            username="admin",
            password="adminpass",
            is_staff=True,
        )

        self.top_token1 = TopToken.objects.create(
            name="Top1",
            symbol="TOP1",
            trading_view_symbol="TOP1USD",
            binance_symbol="TOP1USDT",
            coingecko_id="top1",
            token_type="TOP_TOKEN",
            security_badge=True,
        )

        self.top_token2 = TopToken.objects.create(
            name="Top2",
            symbol="TOP2",
            trading_view_symbol="TOP2USD",
            binance_symbol="TOP2USDT",
            coingecko_id="top2",
            token_type="TOP_TOKEN",
            security_badge=True,
        )

        self.gaming_token1 = GamingToken.objects.create(
            name="Game1",
            symbol="GAME1",
            trading_view_symbol="GAME1USD",
            network="Ethereum",
            pool_address="0x123",
            security_badge=True,
        )

        self.gaming_token2 = GamingToken.objects.create(
            name="Game2",
            symbol="GAME2",
            trading_view_symbol="GAME2USD",
            network="Polygon",
            pool_address="0x456",
            security_badge=True,
        )

        self.list_url = reverse("token-update-request-list")
        self.accept_url_name = "token-update-request-accept"

    def _get_detail_url(self, pk):
        return reverse("token-update-request-detail", args=[pk])

    def _get_accept_url(self, pk):
        return reverse(self.accept_url_name, args=[pk])

    def test_user_create_request_valid_top_token(self):
        """Authenticated user can create request with top token"""
        self.client.force_authenticate(user=self.user1)
        data = {"top_token": self.top_token1.id}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.top_token1.refresh_from_db()
        self.assertFalse(self.top_token1.security_badge)

    def test_user_create_request_valid_gaming_token(self):
        """Authenticated user can create request with gaming token"""
        self.client.force_authenticate(user=self.user1)
        data = {"gaming_token": self.gaming_token1.id}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.gaming_token1.refresh_from_db()
        self.assertFalse(self.gaming_token1.security_badge)

    def test_user_cannot_create_request_with_both_tokens(self):
        """Validation error when both tokens are provided"""
        self.client.force_authenticate(user=self.user1)
        data = {"top_token": self.top_token1.id, "gaming_token": self.gaming_token1.id}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Exactly one", response.data["non_field_errors"][0])

    def test_user_cannot_create_request_without_token(self):
        """Validation error when no token is provided"""
        self.client.force_authenticate(user=self.user1)
        data = {}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Exactly one", response.data["non_field_errors"][0])

    def test_duplicate_token_request_prevention(self):
        """Prevent duplicate requests for same token"""
        self.client.force_authenticate(user=self.user1)
        data1 = {"top_token": self.top_token1.id}
        
        response1 = self.client.post(self.list_url, data1)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        response2 = self.client.post(self.list_url, data1)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("top_token", response2.data)
        self.assertEqual(
            response2.data["top_token"][0],
            "An update request for this token already exists."
        )
        
        self.client.force_authenticate(user=self.user2)
        response3 = self.client.post(self.list_url, data1)
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("top_token", response3.data)
        self.assertEqual(
            response3.data["top_token"][0],
            "An update request for this token already exists."
        )

    def test_user_sees_only_own_requests(self):
        """Users should only see their own requests"""
        self.client.force_authenticate(user=self.user1)
        data = {"top_token": self.top_token1.id}
        self.client.post(self.list_url, data)

        self.client.force_authenticate(user=self.user2)
        data = {"gaming_token": self.gaming_token1.id}
        self.client.post(self.list_url, data)

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user"], self.user1.id)

    def test_admin_sees_all_requests(self):
        """Admin should see all requests"""
        self.client.force_authenticate(user=self.user1)
        self.client.post(self.list_url, {"top_token": self.top_token1.id})

        self.client.force_authenticate(user=self.user2)
        self.client.post(self.list_url, {"gaming_token": self.gaming_token1.id})

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_regular_user_cannot_delete_request(self):
        """Non-admin users cannot delete requests"""
        self.client.force_authenticate(user=self.user1)
        data = {"top_token": self.top_token1.id}
        response = self.client.post(self.list_url, data)
        request_id = response.data["id"]

        detail_url = self._get_detail_url(request_id)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_any_request(self):
        """Admin can delete any request"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.list_url, {"top_token": self.top_token1.id})
        request_id = response.data["id"]

        self.client.force_authenticate(user=self.admin)
        detail_url = self._get_detail_url(request_id)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_accept_request_as_admin(self):
        """Admin can accept requests and update token"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            self.list_url, {"gaming_token": self.gaming_token1.id}
        )
        request_id = response.data["id"]

        self.client.force_authenticate(user=self.admin)
        accept_url = self._get_accept_url(request_id)
        response = self.client.post(accept_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "Token update accepted")

        self.gaming_token1.refresh_from_db()
        self.assertTrue(self.gaming_token1.security_badge)

        with self.assertRaises(TokenUpdateRequest.DoesNotExist):
            TokenUpdateRequest.objects.get(id=request_id)

    def test_non_admin_cannot_accept_request(self):
        """Regular users cannot accept requests"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.list_url, {"top_token": self.top_token1.id})
        request_id = response.data["id"]

        accept_url = self._get_accept_url(request_id)
        response = self.client.post(accept_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user2)
        response = self.client.post(accept_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_invalid_request(self):
        """Handling invalid accept requests"""
        self.client.force_authenticate(user=self.admin)

        accept_url = self._get_accept_url(9999)
        response = self.client.post(accept_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_security_badge_workflow(self):
        """Full security badge lifecycle test"""
        self.assertTrue(self.top_token1.security_badge)

        self.client.force_authenticate(user=self.user1)
        self.client.post(self.list_url, {"top_token": self.top_token1.id})
        self.top_token1.refresh_from_db()
        self.assertFalse(self.top_token1.security_badge)

        request = TokenUpdateRequest.objects.get(top_token=self.top_token1)
        self.client.force_authenticate(user=self.admin)
        self.client.post(self._get_accept_url(request.id))
        self.top_token1.refresh_from_db()
        self.assertTrue(self.top_token1.security_badge)
