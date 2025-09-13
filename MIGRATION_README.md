# Инструкция по миграции на сервер

## Файлы для переноса на сервер

### Основные файлы (обязательно):
- `telegram_bot.py` - основной код бота
- `run.py` - точка входа
- `config.py` - конфигурация
- `metadata_cleaner.py` - очистка метаданных
- `monitor.py` - мониторинг
- `utils.py` - утилиты
- `requirements.txt` - зависимости Python

### Конфигурация:
- `env_example.txt` - пример конфигурации (скопировать в .env)

### Документация:
- `README.md` - основная документация

## Шаги миграции:

### 1. Загрузка файлов на сервер
```bash
# Загрузите все файлы в папку /opt/telegram-relay-bot/
scp -r * user@server:/opt/telegram-relay-bot/
```

### 2. Создание .env файла
```bash
cd /opt/telegram-relay-bot
cp env.example .env
nano .env  # отредактируйте настройки
```

### 3. Установка зависимостей
```bash
# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### 4. Настройка .env файла
```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here
SOURCE_CHANNEL_ID=-1001234567890
TARGET_CHANNEL_ID=-1001234567891

# Proxy Configuration (обязательно для продакшена)
PROXY_URL=socks5://proxy.example.com:1080
PROXY_USERNAME=your_proxy_username
PROXY_PASSWORD=your_proxy_password

# Security Settings
ENABLE_METADATA_CLEANING=true
LOG_LEVEL=INFO

# File Settings
TEMP_DIR=./temp
MAX_FILE_SIZE=50
```

### 5. Создание systemd сервиса
```bash
sudo nano /etc/systemd/system/telegram-relay-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=Telegram Relay Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/opt/telegram-relay-bot
ExecStart=/opt/telegram-relay-bot/venv/bin/python /opt/telegram-relay-bot/run.py
Restart=always
RestartSec=10
Environment=PATH=/opt/telegram-relay-bot/venv/bin

[Install]
WantedBy=multi-user.target
```

### 6. Запуск сервиса
```bash
# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите автозапуск
sudo systemctl enable telegram-relay-bot

# Запустите бота
sudo systemctl start telegram-relay-bot

# Проверьте статус
sudo systemctl status telegram-relay-bot

# Просмотрите логи
journalctl -u telegram-relay-bot -f
```

## Управление сервисом

```bash
# Запуск
sudo systemctl start telegram-relay-bot

# Остановка
sudo systemctl stop telegram-relay-bot

# Перезапуск
sudo systemctl restart telegram-relay-bot

# Статус
sudo systemctl status telegram-relay-bot

# Логи
journalctl -u telegram-relay-bot -f
```

## Проверка работы

1. Проверьте статус сервиса
2. Просмотрите логи на предмет ошибок
3. Отправьте тестовое сообщение в исходный канал
4. Убедитесь, что сообщение переслалось в целевой канал
