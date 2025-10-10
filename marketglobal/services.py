import time
import json
import logging
from requests import RequestException
import datetime as dt
from decimal import Decimal, getcontext
from typing import Dict, List, Tuple

import requests
from django.conf import settings
from django.db import transaction

from .models import (
    MarketSnapshot,
    Top20IndexPoint,
    FearGreedReading,
    AltseasonReading,
    AverageRsiReading,
)

getcontext().prec = 28

CMC_BASE = getattr(settings, "CMC_API_BASE", "https://pro-api.coinmarketcap.com")
HEADERS = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": settings.CMC_PRO_API_KEY}
STABLE_TICKERS = set(getattr(settings, "MARKETGLOBAL_STABLE_TICKERS", set()))

logger = logging.getLogger(__name__)


def _cmc_get(path: str, params: Dict = None) -> Dict:
    backoffs = [0, 0.5, 1.0, 2.0]
    last = None
    for s in backoffs:
        if s:
            time.sleep(s)
        try:
            r = requests.get(f"{CMC_BASE}{path}", headers=HEADERS, params=params or {}, timeout=25)
            try:
                payload = r.json()
            except Exception:
                r.raise_for_status()
                raise
            status = payload.get("status", {})
            raw_code = status.get("error_code", 0)
            try:
                err_code = int(raw_code)
            except (TypeError, ValueError):
                err_code = 0
            if err_code not in (None, 0):
                msg = status.get("error_message") or ""
                raise RequestException(f"CMC error {err_code}: {msg}")
            r.raise_for_status()
            return payload.get("data", payload)
        except RequestException as e:
            last = e
            raw = None
            try:
                raw = r.text[:500]
            except Exception: pass
            logger.warning("CMC GET %s failed: %s | raw=%s", path, e, raw)
    raise last


# --------- Global Metrics ---------

def fetch_global_metrics() -> Dict:
    data = _cmc_get("/v1/global-metrics/quotes/latest")
    q = data["quote"]["USD"]
    return {
        "source_ts": q.get("last_updated"),
        "market_cap": Decimal(str(q["total_market_cap"])),
        "market_cap_pct_24h": Decimal(str(q.get("total_market_cap_yesterday_percentage_change", 0))),
        "vol_24h": Decimal(str(q["total_volume_24h"])),
        "vol_24h_pct_24h": Decimal(str(q.get("total_volume_24h_yesterday_percentage_change", 0))),
        "active_cryptos": data.get("active_cryptocurrencies"),
        "active_exchanges": data.get("active_exchanges"),
        "active_market_pairs": data.get("active_market_pairs"),
        "btc_dominance": Decimal(str(data.get("btc_dominance", 0))),
        "eth_dominance": Decimal(str(data.get("eth_dominance", 0))),
    }


def persist_global_metrics(payload: Dict) -> MarketSnapshot:
    return MarketSnapshot.objects.create(
        source_ts=payload["source_ts"],
        market_cap=payload["market_cap"],
        market_cap_pct_24h=payload["market_cap_pct_24h"],
        vol_24h=payload["vol_24h"],
        vol_24h_pct_24h=payload["vol_24h_pct_24h"],
        active_cryptos=payload["active_cryptos"],
        active_exchanges=payload["active_exchanges"],
        active_market_pairs=payload["active_market_pairs"],
        btc_dominance=payload["btc_dominance"],
        eth_dominance=payload["eth_dominance"],
    )


# --------- “CMC20” Top-20 Index (cap-weighted; yesterday=100) ---------

def _fetch_top_list(n: int) -> List[dict]:
    data = _cmc_get("/v1/cryptocurrency/listings/latest", {
        "start": "1",
        "limit": str(max(n, 40)),
        "convert": "USD",
        "sort": "market_cap",
    })
    coins = [c for c in data if c["symbol"] not in STABLE_TICKERS]
    return coins[:n]


def _cap_weight_levels(coins: List[dict]) -> Tuple[Decimal, Decimal]:
    level_now, level_yday = Decimal(0), Decimal(0)
    for c in coins:
        q = c["quote"]["USD"]
        mcap = Decimal(str(q.get("market_cap", 0)))
        price_now = Decimal(str(q["price"]))
        chg24 = Decimal(str(q.get("percent_change_24h", 0)))  # %
        denom = (Decimal(1) + (chg24 / Decimal(100))) or Decimal(1)
        price_yday = price_now / denom
        level_now += mcap * price_now
        level_yday += mcap * price_yday
    return level_now, level_yday


def compute_top20_index() -> Dict:
    coins = _fetch_top_list(20)
    now_val, yday_val = _cap_weight_levels(coins)
    if yday_val == 0:
        idx, pct = Decimal(100), Decimal(0)
    else:
        idx = (now_val / yday_val) * Decimal(100)
        pct = ((idx - Decimal(100)) / Decimal(100)) * Decimal(100)
    return {"index_value": idx.quantize(Decimal("0.01")), "pct_change_24h": pct.quantize(Decimal("0.01"))}


def persist_top20_index(point: Dict) -> Top20IndexPoint:
    return Top20IndexPoint.objects.create(
        index_value=point["index_value"],
        pct_change_24h=point["pct_change_24h"],
    )


# --------- Fear & Greed ---------

def fetch_fear_greed_latest() -> Dict:
    data = _cmc_get("/v3/fear-and-greed/latest")
    # Expected (from your curl):
    # data = {"value": 58, "update_time": "...Z", "value_classification": "Neutral"}
    d = data if isinstance(data, dict) else {}
    v   = d.get("value") or d.get("score")
    cls = d.get("value_classification") or d.get("classification") or ""
    ts  = d.get("update_time") or d.get("timestamp") or d.get("updated_at") or d.get("last_updated")
    if v is None or ts is None:
        logger.error("Unexpected F&G payload: %s", json.dumps(data)[:1000])
        raise ValueError("Unexpected fear-and-greed payload shape")
    return {"value": int(v), "classification": cls, "timestamp": ts}


def persist_fear_greed(payload: Dict) -> FearGreedReading:
    ts = dt.datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
    obj, _ = FearGreedReading.objects.get_or_create(
        ts=ts,
        defaults={"value": payload["value"], "classification": payload["classification"]},
    )
    return obj


# --------- Optional “heavy” metrics (Altseason & Avg RSI) ---------

def _fetch_ohlc_daily(coin_id: int, days: int) -> List[dict]:
    end = dt.datetime.utcnow().date()
    start = end - dt.timedelta(days=days)
    data = _cmc_get("/v1/cryptocurrency/ohlcv/historical", {
        "id": str(coin_id),
        "convert": "USD",
        "time_start": start.isoformat(),
        "time_end": end.isoformat(),
        "interval": "daily",
    })
    return data.get("quotes", [])


def _pct_change_from_ohlc(rows: List[dict]) -> Decimal:
    if not rows:
        return Decimal(0)
    p0 = Decimal(str(rows[0]["quote"]["USD"]["close"]))
    pn = Decimal(str(rows[-1]["quote"]["USD"]["close"]))
    return ((pn - p0) / p0) * Decimal(100) if p0 else Decimal(0)


def _rsi_from_ohlc(rows: List[dict], period: int = 14) -> Decimal:
    closes = [Decimal(str(r["quote"]["USD"]["close"])) for r in rows]
    if len(closes) < period + 1:
        return Decimal(50)
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, Decimal(0)))
        losses.append(max(-d, Decimal(0)))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return Decimal(100)
    rs = avg_gain / avg_loss
    return Decimal(100) - (Decimal(100) / (Decimal(1) + rs))


def compute_altseason_and_avg_rsi(
    altseason_lookback_days: int = 90,
    rsi_lookback_days: int = 100,
    rsi_basket_size: int = 100,
) -> Tuple[Dict, Dict]:
    top = _fetch_top_list(max(rsi_basket_size, 60))
    alts = [c for c in top if c["symbol"] not in STABLE_TICKERS and c["symbol"] != "BTC"][:50]
    btc = next(c for c in top if c["symbol"] == "BTC")

    btc_rows = _fetch_ohlc_daily(btc["id"], altseason_lookback_days)
    btc_pct = _pct_change_from_ohlc(btc_rows)

    beaters = 0
    for c in alts:
        rows = _fetch_ohlc_daily(c["id"], altseason_lookback_days)
        if _pct_change_from_ohlc(rows) > btc_pct:
            beaters += 1
    share = (beaters / max(len(alts), 1)) * 100
    altseason = {"percentage": Decimal(str(round(share, 2))), "is_altseason": share >= 75}

    rsi_universe = [c for c in top if c["symbol"] not in STABLE_TICKERS][:rsi_basket_size]
    rsis = []
    for c in rsi_universe:
        rows = _fetch_ohlc_daily(c["id"], rsi_lookback_days)
        rsis.append(_rsi_from_ohlc(rows, 14))
    avg_rsi = sum(rsis) / Decimal(len(rsis)) if rsis else Decimal(50)
    avg_rsi_payload = {"avg_rsi": Decimal(str(round(avg_rsi, 2)))}

    return altseason, avg_rsi_payload


def persist_altseason(payload: Dict) -> AltseasonReading:
    return AltseasonReading.objects.create(
        percentage=payload["percentage"],
        is_altseason=payload["is_altseason"],
    )


def persist_avg_rsi(payload: Dict) -> AverageRsiReading:
    return AverageRsiReading.objects.create(avg_rsi=payload["avg_rsi"])


# --------- Orchestrator ---------

@transaction.atomic
def update_dashboard(compute_heavy: bool = False) -> Dict:
    out: Dict[str, object] = {}

    gm = fetch_global_metrics()
    out["market_snapshot"] = persist_global_metrics(gm)

    idx = compute_top20_index()
    out["top20_point"] = persist_top20_index(idx)

    try:
        fg = fetch_fear_greed_latest()
        out["fear_greed"] = persist_fear_greed(fg)
    except Exception as e:
        out["fear_greed_error"] = str(e)

    if compute_heavy:
        altseason, avg_rsi = compute_altseason_and_avg_rsi()
        out["altseason"] = persist_altseason(altseason)
        out["average_rsi"] = persist_avg_rsi(avg_rsi)

    return out
