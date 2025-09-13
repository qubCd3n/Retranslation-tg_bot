#!/usr/bin/env python3
"""
Скрипт запуска бота-ретранслятора
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

from telegram_bot import TelegramRelayBot
from monitor import get_monitor
from config import Config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL.upper()),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

class BotRunner:
    """Класс для запуска и управления ботом"""
    
    def __init__(self):
        self.bot = None
        self.monitor = get_monitor()
        self.running = False
        
    async def start(self):
        """Запускает бота"""
        try:
            logger.info("Starting Telegram Relay Bot...")
            
            # Создаем экземпляр бота
            self.bot = TelegramRelayBot()
            self.running = True
            
            # Настраиваем обработчики сигналов
            self._setup_signal_handlers()
            
            # Запускаем бота
            await self.bot.start()
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            self.monitor.record_error(f"Startup failed: {e}")
            raise
    
    def _setup_signal_handlers(self):
        """Настраивает обработчики сигналов для корректного завершения"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def health_check_loop(self):
        """Цикл проверки здоровья бота"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Проверка каждые 5 минут
                
                if self.running:
                    health = await self.monitor.check_bot_health()
                    if health['status'] != 'healthy':
                        logger.warning(f"Bot health check failed: {health}")
                        
            except Exception as e:
                logger.error(f"Health check error: {e}")
                self.monitor.record_error(f"Health check error: {e}")
    
    async def cleanup_loop(self):
        """Цикл очистки временных файлов"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Очистка каждый час
                
                if self.running:
                    from utils import cleanup_temp_dir
                    cleanup_temp_dir(Config.TEMP_DIR)
                    
            except Exception as e:
                logger.error(f"Cleanup error: {e}")

async def main():
    """Главная функция"""
    runner = BotRunner()
    
    try:
        # Запускаем бота и фоновые задачи
        await asyncio.gather(
            runner.start(),
            runner.health_check_loop(),
            runner.cleanup_loop()
        )
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        runner.monitor.record_error(f"Unexpected error: {e}")
    finally:
        runner.running = False
        logger.info("Bot stopped")

if __name__ == "__main__":
    # Проверяем наличие .env файла
    env_file = Path(".env")
    if not env_file.exists():
        logger.error("No .env file found! Please create one based on env_example.txt")
        sys.exit(1)
    
    # Запускаем бота
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to run bot: {e}")
        sys.exit(1)
