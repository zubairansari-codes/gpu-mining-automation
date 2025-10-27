#!/usr/bin/env python3
"""
VastAI Manager - Handles API interactions with Vast.ai for listing, renting, and managing instances.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import aiohttp

logger = logging.getLogger(__name__)

API_BASE = "https://api.vast.ai/v0"

class VastAIManager:
    def __init__(self, api_key: Optional[str], config: Dict[str, Any]):
        self.api_key = api_key or os.getenv('VASTAI_API_KEY')
        self.config = config or {}
        if not self.api_key:
            logger.warning("VASTAI_API_KEY not set; VastAI actions will be mocked.")

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    async def find_profitable_gpus(self, min_gpu_ram: int, max_price_per_hour: float) -> List[Dict[str, Any]]:
        if not self.api_key:
            # Mocked list
            return [{"id": "mock-offer-1", "gpu_name": "RTX 3080", "vram_gb": 10, "dph_total": 0.35}]
        params = {
            "q": f"verified=true&cuda_vers=>=11&min_gpu_ram={min_gpu_ram}",
            "order": "dph_total+asc",
            "type": "on-demand"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE}/listings", params=params, headers=self._headers()) as resp:
                data = await resp.json()
                offers = [o for o in data.get('offers', []) if o.get('dph_total', 999) <= max_price_per_hour]
                return offers

    async def rent_instance(self, offer: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            return {"id": f"mock-inst-{offer['id']}", "offer_id": offer['id'], "state": "running"}
        payload = {"image": self.config.get("image", "nvidia/cuda:12.2.2-base"), "disk": self.config.get("disk_gb", 20)}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_BASE}/instances", json=payload, headers=self._headers()) as resp:
                if resp.status >= 400:
                    txt = await resp.text()
                    logger.error(f"Failed to rent instance: {resp.status} {txt}")
                    return None
                return await resp.json()

    async def exec_on_instance(self, instance_id: str, command: str) -> Any:
        if not self.api_key:
            logger.info(f"[MOCK] exec on {instance_id}: {command}")
            return {"ok": True}
        payload = {"cmd": command}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_BASE}/instances/{instance_id}/exec", json=payload, headers=self._headers()) as resp:
                return await resp.json()

    async def get_instance_status(self, instance_id: str) -> Dict[str, Any]:
        if not self.api_key:
            return {"id": instance_id, "state": "running"}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE}/instances/{instance_id}", headers=self._headers()) as resp:
                return await resp.json()

    async def terminate_instance(self, instance_id: str) -> bool:
        if not self.api_key:
            logger.info(f"[MOCK] terminate {instance_id}")
            return True
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{API_BASE}/instances/{instance_id}", headers=self._headers()) as resp:
                return resp.status < 400

    async def get_instance(self, instance_id: str) -> Dict[str, Any]:
        return await self.get_instance_status(instance_id)
