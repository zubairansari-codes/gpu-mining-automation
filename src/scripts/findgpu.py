#!/usr/bin/env python3
import asyncio
from vastaimanager import VastAIManager
import yaml

async def main():
    cfg = yaml.safe_load(open('configs/config.yaml'))
    vast = VastAIManager(api_key=None, config=cfg.get('vastai', {}))
    offers = await vast.find_profitable_gpus(min_gpu_ram=cfg['vastai'].get('min_gpu_ram',8), max_price_per_hour=cfg['vastai'].get('max_price_per_hour',0.5))
    for o in offers:
        print(o)

if __name__ == '__main__':
    asyncio.run(main())
