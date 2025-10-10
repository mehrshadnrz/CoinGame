# services.py
import logging
from typing import Dict, Any, List, Optional

import requests
from django.conf import settings

from .models import Category, CryptoCoin

logger = logging.getLogger(__name__)

CMC_BASE = "https://pro-api.coinmarketcap.com/v1"
SESSION = requests.Session()
SESSION.headers.update({
    "X-CMC_PRO_API_KEY": settings.CMC_PRO_API_KEY,
    "Accept": "application/json",
})

def _cmc_get(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{CMC_BASE}{path}"
    r = SESSION.get(url, params=params, timeout=20)
    try:
        r.raise_for_status()
    except Exception:
        logger.exception("CMC error %s %s -> %s", path, params, r.text[:500])
        raise
    return r.json()

# ---------- MAPPERS ----------

def _map_listing_item(item: Dict[str, Any], quote_symbol: str = "USD") -> Dict[str, Any]:
    q = item["quote"][quote_symbol]
    return {
        "cmc_id": item["id"],
        "slug": item.get("slug"),
        "rank": item.get("cmc_rank"),
        "name": item.get("name"),
        "symbol": item.get("symbol", "").upper(),
        "price": q.get("price", 0) or 0,
        "percent_change_1h": q.get("percent_change_1h") or 0,
        "percent_change_24h": q.get("percent_change_24h") or 0,
        "percent_change_7d": q.get("percent_change_7d") or 0,
        "market_cap": str(q.get("market_cap") or 0),
        "volume_24h": str(q.get("volume_24h") or 0),
        "circulating_supply": str(item.get("circulating_supply") or 0),
        "sparkline_in_7d": None,  # Optional: fill using OHLCV/Historical if your tier allows
    }

def _map_quote_item(info: Dict[str, Any], quote_symbol: str = "USD") -> Dict[str, Any]:
    # info is from /cryptocurrency/quotes/latest for one coin
    q = info["quote"][quote_symbol]
    return {
        "cmc_id": info["id"],
        "slug": info.get("slug"),
        "rank": info.get("cmc_rank"),
        "name": info.get("name"),
        "symbol": info.get("symbol", "").upper(),
        "price": q.get("price", 0) or 0,
        "percent_change_1h": q.get("percent_change_1h") or 0,
        "percent_change_24h": q.get("percent_change_24h") or 0,
        "percent_change_7d": q.get("percent_change_7d") or 0,
        "market_cap": str(q.get("market_cap") or 0),
        "volume_24h": str(q.get("volume_24h") or 0),
        "circulating_supply": str(info.get("circulating_supply") or 0),
        "sparkline_in_7d": None,
    }

# ---------- PUBLIC FUNCTIONS (same names you already use) ----------

def fetch_top_coin_by_symbol(symbol: str, category_name: str = "Top"):
    """
    Replace CoinGecko lookups with CMC's /quotes/latest (best for a single symbol),
    falling back to /listings/latest symbol match.
    """
    symbol = symbol.upper()
    quote = getattr(settings, "CMC_DEFAULT_FIAT", "USD")

    # first try quotes/latest by symbol
    try:
        data = _cmc_get(
            "/cryptocurrency/quotes/latest",
            {"symbol": symbol, "convert": quote}
        )
        item = list(data["data"].values())[0]  # e.g. {"BTC": {...}}
    except Exception:
        # fallback: listings/latest first page scan
        lst = _cmc_get(
            "/cryptocurrency/listings/latest",
            {"start": 1, "limit": 500, "convert": quote, "sort": "market_cap"}
        )
        candidates = [i for i in lst.get("data", []) if i.get("symbol", "").upper() == symbol]
        if not candidates:
            logger.warning("CMC: no data for symbol=%s", symbol)
            return None
        item = candidates[0]

    category, _ = Category.objects.get_or_create(name=category_name)
    mapped = _map_quote_item(item, quote_symbol=quote) if "quote" in item and symbol in (item.get("symbol") or "") else _map_listing_item(item, quote_symbol=quote)
    mapped["category"] = category
    return mapped


def fetch_top_coins(limit=1000, vs_currency="usd"):
    """
    Use /listings/latest with pagination (250/page like before).
    """
    quote = (vs_currency or "usd").upper()
    per_page = 250
    results: List[Dict[str, Any]] = []
    start = 1
    while len(results) < limit:
        page_limit = min(per_page, limit - len(results))
        payload = _cmc_get(
            "/cryptocurrency/listings/latest",
            {"start": start, "limit": page_limit, "convert": quote, "sort": "market_cap"}
        )
        batch = [_map_listing_item(it, quote_symbol=quote) for it in payload.get("data", [])]
        if not batch:
            break
        results.extend(batch)
        start += page_limit
    return results[:limit]


def update_top_coins(limit=1000, vs_currency="usd"):
    coins = fetch_top_coins(limit=limit, vs_currency=vs_currency)
    category, _ = Category.objects.get_or_create(name="Top")

    for c in coins:
        # Prefer cmc_id when present; fall back to symbol
        lookup_kwargs = {"cmc_id": c.get("cmc_id")} if c.get("cmc_id") else {"symbol": c["symbol"]}
        defaults = {
            "rank": c["rank"],
            "name": c["name"],
            "symbol": c["symbol"],
            "price": c["price"],
            "percent_change_1h": c["percent_change_1h"],
            "percent_change_24h": c["percent_change_24h"],
            "percent_change_7d": c["percent_change_7d"],
            "market_cap": c["market_cap"],
            "volume_24h": c["volume_24h"],
            "circulating_supply": c["circulating_supply"],
            "sparkline_in_7d": c["sparkline_in_7d"],
            "category": category,
            "slug": c.get("slug"),
        }
        CryptoCoin.objects.update_or_create(**lookup_kwargs, defaults=defaults)


def fetch_coin_detail(coin_id: str):
    """
    Previously: CoinGecko coins.get_id(...)
    With CMC: combine /info and /quotes/latest by id or by symbol.
    Here we accept CMC numeric ID *or* symbol string.
    """
    quote = getattr(settings, "CMC_DEFAULT_FIAT", "USD")

    # Decide if `coin_id` is numeric CMC id or a symbol
    is_numeric = str(coin_id).isdigit()
    key = "id" if is_numeric else "symbol"
    # /info
    info = _cmc_get("/cryptocurrency/info", {key: coin_id})
    info_data = list(info.get("data", {}).values())[0]

    # /quotes/latest
    quotes = _cmc_get("/cryptocurrency/quotes/latest", {key: coin_id, "convert": quote})
    quotes_data = list(quotes.get("data", {}).values())[0]

    # Build a dict close to your CoinDetailSerializer schema
    return {
        "id": str(info_data["id"]),
        "symbol": info_data["symbol"],
        "name": info_data["name"],
        "image": {"large": info_data.get("logo")},
        "description": {"en": (info_data.get("description") or "")},
        "links": {
            "website": info_data.get("urls", {}).get("website", []),
            "source_code": info_data.get("urls", {}).get("source_code", []),
            "twitter": info_data.get("urls", {}).get("twitter", []),
            "reddit": info_data.get("urls", {}).get("reddit", []),
            "message_board": info_data.get("urls", {}).get("message_board", []),
            "chat": info_data.get("urls", {}).get("chat", []),
        },
        "market_data": {
            "current_price": {quote: quotes_data["quote"][quote]["price"]},
            "market_cap": {quote: quotes_data["quote"][quote]["market_cap"]},
            "price_change_percentage_1h_in_currency": {quote: quotes_data["quote"][quote]["percent_change_1h"]},
            "price_change_percentage_24h_in_currency": {quote: quotes_data["quote"][quote]["percent_change_24h"]},
            "price_change_percentage_7d_in_currency": {quote: quotes_data["quote"][quote]["percent_change_7d"]},
            "total_volume": {quote: quotes_data["quote"][quote]["volume_24h"]},
            "circulating_supply": quotes_data.get("circulating_supply"),
        },
        "tickers": [],  # CMC exposes market pairs via /market-pairs/latest if/when you need it
        "community_data": {},
        "developer_data": {},
        "sparkline_in_7d": {},  # fill from OHLCV if you enable it
        "last_updated": quotes_data["last_updated"],
    }


def import_coin(user, symbol, category="Top", trading_view_name=None):
    try:
        symbol = (symbol or "").upper().strip()
        coin = CryptoCoin.objects.filter(symbol=symbol).first()

        if not coin:
            data = fetch_top_coin_by_symbol(symbol=symbol, category_name=category)
            if not data:
                raise ValueError("Coin not found in CoinMarketCap")

            coin = CryptoCoin.objects.create(
                cmc_id=data.get("cmc_id"),
                slug=data.get("slug"),
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
                category=data["category"],
                trading_view_name=trading_view_name,
            )
        # log
        from .models import CoinImportRequest
        request_log = CoinImportRequest.objects.create(
            user=user, symbol=symbol, created_coin=coin, status="success"
        )
        return coin, request_log

    except Exception as e:
        from .models import CoinImportRequest
        request_log = CoinImportRequest.objects.create(
            user=user, symbol=symbol or None, created_coin=None, status="failed"
        )
        logger.exception("CMC import failed: %s", e)
        return None, request_log
