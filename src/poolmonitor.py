#!/usr/bin/env python3
"""
Pool Monitor - Build miner commands and query pools for hashrate and earnings.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PoolMonitor:
    def __init__(self, pools_config: Dict[str, Any], config: Dict[str, Any]):
        self.pools = pools_config or {}
        self.config = config or {}

    def build_miner_command(self, coin: Dict[str, Any]) -> str:
        algo = coin['algorithm']
        pool = self.pools.get(coin['name'], {})
        url = pool.get('url', 'stratum+tcp://example.com:3333')
        wallet = pool.get('wallet', 'WALLET_ADDRESS')
        worker = pool.get('worker', 'worker1')
        miner = self.config.get('miner', 'lolMiner')
        if miner.lower() == 'lolminer':
            return f"nohup ./lolMiner --algo {algo} --pool {url} --user {wallet}.{worker} > miner.log 2>&1 &"
        if miner.lower() == 'nbminer':
            return f"nohup ./nbminer -a {algo} -o {url} -u {wallet}.{worker} > miner.log 2>&1 &"
        return f"echo 'Unsupported miner'"

    async def get_pool_stats(self, coin_name: str) -> Dict[str, Any]:
        # Placeholder for pool API requests per coin
        return {"reported_hashrate": 50, "unpaid": 0.0}
