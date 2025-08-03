from rest_framework.test import APITestCase
from rest_framework import status
from tokens.models import GamingToken, TopToken, TokenTypes


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
        response = self.client.put(f"{self.url}{token.id}/", updated_data, format="json")
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
        response = self.client.put(f"{self.url}{token.id}/", updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "UpdatedTopCoin")

    def test_delete_gaming_token(self):
        token = TopToken.objects.create(**self.token_data)
        response = self.client.delete(f"{self.url}{token.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(GamingToken.objects.count(), 0)