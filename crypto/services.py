import logging

import requests
from coingecko_sdk import Coingecko
from django.conf import settings

from .models import Category, CoinImportRequest, CryptoCoin

logger = logging.getLogger(__name__)

client = Coingecko(
    demo_api_key=settings.COINGECKO_DEMO_API_KEY,
    environment="demo",
)

GECKOTERMINAL_BASE_URL = "https://api.geckoterminal.com/api/v2"


def fetch_top_coin_by_symbol(symbol: str, category_name: str = "Top"):
    """
    Update coin data using CoinGecko (for major tokens)
    """
    category, _ = Category.objects.get_or_create(name=category_name)
    coin = client.coins.markets.get(
        vs_currency="usd",
        order="rank",
        sparkline=True,
        symbols=symbol,
        price_change_percentage="1h,24h,7d",
    )

    if not coin:
        logger.warning(f"No data found for symbol {symbol} on CoinGecko")
        return

    coin = coin[0]

    return {
        "coingecko_id": coin.id,
        "rank": coin.market_cap_rank,
        "name": coin.name,
        "symbol": coin.symbol.upper(),
        "price": coin.current_price,
        "percent_change_1h": coin.price_change_percentage_1h_in_currency or 0,
        "percent_change_24h": coin.price_change_percentage_24h_in_currency or 0,
        "percent_change_7d": coin.price_change_percentage_7d_in_currency or 0,
        "market_cap": str(coin.market_cap),
        "volume_24h": str(coin.total_volume),
        "circulating_supply": str(coin.circulating_supply),
        "sparkline_in_7d": coin.sparkline_in_7d["price"]
        if coin.sparkline_in_7d
        else None,
        "category": category,
    }


def fetch_top_coins(limit=1000, vs_currency="usd"):
    """Fetch top coins from CoinGecko (unchanged)"""
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
    """Update top coins from CoinGecko (unchanged)"""
    coins = fetch_top_coins(limit=limit, vs_currency=vs_currency)
    category, _ = Category.objects.get_or_create(name="Top")

    for coin in coins:
        CryptoCoin.objects.update_or_create(
            coingecko_id=coin.id,
            defaults={
                "rank": coin.market_cap_rank,
                "name": coin.name,
                "symbol": coin.symbol.upper(),
                "price": coin.current_price,
                "percent_change_1h": coin.price_change_percentage_1h_in_currency or 0,
                "percent_change_24h": coin.price_change_percentage_24h_in_currency or 0,
                "percent_change_7d": coin.price_change_percentage_7d_in_currency or 0,
                "market_cap": str(coin.market_cap),
                "volume_24h": str(coin.total_volume),
                "circulating_supply": str(coin.circulating_supply),
                "sparkline_in_7d": coin.sparkline_in_7d["price"]
                if coin.sparkline_in_7d
                else None,
                "category": category,
            },
        )


def fetch_coin_detail(coin_id: str):
    """
    Fetch detailed info for a coin by its CoinGecko ID (unchanged)
    """
    return client.coins.get_id(
        id=coin_id,
        localization=True,
        tickers=True,
        market_data=True,
        community_data=True,
        developer_data=True,
        sparkline=True,
    )


def import_coin(
    user,
    symbol,
    category="Top",
):
    try:
        symbol = symbol.upper()
        coin = CryptoCoin.objects.filter(symbol=symbol).first()

        if not coin:
            data = fetch_top_coin_by_symbol(symbol=symbol, category_name=category)
            if not data:
                raise ValueError("Coin not found in CoinGecko")

            print(data, "\n\n\n\n")

            coin = CryptoCoin.objects.create(
                coingecko_id=data["coingecko_id"],
                rank=data["rank"],
                name=data["name"],
                symbol=data["symbol"],
                price=data["price"],
                market_cap=data["market_cap"],
                volume_24h=data["volume_24h"],
                percent_change_1h=data["percent_change_1h"],
                percent_change_24h=data["percent_change_24h"],
                percent_change_7d=data["percent_change_7d"],
                sparkline_in_7d=data["sparkline_in_7d"],
                circulating_supply=data["circulating_supply"],
                category=data["category"]
            )

        request_log = CoinImportRequest.objects.create(
            user=user,
            symbol=symbol,
            created_coin=coin,
            status="success",
        )

    except Exception as e:
        request_log = CoinImportRequest.objects.create(
            user=user,
            symbol=symbol,
            created_coin=None,
            status="failed",
        )
        print("Import failed:", e)

    return coin, request_log
