import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List
import json
import os

from telegram import Bot
from config import Config

logger = logging.getLogger(__name__)

class BotMonitor:
    """Система мониторинга бота"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.bot = Bot(token=bot_token)
        self.stats_file = "bot_stats.json"
        self.stats = self._load_stats()
        
    def _load_stats(self) -> Dict:
        """Загружает статистику из файла"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading stats: {e}")
        
        return {
            "messages_processed": 0,
            "errors_count": 0,
            "last_message_time": None,
            "uptime_start": datetime.now().isoformat(),
            "daily_stats": {}
        }
    
    def _save_stats(self):
        """Сохраняет статистику в файл"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving stats: {e}")
    
    def record_message_processed(self):
        """Записывает обработанное сообщение"""
        self.stats["messages_processed"] += 1
        self.stats["last_message_time"] = datetime.now().isoformat()
        
        # Обновляем дневную статистику
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.stats["daily_stats"]:
            self.stats["daily_stats"][today] = 0
        self.stats["daily_stats"][today] += 1
        
        self._save_stats()
    
    def record_error(self, error_msg: str):
        """Записывает ошибку"""
        self.stats["errors_count"] += 1
        logger.error(f"Bot error: {error_msg}")
        self._save_stats()
    
    def get_uptime(self) -> timedelta:
        """Возвращает время работы бота"""
        start_time = datetime.fromisoformat(self.stats["uptime_start"])
        return datetime.now() - start_time
    
    def get_daily_stats(self, days: int = 7) -> List[Dict]:
        """Возвращает статистику за последние дни"""
        result = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            count = self.stats["daily_stats"].get(date, 0)
            result.append({"date": date, "messages": count})
        return result
    
    async def check_bot_health(self) -> Dict:
        """Проверяет состояние бота"""
        try:
            # Проверяем подключение к Telegram
            bot_info = await self.bot.get_me()
            
            # Проверяем доступность каналов
            source_channel = await self.bot.get_chat(Config.SOURCE_CHANNEL_ID)
            target_channel = await self.bot.get_chat(Config.TARGET_CHANNEL_ID)
            
            return {
                "status": "healthy",
                "bot_username": bot_info.username,
                "source_channel": source_channel.title,
                "target_channel": target_channel.title,
                "uptime": str(self.get_uptime()),
                "messages_processed": self.stats["messages_processed"],
                "errors_count": self.stats["errors_count"]
            }
            
        except Exception as e:
            self.record_error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "uptime": str(self.get_uptime()),
                "messages_processed": self.stats["messages_processed"],
                "errors_count": self.stats["errors_count"]
            }
    
    async def send_health_report(self, admin_chat_id: str = None):
        """Отправляет отчет о состоянии бота"""
        if not admin_chat_id:
            return
        
        try:
            health = await self.check_bot_health()
            daily_stats = self.get_daily_stats(7)
            
            report = f"🤖 **Отчет о состоянии бота**\n\n"
            report += f"**Статус:** {'✅ Здоров' if health['status'] == 'healthy' else '❌ Проблемы'}\n"
            report += f"**Время работы:** {health['uptime']}\n"
            report += f"**Обработано сообщений:** {health['messages_processed']}\n"
            report += f"**Ошибок:** {health['errors_count']}\n\n"
            
            if health['status'] == 'healthy':
                report += f"**Исходный канал:** {health['source_channel']}\n"
                report += f"**Целевой канал:** {health['target_channel']}\n\n"
            
            report += "**Статистика за последние 7 дней:**\n"
            for stat in daily_stats:
                report += f"• {stat['date']}: {stat['messages']} сообщений\n"
            
            await self.bot.send_message(
                chat_id=admin_chat_id,
                text=report,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error sending health report: {e}")

# Глобальный экземпляр монитора
monitor = None

def get_monitor() -> BotMonitor:
    """Возвращает экземпляр монитора"""
    global monitor
    if monitor is None:
        monitor = BotMonitor(Config.BOT_TOKEN)
    return monitor
