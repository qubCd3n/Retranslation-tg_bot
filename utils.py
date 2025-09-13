import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def ensure_temp_dir(temp_dir: str) -> Path:
    """Создает временную директорию если она не существует"""
    temp_path = Path(temp_dir)
    temp_path.mkdir(parents=True, exist_ok=True)
    return temp_path

def cleanup_temp_dir(temp_dir: str, max_age_hours: int = 24):
    """Очищает старые файлы из временной директории"""
    temp_path = Path(temp_dir)
    if not temp_path.exists():
        return
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for file_path in temp_path.iterdir():
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_path.unlink()
                    logger.debug(f"Deleted old temp file: {file_path}")
                except Exception as e:
                    logger.error(f"Error deleting temp file {file_path}: {e}")

def get_file_size_mb(file_path: str) -> float:
    """Возвращает размер файла в мегабайтах"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0.0

def is_safe_filename(filename: str) -> bool:
    """Проверяет безопасность имени файла"""
    dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    return not any(char in filename for char in dangerous_chars)

def sanitize_filename(filename: str) -> str:
    """Очищает имя файла от опасных символов"""
    dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    return filename

def create_backup(file_path: str, backup_dir: str = "backups") -> Optional[str]:
    """Создает резервную копию файла"""
    try:
        backup_path = Path(backup_dir)
        backup_path.mkdir(exist_ok=True)
        
        filename = Path(file_path).name
        backup_file = backup_path / f"{filename}.backup"
        
        shutil.copy2(file_path, backup_file)
        logger.info(f"Created backup: {backup_file}")
        return str(backup_file)
        
    except Exception as e:
        logger.error(f"Error creating backup for {file_path}: {e}")
        return None

def validate_channel_id(channel_id: str) -> bool:
    """Проверяет валидность ID канала"""
    try:
        # ID канала должен быть числом, начинающимся с -100
        if not channel_id.startswith('-100'):
            return False
        
        int(channel_id)
        return True
        
    except ValueError:
        return False

def format_file_size(size_bytes: int) -> str:
    """Форматирует размер файла в читаемый вид"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def get_supported_media_types() -> list:
    """Возвращает список поддерживаемых типов медиафайлов"""
    return [
        'photo', 'video', 'document', 'animation', 
        'video_note', 'voice', 'audio'
    ]

def is_media_message(message) -> bool:
    """Проверяет, является ли сообщение медиафайлом"""
    return any([
        message.photo, message.video, message.document,
        message.animation, message.video_note, message.voice, message.audio
    ])

def get_media_type(message) -> Optional[str]:
    """Возвращает тип медиафайла в сообщении"""
    if message.photo:
        return 'photo'
    elif message.video:
        return 'video'
    elif message.document:
        return 'document'
    elif message.animation:
        return 'animation'
    elif message.video_note:
        return 'video_note'
    elif message.voice:
        return 'voice'
    elif message.audio:
        return 'audio'
    else:
        return None
