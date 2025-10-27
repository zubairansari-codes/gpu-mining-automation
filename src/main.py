#!/usr/bin/env python3
"""
GPU Mining Automation - Main Entry Point

This is the core orchestration module that coordinates all mining automation activities.
It manages GPU rentals, mining operations, profitability tracking, and notifications.
"""

import os
import sys
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

import yaml
from dotenv import load_dotenv

# Import our custom modules
from miningcontroller import MiningController
from vastaimanager import VastAIManager
from poolmonitor import PoolMonitor
from telegramnotifier import TelegramNotifier
from coinswitcher import CoinSwitcher
from tracker import ProfitTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mining_automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class GPUMiningAutomation:
    """Main orchestration class for GPU mining automation."""
    
    def __init__(self, config_path: str = 'configs/config.yaml'):
        """Initialize the GPU mining automation system.
        
        Args:
            config_path: Path to the main configuration file
        """
        logger.info("Initializing GPU Mining Automation System...")
        
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        self.config = self._load_config(config_path)
        self.mining_pools_config = self._load_config('configs/miningpools.yaml')
        self.coins_config = self._load_config('configs/coins.yaml')
        
        # Initialize components
        self.vastai_manager = VastAIManager(
            api_key=os.getenv('VASTAI_API_KEY'),
            config=self.config['vastai']
        )
        
        self.telegram_notifier = TelegramNotifier(
            bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
            chat_id=os.getenv('TELEGRAM_CHAT_ID')
        )
        
        self.pool_monitor = PoolMonitor(
            pools_config=self.mining_pools_config,
            config=self.config['pool_monitor']
        )
        
        self.coin_switcher = CoinSwitcher(
            coins_config=self.coins_config,
            config=self.config['coin_switcher']
        )
        
        self.profit_tracker = ProfitTracker(
            config=self.config['profit_tracker']
        )
        
        self.mining_controller = MiningController(
            vastai_manager=self.vastai_manager,
            pool_monitor=self.pool_monitor,
            coin_switcher=self.coin_switcher,
            profit_tracker=self.profit_tracker,
            telegram_notifier=self.telegram_notifier,
            config=self.config['mining_controller']
        )
        
        self.running = False
        self.active_instances = {}
        
        logger.info("GPU Mining Automation System initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load YAML configuration file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            raise
    
    async def start(self):
        """Start the GPU mining automation system."""
        logger.info("Starting GPU Mining Automation System...")
        self.running = True
        
        try:
            # Send startup notification
            await self.telegram_notifier.send_message(
                "🚀 GPU Mining Automation System Started\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Mode: {self.config.get('mode', 'auto')}"
            )
            
            # Main automation loop
            while self.running:
                try:
                    await self._automation_cycle()
                    
                    # Sleep between cycles
                    sleep_interval = self.config.get('check_interval', 300)
                    logger.info(f"Sleeping for {sleep_interval} seconds before next cycle")
                    await asyncio.sleep(sleep_interval)
                    
                except Exception as e:
                    logger.error(f"Error in automation cycle: {e}", exc_info=True)
                    await self.telegram_notifier.send_message(
                        f"⚠️ Error in automation cycle: {str(e)}"
                    )
                    await asyncio.sleep(60)  # Wait before retrying
                    
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await self.stop()
    
    async def _automation_cycle(self):
        """Execute one cycle of the automation process."""
        logger.info("Starting automation cycle...")
        
        # Step 1: Find profitable GPUs
        profitable_gpus = await self.vastai_manager.find_profitable_gpus(
            min_gpu_ram=self.config['vastai'].get('min_gpu_ram', 8),
            max_price_per_hour=self.config['vastai'].get('max_price_per_hour', 0.5)
        )
        
        if not profitable_gpus:
            logger.info("No profitable GPUs found in this cycle")
            return
        
        logger.info(f"Found {len(profitable_gpus)} profitable GPU(s)")
        
        # Step 2: Check current profitability for best coin
        best_coin = await self.coin_switcher.get_most_profitable_coin()
        if not best_coin:
            logger.warning("Could not determine most profitable coin")
            return
        
        logger.info(f"Most profitable coin: {best_coin['name']} ({best_coin['algorithm']})")
        
        # Step 3: Calculate expected profit
        for gpu in profitable_gpus:
            expected_profit = await self.profit_tracker.calculate_expected_profit(
                gpu_specs=gpu,
                coin=best_coin,
                rental_price=gpu['dph_total']
            )
            
            if expected_profit['net_profit_per_hour'] > self.config.get('min_profit_per_hour', 0.05):
                logger.info(
                    f"GPU {gpu['id']} expected profit: "
                    f"${expected_profit['net_profit_per_hour']:.4f}/hour"
                )
                
                # Step 4: Rent GPU and start mining
                instance = await self.mining_controller.rent_and_mine(
                    gpu=gpu,
                    coin=best_coin
                )
                
                if instance:
                    self.active_instances[instance['id']] = {
                        'instance': instance,
                        'gpu': gpu,
                        'coin': best_coin,
                        'start_time': datetime.now(),
                        'expected_profit': expected_profit
                    }
                    
                    await self.telegram_notifier.send_message(
                        f"✅ Started mining on GPU {gpu['id']}\n"
                        f"Coin: {best_coin['name']}\n"
                        f"Expected profit: ${expected_profit['net_profit_per_hour']:.4f}/hour\n"
                        f"Rental cost: ${gpu['dph_total']:.4f}/hour"
                    )
        
        # Step 5: Monitor active instances
        await self._monitor_active_instances()
    
    async def _monitor_active_instances(self):
        """Monitor and manage active mining instances."""
        if not self.active_instances:
            return
        
        logger.info(f"Monitoring {len(self.active_instances)} active instance(s)")
        
        for instance_id, instance_data in list(self.active_instances.items()):
            try:
                # Check instance status
                status = await self.vastai_manager.get_instance_status(instance_id)
                
                if status['state'] != 'running':
                    logger.warning(f"Instance {instance_id} is not running (state: {status['state']})")
                    await self.telegram_notifier.send_message(
                        f"⚠️ Instance {instance_id} stopped (state: {status['state']})"
                    )
                    del self.active_instances[instance_id]
                    continue
                
                # Check mining performance
                performance = await self.mining_controller.get_mining_performance(instance_id)
                
                # Update profit tracking
                actual_profit = await self.profit_tracker.update_instance_profit(
                    instance_id=instance_id,
                    performance=performance,
                    rental_cost=instance_data['gpu']['dph_total']
                )
                
                # Check if still profitable
                if actual_profit['net_profit_per_hour'] < 0:
                    logger.warning(
                        f"Instance {instance_id} is no longer profitable: "
                        f"${actual_profit['net_profit_per_hour']:.4f}/hour"
                    )
                    
                    await self.mining_controller.stop_mining(instance_id)
                    del self.active_instances[instance_id]
                    
                    await self.telegram_notifier.send_message(
                        f"🛑 Stopped unprofitable instance {instance_id}\n"
                        f"Net profit: ${actual_profit['net_profit_per_hour']:.4f}/hour"
                    )
                
                # Check if should switch coins
                should_switch, new_coin = await self.coin_switcher.should_switch_coin(
                    current_coin=instance_data['coin'],
                    current_profit=actual_profit['net_profit_per_hour']
                )
                
                if should_switch:
                    logger.info(f"Switching instance {instance_id} to {new_coin['name']}")
                    await self.mining_controller.switch_coin(instance_id, new_coin)
                    instance_data['coin'] = new_coin
                    
                    await self.telegram_notifier.send_message(
                        f"🔄 Switched instance {instance_id} to {new_coin['name']}"
                    )
                    
            except Exception as e:
                logger.error(f"Error monitoring instance {instance_id}: {e}", exc_info=True)
    
    async def stop(self):
        """Stop the GPU mining automation system."""
        logger.info("Stopping GPU Mining Automation System...")
        self.running = False
        
        # Stop all active mining instances
        for instance_id in list(self.active_instances.keys()):
            try:
                await self.mining_controller.stop_mining(instance_id)
                logger.info(f"Stopped instance {instance_id}")
            except Exception as e:
                logger.error(f"Error stopping instance {instance_id}: {e}")
        
        # Generate final profit report
        final_report = await self.profit_tracker.generate_final_report()
        
        # Send shutdown notification
        await self.telegram_notifier.send_message(
            "🛑 GPU Mining Automation System Stopped\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Total profit: ${final_report.get('total_profit', 0):.2f}\n"
            f"Total runtime: {final_report.get('total_runtime', 'N/A')}"
        )
        
        logger.info("GPU Mining Automation System stopped successfully")


async def main():
    """Main entry point."""
    # Ensure required directories exist
    Path('logs').mkdir(exist_ok=True)
    Path('data').mkdir(exist_ok=True)
    
    # Initialize and start the system
    automation = GPUMiningAutomation()
    await automation.start()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
