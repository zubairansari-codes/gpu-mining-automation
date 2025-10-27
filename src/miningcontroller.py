#!/usr/bin/env python3
"""
Mining Controller - Orchestrates renting and mining workflow per instance.
"""
import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MiningController:
    def __init__(self, vastai_manager, pool_monitor, coin_switcher, profit_tracker, telegram_notifier, config: Dict[str, Any]):
        self.vastai = vastai_manager
        self.pool_monitor = pool_monitor
        self.coin_switcher = coin_switcher
        self.tracker = profit_tracker
        self.notify = telegram_notifier
        self.config = config or {}

    async def rent_and_mine(self, gpu: Dict[str, Any], coin: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            logger.info(f"Attempting to rent GPU offer {gpu['id']} for coin {coin['name']}")
            instance = await self.vastai.rent_instance(gpu)
            if not instance:
                logger.warning("Failed to rent instance")
                return None

            await self._provision_instance(instance)
            await self._start_miner(instance, coin)
            return instance
        except Exception as e:
            logger.error(f"rent_and_mine error: {e}", exc_info=True)
            await self.notify.send_message(f"❌ rent_and_mine failed for GPU {gpu.get('id')}: {e}")
            return None

    async def _provision_instance(self, instance: Dict[str, Any]):
        logger.info(f"Provisioning instance {instance['id']}")
        # Install drivers/miner etc. This is a placeholder to run remote commands via SSH or API
        await self.vastai.exec_on_instance(instance['id'], "echo provisioning && sleep 1")

    async def _start_miner(self, instance: Dict[str, Any], coin: Dict[str, Any]):
        logger.info(f"Starting miner for {coin['name']} on instance {instance['id']}")
        pool_cmd = self.pool_monitor.build_miner_command(coin)
        await self.vastai.exec_on_instance(instance['id'], pool_cmd)

    async def get_mining_performance(self, instance_id: str) -> Dict[str, Any]:
        # Query miner API or parse logs
        stats = await self.vastai.exec_on_instance(instance_id, "echo '{\"hashrate\": 50, \"power\": 150}'")
        return {"hashrate": 50, "power": 150, "unit": "MH/s"}

    async def stop_mining(self, instance_id: str):
        logger.info(f"Stopping miner on instance {instance_id}")
        await self.vastai.exec_on_instance(instance_id, "pkill -f miner || true")
        await self.vastai.terminate_instance(instance_id)

    async def switch_coin(self, instance_id: str, coin: Dict[str, Any]):
        logger.info(f"Switching instance {instance_id} to coin {coin['name']}")
        await self.stop_mining(instance_id)
        # Assume we can retrieve instance object again
        instance = await self.vastai.get_instance(instance_id)
        await self._start_miner(instance, coin)
