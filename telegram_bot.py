import asyncio
import logging
import os
import tempfile
from typing import Optional, Union
from pathlib import Path

from telegram import Update, Message, Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from telegram.error import TelegramError

from config import Config
from metadata_cleaner import MetadataCleaner

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL.upper())
)
logger = logging.getLogger(__name__)

class TelegramRelayBot:
    """Бот для ретрансляции сообщений между каналами"""
    
    def __init__(self):
        self.config = Config()
        self.config.validate()
        
        # Создаем временную директорию
        self.temp_dir = Path(self.config.TEMP_DIR)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Настраиваем прокси если указан (опционально для тестирования)
        self.proxy_url = None
        if self.config.PROXY_URL:
            self.proxy_url = self.config.PROXY_URL
            if self.config.PROXY_USERNAME and self.config.PROXY_PASSWORD:
                # Формируем URL с авторизацией
                protocol, rest = self.proxy_url.split('://', 1)
                self.proxy_url = f"{protocol}://{self.config.PROXY_USERNAME}:{self.config.PROXY_PASSWORD}@{rest}"
            logger.info(f"Using proxy: {self.proxy_url.split('@')[-1] if '@' in self.proxy_url else self.proxy_url}")
        else:
            logger.info("Running without proxy (suitable for testing)")
        
        # Создаем приложение с прокси
        self.application = self._create_application()
        
    def _create_application(self) -> Application:
        """Создает приложение Telegram с настройками прокси"""
        builder = Application.builder().token(self.config.BOT_TOKEN)
        
        if self.proxy_url:
            builder = builder.proxy_url(self.proxy_url)
        
        return builder.build()
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает входящие сообщения из исходного канала"""
        # Логируем все обновления для отладки
        logger.info(f"Received update: {update}")
        logger.info(f"Update type: {update.message is not None and 'message' or 'no message'}")
        
        # Получаем сообщение из update (может быть message или channel_post)
        message = update.message or update.channel_post
        
        if not message:
            logger.warning("No message in update")
            return
        
        # Логируем все входящие сообщения
        logger.info(f"Received message from chat_id: {message.chat_id}, expected: {self.config.SOURCE_CHANNEL_ID}")
        logger.info(f"Message type: {message.chat.type}, Message ID: {message.message_id}")
        
        # Проверяем, что сообщение из нужного канала
        if str(message.chat_id) != str(self.config.SOURCE_CHANNEL_ID):
            logger.debug(f"Message from unexpected channel: {message.chat_id}, expected: {self.config.SOURCE_CHANNEL_ID}")
            return
        
        logger.info(f"Processing message from source channel: {message.message_id}")
        
        try:
            # Копируем сообщение в целевой канал
            await self._copy_message_to_target(message)
            logger.info(f"Successfully copied message {message.message_id}")
            
        except Exception as e:
            logger.error(f"Error copying message {message.message_id}: {e}")
    
    async def _copy_message_to_target(self, source_message: Message) -> None:
        """Копирует сообщение в целевой канал с полным копированием контента"""
        
        # Получаем бота из контекста
        bot = self.application.bot
        
        # Обрабатываем текст сообщения
        text = source_message.text or source_message.caption or ""
        parse_mode = getattr(source_message, 'parse_mode', None) or ParseMode.HTML
        
        # Обрабатываем медиафайлы
        media_files = []
        
        if source_message.photo:
            # Обрабатываем фото
            photo = source_message.photo[-1]  # Берем самое большое фото
            media_files.append(('photo', photo.file_id, photo.file_unique_id))
            
        elif source_message.video:
            # Обрабатываем видео
            video = source_message.video
            media_files.append(('video', video.file_id, video.file_unique_id))
            
        elif source_message.document:
            # Обрабатываем документ
            document = source_message.document
            media_files.append(('document', document.file_id, document.file_unique_id))
            
        elif source_message.animation:
            # Обрабатываем GIF/анимацию
            animation = source_message.animation
            media_files.append(('animation', animation.file_id, animation.file_unique_id))
            
        elif source_message.video_note:
            # Обрабатываем видеосообщение
            video_note = source_message.video_note
            media_files.append(('video_note', video_note.file_id, video_note.file_unique_id))
            
        elif source_message.voice:
            # Обрабатываем голосовое сообщение
            voice = source_message.voice
            media_files.append(('voice', voice.file_id, voice.file_unique_id))
            
        elif source_message.audio:
            # Обрабатываем аудио
            audio = source_message.audio
            media_files.append(('audio', audio.file_id, audio.file_unique_id))
        
        # Обрабатываем медиафайлы если они есть
        if media_files:
            await self._process_media_files(bot, media_files, text, parse_mode)
        else:
            # Отправляем только текст
            await bot.send_message(
                chat_id=self.config.TARGET_CHANNEL_ID,
                text=text,
                parse_mode=parse_mode
            )
    
    async def _process_media_files(self, bot: Bot, media_files: list, caption: str, parse_mode: str) -> None:
        """Обрабатывает медиафайлы с очисткой метаданных"""
        
        for media_type, file_id, file_unique_id in media_files:
            try:
                # Скачиваем файл
                file_path = await self._download_file(bot, file_id, media_type)
                
                if not file_path:
                    logger.error(f"Failed to download {media_type}: {file_id}")
                    continue
                
                # Очищаем метаданные если включено
                if self.config.ENABLE_METADATA_CLEANING:
                    cleaned_path = self._clean_file_metadata(file_path)
                else:
                    cleaned_path = file_path
                
                # Отправляем файл в целевой канал
                await self._send_media_to_target(bot, media_type, cleaned_path, caption, parse_mode)
                
                # Удаляем временные файлы
                self._cleanup_temp_files([file_path, cleaned_path])
                
            except Exception as e:
                logger.error(f"Error processing {media_type} {file_id}: {e}")
    
    async def _download_file(self, bot: Bot, file_id: str, media_type: str) -> Optional[str]:
        """Скачивает файл с серверов Telegram"""
        try:
            file = await bot.get_file(file_id)
            
            # Создаем временный файл
            temp_file = tempfile.NamedTemporaryFile(
                dir=self.temp_dir,
                delete=False,
                suffix=f"_{media_type}"
            )
            temp_path = temp_file.name
            temp_file.close()
            
            # Скачиваем файл
            await file.download_to_drive(temp_path)
            
            # Проверяем размер файла
            file_size = os.path.getsize(temp_path)
            if file_size > self.config.MAX_FILE_SIZE:
                logger.warning(f"File too large: {file_size} bytes")
                os.unlink(temp_path)
                return None
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            return None
    
    def _clean_file_metadata(self, file_path: str) -> str:
        """Очищает метаданные из файла"""
        try:
            # Создаем путь для очищенного файла
            cleaned_path = file_path + "_cleaned"
            
            # Очищаем метаданные
            return MetadataCleaner.clean_file_metadata(file_path, cleaned_path)
            
        except Exception as e:
            logger.error(f"Error cleaning metadata from {file_path}: {e}")
            return file_path
    
    async def _send_media_to_target(self, bot: Bot, media_type: str, file_path: str, caption: str, parse_mode: str) -> None:
        """Отправляет медиафайл в целевой канал"""
        try:
            with open(file_path, 'rb') as file:
                if media_type == 'photo':
                    await bot.send_photo(
                        chat_id=self.config.TARGET_CHANNEL_ID,
                        photo=file,
                        caption=caption,
                        parse_mode=parse_mode
                    )
                elif media_type == 'video':
                    await bot.send_video(
                        chat_id=self.config.TARGET_CHANNEL_ID,
                        video=file,
                        caption=caption,
                        parse_mode=parse_mode
                    )
                elif media_type == 'document':
                    await bot.send_document(
                        chat_id=self.config.TARGET_CHANNEL_ID,
                        document=file,
                        caption=caption,
                        parse_mode=parse_mode
                    )
                elif media_type == 'animation':
                    await bot.send_animation(
                        chat_id=self.config.TARGET_CHANNEL_ID,
                        animation=file,
                        caption=caption,
                        parse_mode=parse_mode
                    )
                elif media_type == 'video_note':
                    await bot.send_video_note(
                        chat_id=self.config.TARGET_CHANNEL_ID,
                        video_note=file
                    )
                elif media_type == 'voice':
                    await bot.send_voice(
                        chat_id=self.config.TARGET_CHANNEL_ID,
                        voice=file,
                        caption=caption,
                        parse_mode=parse_mode
                    )
                elif media_type == 'audio':
                    await bot.send_audio(
                        chat_id=self.config.TARGET_CHANNEL_ID,
                        audio=file,
                        caption=caption,
                        parse_mode=parse_mode
                    )
                    
        except Exception as e:
            logger.error(f"Error sending {media_type} to target channel: {e}")
            raise
    
    def _cleanup_temp_files(self, file_paths: list) -> None:
        """Удаляет временные файлы"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.error(f"Error deleting temp file {file_path}: {e}")
    
    def setup_handlers(self) -> None:
        """Настраивает обработчики сообщений"""
        # Обработчик для сообщений из каналов
        self.application.add_handler(
            MessageHandler(
                filters.ChatType.CHANNEL,
                self.handle_message
            )
        )
    
    async def start(self) -> None:
        """Запускает бота"""
        logger.info("Starting Telegram Relay Bot...")
        
        # Настраиваем обработчики
        self.setup_handlers()
        
        # Запускаем бота
        await self.application.initialize()
        await self.application.start()
        
        # Получаем информацию о боте
        bot_info = await self.application.bot.get_me()
        logger.info(f"Bot started: @{bot_info.username}")
        
        # Запускаем polling
        await self.application.updater.start_polling()
        
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        # Ждем завершения
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Stopping bot...")
        finally:
            await self.application.stop()
            await self.application.shutdown()

def main():
    """Главная функция"""
    try:
        bot = TelegramRelayBot()
        asyncio.run(bot.start())
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    main()
