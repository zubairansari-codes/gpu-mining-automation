#!/usr/bin/env python3
import asyncio
import yaml
from vastaimanager import VastAIManager
from miningcontroller import MiningController
from poolmonitor import PoolMonitor
from coinswitcher import CoinSwitcher
from tracker import ProfitTracker
from telegramnotifier import TelegramNotifier

async def main():
    cfg = yaml.safe_load(open('configs/config.yaml'))
    pool_cfg = yaml.safe_load(open('configs/miningpools.yaml'))
    coins_cfg = yaml.safe_load(open('configs/coins.yaml'))

    vast = VastAIManager(api_key=None, config=cfg.get('vastai', {}))
    pool = PoolMonitor(pools_config=pool_cfg, config=cfg.get('pool_monitor', {}))
    coins = CoinSwitcher(coins_config=coins_cfg, config=cfg.get('coin_switcher', {}))
    tracker = ProfitTracker(config=cfg.get('profit_tracker', {}))
    telegram = TelegramNotifier(bot_token=None, chat_id=None)
    controller = MiningController(vast, pool, coins, tracker, telegram, cfg.get('mining_controller', {}))

    offers = await vast.find_profitable_gpus(min_gpu_ram=cfg['vastai'].get('min_gpu_ram',8), max_price_per_hour=cfg['vastai'].get('max_price_per_hour',0.5))
    if not offers:
        print('No offers')
        return
    best_coin = await coins.get_most_profitable_coin()
    await controller.rent_and_mine(offers[0], best_coin)

if __name__ == '__main__':
    asyncio.run(main())
