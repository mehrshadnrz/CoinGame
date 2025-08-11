from django.test import TestCase
from django.db.utils import IntegrityError
from tokens.models import GamingToken, TopToken, TopTokenTypes


class GamingTokenModelTest(TestCase):
    def test_gaming_token_creation(self):
        token = GamingToken.objects.create(
            name="GameCoin",
            symbol="GCN",
            promoted=True,
            security_badge=True,
            trading_view_symbol="GCNUSD",
            network="Ethereum",
            pool_address="0xpooladdressgame",
        )
        self.assertEqual(token.name, "GameCoin")
        self.assertEqual(token.symbol, "GCN")
        self.assertEqual(str(token), "GameCoin (GCN)")

    def test_unique_symbol_constraint(self):
        GamingToken.objects.create(
            name="TokenA",
            symbol="TKA",
            promoted=False,
            security_badge=False,
            trading_view_symbol="TKAUSD",
            network="BSC",
            pool_address="0xpoolA",
        )
        with self.assertRaises(IntegrityError):
            GamingToken.objects.create(
                name="TokenB",
                symbol="TKA",  # duplicate
                promoted=False,
                security_badge=False,
                trading_view_symbol="TKBUSD",
                network="Polygon",
                pool_address="0xpoolB",
            )

    def test_optional_fields_can_be_null(self):
        token = GamingToken.objects.create(
            name="OptionalToken",
            symbol="OPT",
            promoted=False,
            security_badge=False,
            trading_view_symbol="OPTUSD",
            network="Solana",
            pool_address="0xpoolopt",
            base_token=None,
            quote_token=None,
            about_token=None,
        )
        self.assertIsNone(token.base_token)
        self.assertIsNone(token.about_token)


class TopTokenModelTest(TestCase):
    def test_top_token_creation(self):
        token = TopToken.objects.create(
            name="TopCoin",
            symbol="TPC",
            promoted=False,
            security_badge=True,
            trading_view_symbol="TPCUSD",
            binance_symbol="TOPCOINUSDT",
            token_type=TopTokenTypes.TOP_TOKEN,
            coingecko_id="topcoin",
        )
        self.assertEqual(token.name, "TopCoin")
        self.assertEqual(token.token_type, TopTokenTypes.TOP_TOKEN)
        self.assertEqual(str(token), "TopCoin (TPC)")
