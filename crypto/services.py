import time

from coingecko_sdk import Coingecko
from django.conf import settings
from django.utils.dateparse import parse_datetime

from .models import Category, CryptoCoins, MarketStatistics

client = Coingecko(
    demo_api_key=settings.COINGECKO_DEMO_API_KEY,
    environment="demo",
)


def update_market_coins():
    data = client.coins.markets.get(
        vs_currency="usd",
        order="market_cap_desc",
        sparkline=True,
        price_change_percentage="1h,24h,7d",
    )
    return data


def fetch_top_coins(limit=1000, vs_currency="usd"):
    all_coins = []
    per_page = 250
    for page in range(1, (limit // per_page) + 1):
        data = client.coins.markets.get(
            vs_currency=vs_currency,
            order="market_cap_desc",
            per_page=per_page,
            page=page,
            sparkline=True,
            price_change_percentage="1h,24h,7d",
        )
        if not data:
            break
        all_coins.extend(data)
    return all_coins[:limit]


def update_top_coins(limit=1000, vs_currency="usd"):
    coins = fetch_top_coins(limit=limit, vs_currency=vs_currency)

    category, _ = Category.objects.get_or_create(name="Top")

    for coin in coins:
        CryptoCoins.objects.update_or_create(
            symbol=coin.symbol.upper(),  # <-- dot notation
            defaults={
                "rank": coin.market_cap_rank,
                "name": coin.name,
                "price": coin.current_price,
                "percent_change_1h": coin.price_change_percentage_1h_in_currency or 0,
                "percent_change_24h": coin.price_change_percentage_24h_in_currency or 0,
                "percent_change_7d": coin.price_change_percentage_7d_in_currency or 0,
                "market_cap": str(coin.market_cap),
                "volume_24h": str(coin.total_volume),
                "circulating_supply": str(coin.circulating_supply),
                "sparkline_in_7d": coin.sparkline_in_7d["price"] if coin.sparkline_in_7d else None,
                "category": category,
            },
        )


# def update_market_statistics():
#     """Update MarketStatistics model with global data from CoinGecko."""
#     data = client.global_.get()

#     stats, created = MarketStatistics.objects.get_or_create(pk=1)
#     stats.cryptos = str(data["data"].get("active_cryptocurrencies"))
#     stats.exchanges = data["data"].get("markets")
#     stats.market_cap = str(data["data"]["total_market_cap"].get("usd"))
#     stats.market_cap_percent = str(data["data"]["market_cap_percentage"].get("btc"))
#     stats.vol_24h = str(data["data"]["total_volume"].get("usd"))
#     stats.vol_24h_percent = "N/A"
#     stats.dominance = str(data["data"]["market_cap_percentage"].get("btc"))
#     stats.fear_and_greed = "N/A"
#     stats.save()
