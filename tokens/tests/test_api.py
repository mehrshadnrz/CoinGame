from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from tokens.models import (
    GamingToken,
    ListingStatus,
    TokenKind,
    TokenListingRequest,
    TokenPromotionPlan,
    TokenPromotionRequest,
    TokenUpdateRequest,
    TopToken,
    TopTokenTypes,
)

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
            "token_type": TopTokenTypes.TOP_TOKEN,
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
            "An update request for this token already exists.",
        )

        self.client.force_authenticate(user=self.user2)
        response3 = self.client.post(self.list_url, data1)
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("top_token", response3.data)
        self.assertEqual(
            response3.data["top_token"][0],
            "An update request for this token already exists.",
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


class TokenListingRequestTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="password", is_staff=False
        )
        self.user2 = User.objects.create_user(
            username="user2", password="password", is_staff=False
        )
        self.admin = User.objects.create_user(
            username="admin", password="adminpass", is_staff=True
        )

        # some existing production tokens to test duplicate prevention
        TopToken.objects.create(
            name="ExistingTop",
            symbol="EXTOP",
            trading_view_symbol="EXTOPUSD",
            binance_symbol="EXTOPUSDT",
            coingecko_id="existingtop",
            token_type=TokenKind.TOP_TOKEN,
            security_badge=False,
        )

        GamingToken.objects.create(
            name="ExistingGame",
            symbol="EXG",
            trading_view_symbol="EXGUSD",
            network="Ethereum",
            pool_address="0xabc",
            security_badge=False,
        )

        self.list_url = reverse("token-listing-request-list")

    def _detail_url(self, pk):
        return reverse("token-listing-request-detail", args=[pk])

    def _approve_url(self, pk):
        return reverse("token-listing-request-approve", args=[pk])

    def _reject_url(self, pk):
        return reverse("token-listing-request-reject", args=[pk])

    def test_create_top_listing_request_success(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            "kind": TokenKind.TOP_TOKEN,
            "name": "NewTop",
            "symbol": "NEWTP",
            "trading_view_symbol": "NEWTPUSD",
            "network": "Ethereum",
            "binance_symbol": "NEWTPUSDT",
            "token_type": "TOP_TOKEN",
            "coingecko_id": "newtop",
        }
        resp = self.client.post(self.list_url, payload, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TokenListingRequest.objects.filter(symbol="NEWTP").count(), 1)
        req = TokenListingRequest.objects.get(symbol="NEWTP")
        self.assertEqual(req.user, self.user1)
        self.assertEqual(req.status, ListingStatus.PENDING)

    def test_create_gaming_listing_request_success(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            "kind": TokenKind.GAMING_TOKEN,
            "name": "NewGame",
            "symbol": "NEWG",
            "trading_view_symbol": "NEWGUSD",
            "network": "Polygon",
            "pool_address": "0xdeadbeef",
        }
        resp = self.client.post(self.list_url, payload, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TokenListingRequest.objects.filter(symbol="NEWG").count(), 1)
        req = TokenListingRequest.objects.get(symbol="NEWG")
        self.assertEqual(req.user, self.user1)
        self.assertEqual(req.status, ListingStatus.PENDING)

    def test_create_fails_if_missing_kind_specific_fields(self):
        self.client.force_authenticate(user=self.user1)
        # Missing coingecko/binance/token_type for top
        payload_top = {
            "kind": TokenKind.TOP_TOKEN if hasattr(TokenKind, "TOP_TOKEN") else "top",
            "name": "BadTop",
            "symbol": "BADTP",
            "trading_view_symbol": "BADTPUSD",
            "network": "Ethereum",
            "token_type": "TOP_TOKEN",
            "coingecko_id": "newtop",
            # missing binance_symbol
        }
        resp_top = self.client.post(self.list_url, payload_top, format="multipart")
        self.assertEqual(resp_top.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("binance_symbol", resp_top.data)

        payload_top = {
            "kind": TokenKind.TOP_TOKEN if hasattr(TokenKind, "TOP_TOKEN") else "top",
            "name": "BadTop",
            "symbol": "BADTP",
            "trading_view_symbol": "BADTPUSD",
            "network": "Ethereum",
            "binance_symbol": "NEWTPUSDT",
            "coingecko_id": "newtop",
            # missing token_type
        }
        resp_top = self.client.post(self.list_url, payload_top, format="multipart")
        self.assertEqual(resp_top.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("token_type", resp_top.data)

        payload_top = {
            "kind": TokenKind.TOP_TOKEN if hasattr(TokenKind, "TOP_TOKEN") else "top",
            "name": "BadTop",
            "symbol": "BADTP",
            "trading_view_symbol": "BADTPUSD",
            "network": "Ethereum",
            "binance_symbol": "NEWTPUSDT",
            "token_type": "TOP_TOKEN",
            # missing coingecko_id
        }
        resp_top = self.client.post(self.list_url, payload_top, format="multipart")
        self.assertEqual(resp_top.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("coingecko_id", resp_top.data)

        # Missing pool_address/network for gaming
        payload_game = {
            "kind": TokenKind.GAMING_TOKEN,
            "name": "BadGame",
            "symbol": "BADG",
            "trading_view_symbol": "BADGUSD",
            "network": "Polygon",
            # missing pool_address
        }
        resp_game = self.client.post(self.list_url, payload_game, format="multipart")
        self.assertEqual(resp_game.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("pool_address", resp_game.data)

        payload_game = {
            "kind": TokenKind.GAMING_TOKEN,
            "name": "BadGame",
            "symbol": "BADG",
            "trading_view_symbol": "BADGUSD",
            "pool_address": "0xdeadbeef",
            # missing network
        }
        resp_game = self.client.post(self.list_url, payload_game, format="multipart")
        self.assertEqual(resp_game.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("network", resp_game.data)

    def test_cannot_request_symbol_existing_in_production(self):
        # EXTOP already exists as TopToken in setUp
        self.client.force_authenticate(user=self.user1)
        payload = {
            "kind": TokenKind.TOP_TOKEN if hasattr(TokenKind, "TOP_TOKEN") else "top",
            "name": "SomeTop",
            "symbol": "EXTOP",  # existing production symbol
            "trading_view_symbol": "EXTOPUSD",
            "network": "Ethereum",
            "binance_symbol": "SOMETPUSDT",
            "token_type": "TOP_TOKEN",
            "coingecko_id": "sometop",
        }
        resp = self.client.post(self.list_url, payload, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("symbol", resp.data)

    def test_duplicate_listing_request_prevention(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            "kind": TokenKind.GAMING_TOKEN,
            "name": "DupGame",
            "symbol": "DUPG",
            "trading_view_symbol": "DUPGUSD",
            "network": "Polygon",
            "pool_address": "0x111",
        }
        resp1 = self.client.post(self.list_url, payload, format="multipart")
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        # Another attempt with same symbol should fail (unique=True on symbol)
        resp2 = self.client.post(self.list_url, payload, format="multipart")
        self.assertIn(
            resp2.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT)
        )

    def test_user_can_update_own_pending_request(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            "kind": TokenKind.GAMING_TOKEN,
            "name": "EditableGame",
            "symbol": "EDG",
            "trading_view_symbol": "EDGUSD",
            "network": "Polygon",
            "pool_address": "0x222",
        }
        create = self.client.post(self.list_url, payload, format="multipart")
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        req_id = create.data["id"]

        detail = self._detail_url(req_id)
        update_payload = payload.copy()
        update_payload["name"] = "EditedGame"
        resp = self.client.put(detail, update_payload, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "EditedGame")

    def test_user_cannot_update_others_request(self):
        # user1 creates
        self.client.force_authenticate(user=self.user1)
        payload = {
            "kind": TokenKind.GAMING_TOKEN,
            "name": "OtherGame",
            "symbol": "OTG",
            "trading_view_symbol": "OTGUSD",
            "network": "Polygon",
            "pool_address": "0x333",
        }
        create = self.client.post(self.list_url, payload, format="multipart")
        req_id = create.data["id"]

        # user2 tries to update
        self.client.force_authenticate(user=self.user2)
        detail = self._detail_url(req_id)
        update_payload = payload.copy()
        update_payload["name"] = "Hacked"
        resp = self.client.put(detail, update_payload, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_update_non_pending(self):
        # create and have admin approve it
        self.client.force_authenticate(user=self.user1)
        payload = {
            "kind": TokenKind.GAMING_TOKEN,
            "name": "ToApprove",
            "symbol": "TAP",
            "trading_view_symbol": "TAPUSD",
            "network": "Polygon",
            "pool_address": "0x444",
        }
        create = self.client.post(self.list_url, payload, format="multipart")
        req_id = create.data["id"]

        # admin approve
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(self._approve_url(req_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # original user tries to update -> should be 400 (not allowed because not pending)
        self.client.force_authenticate(user=self.user1)
        detail = self._detail_url(req_id)
        update_payload = payload.copy()
        update_payload["name"] = "ShouldFail"
        resp2 = self.client.put(detail, update_payload, format="multipart")
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_cannot_update_or_delete(self):
        # user1 creates a request
        self.client.force_authenticate(user=self.user1)
        payload = {
            "kind": TokenKind.TOP_TOKEN,
            "name": "AdminTry",
            "symbol": "ADMTRY",
            "trading_view_symbol": "ADMTRYUSD",
            "network": "Ethereum",
            "binance_symbol": "ADMTRYUSDT",
            "token_type": "TOP_TOKEN",
            "coingecko_id": "admtry",
        }
        create = self.client.post(self.list_url, payload, format="multipart")
        req_id = create.data["id"]

        # admin attempts update
        self.client.force_authenticate(user=self.admin)
        detail = self._detail_url(req_id)
        update_payload = payload.copy()
        update_payload["name"] = "AdminEdited"
        resp = self.client.put(detail, update_payload, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # admin attempts delete
        resp2 = self.client.delete(detail)
        self.assertEqual(resp2.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_approve_creates_production_token(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            "kind": TokenKind.TOP_TOKEN,
            "name": "MakeRealTop",
            "symbol": "MRTOP",
            "trading_view_symbol": "MRTOPUSD",
            "network": "Ethereum",
            "binance_symbol": "MRTOPUSDT",
            "token_type": "TOP_TOKEN",
            "coingecko_id": "mrtop",
        }
        create = self.client.post(self.list_url, payload, format="multipart")
        req_id = create.data["id"]

        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(self._approve_url(req_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # check token created
        self.assertTrue(TopToken.objects.filter(symbol="MRTOP").exists())
        req = TokenListingRequest.objects.get(id=req_id)
        self.assertEqual(req.status, ListingStatus.APPROVED)
        self.assertEqual(req.processed_by, self.admin)

    def test_admin_reject_marks_rejected_and_no_token_created(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            "kind": TokenKind.GAMING_TOKEN,
            "name": "RejectMe",
            "symbol": "REJ1",
            "trading_view_symbol": "REJ1USD",
            "network": "Polygon",
            "pool_address": "0x555",
        }
        create = self.client.post(self.list_url, payload, format="multipart")
        req_id = create.data["id"]

        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(
            self._reject_url(req_id), data={"admin_note": "spam"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        req = TokenListingRequest.objects.get(id=req_id)
        self.assertEqual(req.status, ListingStatus.REJECTED)
        self.assertEqual(req.processed_by, self.admin)
        self.assertFalse(GamingToken.objects.filter(symbol="REJ1").exists())


class TokenPromotionRequestTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass")
        self.user2 = User.objects.create_user(username="user2", password="pass2")
        self.admin = User.objects.create_user(
            username="admin", password="adminpass", is_staff=True
        )

        self.plan = TokenPromotionPlan.objects.create(
            name="Basic", duration_in_months=1, cost_usd=100
        )

        self.top_token = TopToken.objects.create(
            name="TopPromo",
            symbol="TPR",
            trading_view_symbol="TPRUSD",
            binance_symbol="TPRUSDT",
            coingecko_id="tpr",
            token_type=TopTokenTypes.TOP_TOKEN,
            promoted=False,
        )

        self.gaming_token = GamingToken.objects.create(
            name="GamePromo",
            symbol="GPR",
            trading_view_symbol="GPRUSD",
            network="Ethereum",
            pool_address="0xpromo",
            promoted=False,
        )

        self.list_url = reverse("promotion-request-list")

    def _detail_url(self, pk):
        return reverse("promotion-request-detail", args=[pk])

    def _activate_url(self, pk):
        return reverse("promotion-request-activate", args=[pk])

    def _deactivate_url(self, pk):
        return reverse("promotion-request-deactivate", args=[pk])

    def _mark_paid_url(self, pk):
        return reverse("promotion-request-mark-paid", args=[pk])

    # ---------- Creation & validation ----------

    def test_create_promotion_request_top_token_success(self):
        self.client.force_authenticate(user=self.user1)
        payload = {"plan": self.plan.id, "top_token": self.top_token.id}
        resp = self.client.post(self.list_url, payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        req = TokenPromotionRequest.objects.get(id=resp.data["id"])
        self.assertEqual(req.user, self.user1)
        self.assertIsNotNone(req.expires_at)
        self.assertFalse(req.is_active)
        self.top_token.refresh_from_db()
        self.assertFalse(self.top_token.promoted)

    def test_create_promotion_request_gaming_token_success(self):
        self.client.force_authenticate(user=self.user1)
        payload = {"plan": self.plan.id, "gaming_token": self.gaming_token.id}
        resp = self.client.post(self.list_url, payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TokenPromotionRequest.objects.count(), 1)

    def test_create_requires_plan(self):
        self.client.force_authenticate(user=self.user1)
        payload = {"top_token": self.top_token.id}
        resp = self.client.post(self.list_url, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("plan", resp.data)

    def test_user_cannot_create_request_with_both_tokens(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            "plan": self.plan.id,
            "top_token": self.top_token.id,
            "gaming_token": self.gaming_token.id,
        }
        resp = self.client.post(self.list_url, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", resp.data)

    def test_user_cannot_create_request_without_any_token(self):
        self.client.force_authenticate(user=self.user1)
        payload = {"plan": self.plan.id}
        resp = self.client.post(self.list_url, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", resp.data)

    # ---------- Visibility ----------

    def test_user_sees_only_own_requests(self):
        self.client.force_authenticate(user=self.user1)
        self.client.post(
            self.list_url, {"plan": self.plan.id, "top_token": self.top_token.id}
        )

        self.client.force_authenticate(user=self.user2)
        self.client.post(
            self.list_url, {"plan": self.plan.id, "gaming_token": self.gaming_token.id}
        )

        self.client.force_authenticate(user=self.user1)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Only user1's request
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["user"], self.user1.id)

    def test_admin_sees_all_requests(self):
        self.client.force_authenticate(user=self.user1)
        self.client.post(
            self.list_url, {"plan": self.plan.id, "top_token": self.top_token.id}
        )
        self.client.force_authenticate(user=self.user2)
        self.client.post(
            self.list_url, {"plan": self.plan.id, "gaming_token": self.gaming_token.id}
        )

        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    # ---------- Admin actions ----------

    def test_admin_can_activate_then_deactivate(self):
        # create request
        self.client.force_authenticate(user=self.user1)
        r = self.client.post(
            self.list_url, {"plan": self.plan.id, "top_token": self.top_token.id}
        )
        req_id = r.data["id"]

        # activate
        self.client.force_authenticate(user=self.admin)
        a = self.client.post(self._activate_url(req_id))
        self.assertEqual(a.status_code, status.HTTP_200_OK)
        self.top_token.refresh_from_db()
        self.assertTrue(self.top_token.promoted)

        # deactivate
        d = self.client.post(self._deactivate_url(req_id))
        self.assertEqual(d.status_code, status.HTTP_200_OK)
        self.top_token.refresh_from_db()
        self.assertFalse(self.top_token.promoted)

    def test_non_admin_cannot_activate_deactivate_or_mark_paid(self):
        self.client.force_authenticate(user=self.user1)
        r = self.client.post(
            self.list_url, {"plan": self.plan.id, "gaming_token": self.gaming_token.id}
        )
        req_id = r.data["id"]

        self.client.force_authenticate(user=self.user1)
        self.assertEqual(
            self.client.post(self._activate_url(req_id)).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.post(self._deactivate_url(req_id)).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.post(self._mark_paid_url(req_id)).status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_admin_mark_paid_idempotent(self):
        self.client.force_authenticate(user=self.user1)
        r = self.client.post(
            self.list_url, {"plan": self.plan.id, "top_token": self.top_token.id}
        )
        req_id = r.data["id"]

        self.client.force_authenticate(user=self.admin)
        first = self.client.post(self._mark_paid_url(req_id))
        self.assertEqual(first.status_code, status.HTTP_200_OK)

        second = self.client.post(self._mark_paid_url(req_id))
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", second.data)

    # ---------- Deletion behavior ----------

    def test_user_delete_active_request_first_deactivates_token(self):
        """
        If the request is 'active' and the token was promoted via activation,
        deleting the request should leave token.unpromoted (view should deactivate before delete).
        """
        # create + activate
        self.client.force_authenticate(user=self.user1)
        r = self.client.post(
            self.list_url, {"plan": self.plan.id, "top_token": self.top_token.id}
        )
        req_id = r.data["id"]

        self.client.force_authenticate(user=self.admin)
        self.client.post(self._activate_url(req_id))
        self.top_token.refresh_from_db()
        self.assertTrue(self.top_token.promoted)

        # delete by owner
        self.client.force_authenticate(user=self.user1)
        d = self.client.delete(self._detail_url(req_id))
        self.assertEqual(d.status_code, status.HTTP_204_NO_CONTENT)

        # token should no longer be promoted, request gone
        self.top_token.refresh_from_db()
        self.assertFalse(self.top_token.promoted)
        self.assertFalse(TokenPromotionRequest.objects.filter(id=req_id).exists())
