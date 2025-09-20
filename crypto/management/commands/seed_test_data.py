from django.core.management.base import BaseCommand
from crypto.models import MarketStatistics, CryptoCoins
from config.models import SiteConfig


class Command(BaseCommand):
    help = "Seed database with test data for MarketStatistics, CryptoCoins, and SiteConfig"

    def handle(self, *args, **options):
        # Create MarketStatistics (only one allowed)
        if not MarketStatistics.objects.exists():
            MarketStatistics.objects.create(
                cryptos="25000",
                exchanges=500,
                market_cap="2.8T",
                market_cap_percent="100%",
                vol_24h="150B",
                vol_24h_percent="10%",
                dominance="BTC 55%, ETH 20%",
                fear_and_greed="55/100",
            )
            self.stdout.write(self.style.SUCCESS("✅ MarketStatistics created."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ MarketStatistics already exists, skipped."))

        # Create SiteConfig (only one allowed)
        if not SiteConfig.objects.exists():
            SiteConfig.objects.create(
                about_us="We are a test crypto exchange site.",
                contact_email="support@testcrypto.com",
                contact_phone="09123456789",
                address="123 Blockchain Street, Cryptoville",
                facebook_url="https://facebook.com/testcrypto",
                twitter_url="https://twitter.com/testcrypto",
                instagram_url="https://instagram.com/testcrypto",
                telegram_url="https://t.me/testcrypto",
                discord_url="https://discord.gg/testcrypto",
            )
            self.stdout.write(self.style.SUCCESS("✅ SiteConfig created."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ SiteConfig already exists, skipped."))

        # Create some CryptoCoins
        if not CryptoCoins.objects.exists():
            coins = [
                {
                    "rank": 1,
                    "name": "Bitcoin",
                    "symbol": "BTC",
                    "price": 114381.80,
                    "percent_change_1h": 0.37,
                    "percent_change_24h": 0.48,
                    "percent_change_7d": 3.57,
                    "market_cap": "2.28T",
                    "volume_24h": "58.22B",
                    "circulating_supply": "19.9M BTC",
                    "category": "top",
                },
                {
                    "rank": 2,
                    "name": "Ethereum",
                    "symbol": "ETH",
                    "price": 3643.97,
                    "percent_change_1h": 0.31,
                    "percent_change_24h": 0.78,
                    "percent_change_7d": 5.05,
                    "market_cap": "439.63B",
                    "volume_24h": "33.83B",
                    "circulating_supply": "120.7M ETH",
                    "category": "top",
                },
                {
                    "rank": 3,
                    "name": "Axie Infinity",
                    "symbol": "AXS",
                    "price": 6.21,
                    "percent_change_1h": -0.12,
                    "percent_change_24h": 1.45,
                    "percent_change_7d": -3.21,
                    "market_cap": "900M",
                    "volume_24h": "120M",
                    "circulating_supply": "150M AXS",
                    "category": "gaming",
                },
            ]
            for coin in coins:
                CryptoCoins.objects.create(**coin)

            self.stdout.write(self.style.SUCCESS("✅ CryptoCoins created."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ CryptoCoins already exist, skipped."))
