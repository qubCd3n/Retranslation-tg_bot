import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Channel IDs
    SOURCE_CHANNEL_ID = os.getenv('SOURCE_CHANNEL_ID')  # Закрытый канал
    TARGET_CHANNEL_ID = os.getenv('TARGET_CHANNEL_ID')  # Публичный канал
    
    # Proxy Configuration (optional for testing)
    PROXY_URL = os.getenv('PROXY_URL')  # SOCKS5 proxy URL (optional)
    PROXY_USERNAME = os.getenv('PROXY_USERNAME', '')
    PROXY_PASSWORD = os.getenv('PROXY_PASSWORD', '')
    
    # Security Settings
    ENABLE_METADATA_CLEANING = os.getenv('ENABLE_METADATA_CLEANING', 'true').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # File Settings
    TEMP_DIR = os.getenv('TEMP_DIR', './temp')
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '50')) * 1024 * 1024  # 50MB default
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_vars = ['BOT_TOKEN', 'SOURCE_CHANNEL_ID', 'TARGET_CHANNEL_ID']
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
