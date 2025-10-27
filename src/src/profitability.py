import os
import time
import requests
from typing import Dict, Any

POOL_APIS = {
    "RVN": lambda wallet: f"https://rvn.2miners.com/api/accounts/{wallet}",
    "ETC": lambda wallet: f"https://etc.2miners.com/api/accounts/{wallet}",
    "ZEC": lambda wallet: f"https://zec.2miners.com/api/accounts/{wallet}",
}

def fetch_pool_stats(coin: str, wallet: str) -> Dict[str, Any]:
    coin = coin.upper()
    if not wallet:
        return {}
    if coin not in POOL_APIS:
        return {}
    url = POOL_APIS[coin](wallet)
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}


def estimate_profit(algo: str, hashrate: float, power_watts: float, power_cost: float, pool_fee: float = 0.01) -> float:
    # Backward-compatible static model as fallback
    algo_factor = {
        "KAWPOW": 0.0005,
        "ETHASH": 0.0004,
        "EQUIHASH": 0.00045,
        "SHA256": 1e-9,
    }.get(algo.upper(), 0.0003)
    revenue = hashrate * algo_factor * 24  # USD/day (placeholder if live unavailable)
    cost = power_watts * 24 / 1000 * power_cost
    fees = revenue * pool_fee
    return max(revenue - cost - fees, 0.0)


def estimate_real_earnings(coin: str, wallet: str) -> Dict[str, Any]:
    """
    Uses pool account API to approximate earnings:
    - reportedHashrate, currentHashrate
    - shares, immature, balance, payments
    Returns a dict with USD estimates if price is present, otherwise in coin units.
    """
    stats = fetch_pool_stats(coin, wallet)
    if not stats:
        return {"available": False}

    # 2Miners format: { stats: { ... }, payments: [...], currentHashrate, hashrate, immature, balance, price }
    result = {"available": True}
    for key in ["currentHashrate", "hashrate", "immature", "balance", "price"]:
        if key in stats:
            result[key] = stats[key]
        elif "stats" in stats and key in stats["stats"]:
            result[key] = stats["stats"][key]

    # Rough daily earnings from balance delta is not accessible without history here; use hashrate and pool average if provided
    if "currentHashrate" in result and "price" in result:
        # Convert to MH/s if needed and estimate coins/day from pool hints if provided
        # Here we keep it simple: expose key values and let CLI print them
        pass
    return result


if __name__ == "__main__":
    # CLI quick check
    wallet = os.getenv("WALLET_ADDRESS", "")
    coin = os.getenv("COIN", "RVN")
    info = estimate_real_earnings(coin, wallet)
    print(info if info else {"available": False})
