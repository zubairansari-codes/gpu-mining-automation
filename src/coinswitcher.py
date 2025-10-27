#!/usr/bin/env python3
"""
Coin Switcher - Determines most profitable coin and whether to switch.
"""
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class CoinSwitcher:
    def __init__(self, coins_config: Dict[str, Any], config: Dict[str, Any]):
        self.coins = coins_config or {}
        self.config = config or {"min_delta": 0.02}

    async def get_most_profitable_coin(self) -> Dict[str, Any]:
        # Very simplified profitability ranking based on config-estimated usd_per_mh
        ranked = sorted(self.coins.values(), key=lambda c: c.get('usd_per_mh', 0), reverse=True)
        return ranked[0] if ranked else None

    async def should_switch_coin(self, current_coin: Dict[str, Any], current_profit: float) -> Tuple[bool, Dict[str, Any]]:
        best = await self.get_most_profitable_coin()
        if not best or not current_coin:
            return False, current_coin
        if best['name'] != current_coin['name'] and (best.get('usd_per_mh', 0) - current_coin.get('usd_per_mh', 0)) >= self.config.get('min_delta', 0.02):
            return True, best
        return False, current_coin
