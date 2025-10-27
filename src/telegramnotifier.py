#!/usr/bin/env python3
"""
Telegram Notifier - Sends notifications via Telegram Bot API.
"""
import os
import logging
from typing import Optional
import aiohttp

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self, bot_token: Optional[str], chat_id: Optional[str]):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials missing; notifications will be logged only.")

    async def send_message(self, text: str) -> bool:
        if not self.bot_token or not self.chat_id:
            logger.info(f"[MOCK] Telegram: {text}")
            return True
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"chat_id": self.chat_id, "text": text, "disable_web_page_preview": True}) as resp:
                ok = resp.status < 400
                if not ok:
                    body = await resp.text()
                    logger.error(f"Telegram send failed: {resp.status} {body}")
                return ok
