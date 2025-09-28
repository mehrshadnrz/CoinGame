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


def fetch_geckoterminal_token(
    chain: str, token_address: str, category_name: str = "Gaming"
):
    """
    Fetch a token from GeckoTerminal by chain and contract address.
    Normalizes into CryptoCoin model structure.
    """
    category, _ = Category.objects.get_or_create(name=category_name)
    url = f"{GECKOTERMINAL_BASE_URL}/networks/{chain}/tokens/{token_address}"
    response = requests.get(url)
    if response.status_code != 200:
        logger.warning(
            f"Failed to fetch token {token_address} on {chain}: {response.text}"
        )
        return None

    data = response.json().get("data")
    if not data:
        return None

    attributes = data.get("attributes", {})

    # Normalize to match CryptoCoin fields
    return {
        "coingecko_id": f"{chain}:{token_address}",  # unique identifier
        "rank": None,  # no ranking in GeckoTerminal
        "name": attributes.get("name"),
        "symbol": attributes.get("symbol"),
        "price": attributes.get("price_usd") or 0,
        "percent_change_1h": attributes.get("price_change_percentage", {}).get("m5")
        or 0,
        "percent_change_24h": attributes.get("price_change_percentage", {}).get("h24")
        or 0,
        "percent_change_7d": attributes.get("price_change_percentage", {}).get("d7")
        or 0,
        "market_cap": attributes.get("market_cap_usd") or "0",
        "volume_24h": attributes.get("volume_usd", {}).get("h24") or "0",
        "circulating_supply": attributes.get("circulating_supply") or "N/A",
        "sparkline_in_7d": None,  # GeckoTerminal does not provide sparkline
        "category": category,
    }


def update_geckoterminal_token(chain: str, token_address: str):
    """
    Store/update a GeckoTerminal token in CryptoCoin table.
    """
    token = fetch_geckoterminal_token(chain, token_address)
    if not token:
        return None

    coin, _ = CryptoCoin.objects.update_or_create(
        coingecko_id=token["coingecko_id"],
        defaults={
            "rank": token["rank"],
            "name": token["name"],
            "symbol": token["symbol"].upper(),
            "price": token["price"],
            "percent_change_1h": token["percent_change_1h"],
            "percent_change_24h": token["percent_change_24h"],
            "percent_change_7d": token["percent_change_7d"],
            "market_cap": str(token["market_cap"]),
            "volume_24h": str(token["volume_24h"]),
            "circulating_supply": str(token["circulating_supply"]),
            "sparkline_in_7d": token["sparkline_in_7d"],
            "category": token["category"],
        },
    )
    return coin


def import_coin(user, symbol=None, chain=None, pool_address=None):
    """Import coin and log request in CoinImportRequest."""
    request_log = None
    coin = None

    try:
        if symbol:
            source = "coingecko"
            symbol = symbol.upper()
            coin = CryptoCoin.objects.filter(symbol=symbol).first()

            if not coin:
                data = fetch_top_coin_by_symbol(symbol)
                if not data:
                    raise ValueError("Coin not found in CoinGecko")

                coin = CryptoCoin.objects.create(
                    name=data["name"],
                    symbol=data["symbol"],
                    price=data["price"],
                    market_cap=data["market_cap"],
                    volume_24h=data["volume_24h"],
                    percent_change_1h=data["percent_change_1h"],
                    percent_change_24h=data["percent_change_24h"],
                    percent_change_7d=data["percent_change_7d"],
                )

        elif chain and pool_address:
            source = "geckoterminal"
            coin = CryptoCoin.objects.filter(symbol__iexact=pool_address[:6]).first()

            if not coin:
                data = fetch_geckoterminal_token(chain, pool_address)
                if not data:
                    raise ValueError("Token not found in GeckoTerminal")

                coin = CryptoCoin.objects.create(
                    name=data["name"],
                    symbol=data["symbol"],
                    price=data["price"],
                    market_cap=data["market_cap"],
                    volume_24h=data["volume_24h"],
                    percent_change_1h=data["percent_change_1h"],
                    percent_change_24h=data["percent_change_24h"],
                    percent_change_7d=data["percent_change_7d"],
                )
        else:
            raise ValueError("Invalid parameters")

        request_log = CoinImportRequest.objects.create(
            user=user,
            source=source,
            symbol=symbol,
            chain=chain,
            pool_address=pool_address,
            created_coin=coin,
            status="success",
        )

    except Exception as e:
        request_log = CoinImportRequest.objects.create(
            user=user,
            source="coingecko" if symbol else "geckoterminal",
            symbol=symbol,
            chain=chain,
            pool_address=pool_address,
            created_coin=None,
            status="failed",
        )
        print("Import failed:", e)

    return coin, request_log


def fetch_geckoterminal_coin_detail(chain: str, token_address: str):
    """
    Fetch detailed token info from GeckoTerminal using both
    `/tokens/{address}` and `/tokens/{address}/info`.
    Normalizes into CoinDetailSerializer schema.
    """
    # Base attributes
    base_url = f"{GECKOTERMINAL_BASE_URL}/networks/{chain}/tokens/{token_address}"
    info_url = f"{base_url}/info"

    info_resp = requests.get(info_url)
    info_data = {}

    if info_resp.status_code == 200:
        info_data = info_resp.json().get("data", {}).get("attributes", {})

    base_resp = requests.get(base_url)
    if base_resp.status_code != 200:
        return None

    base_data = base_resp.json().get("data", {})
    attributes = base_data.get("attributes", {})

    return {
        "id": f"{chain}:{token_address}",
        "symbol": attributes.get("symbol"),
        "name": attributes.get("name"),
        "image": {"large": info_data.get("image_url") or attributes.get("image_url")},
        "description": {"en": info_data.get("description", "")},
        "links": {
            "homepage": [info_data.get("website")] if info_data.get("website") else [],
            "discord": info_data.get("discord_url"),
            "telegram": info_data.get("telegram_url"),
            "twitter": f"https://twitter.com/{info_data.get('twitter_handle')}"
            if info_data.get("twitter_handle")
            else None,
        },
        "market_data": {
            "current_price": {"usd": attributes.get("price_usd")},
            "market_cap": {"usd": attributes.get("market_cap_usd")},
            "total_volume": {"usd": attributes.get("volume_usd", {}).get("h24")},
            "price_change_percentage_1h_in_currency": {
                "usd": attributes.get("price_change_percentage", {}).get("m5")
            },
            "price_change_percentage_24h_in_currency": {
                "usd": attributes.get("price_change_percentage", {}).get("h24")
            },
            "price_change_percentage_7d_in_currency": {
                "usd": attributes.get("price_change_percentage", {}).get("d7")
            },
        },
        "tickers": [],
        "community_data": {},
        "developer_data": {},
        "sparkline_in_7d": {"price": []},
        "last_updated": attributes.get("updated_at") or info_data.get("updated_at"),
    }
