# Telegram Relay Bot

Бот для автоматической ретрансляции сообщений между Telegram каналами с поддержкой прокси и очистки метаданных.

## 🚀 Возможности

- **Автоматическая ретрансляция** сообщений между каналами
- **Поддержка всех типов контента**: текст, фото, видео, документы, аудио, голосовые сообщения
- **Очистка метаданных** из медиафайлов для безопасности
- **Поддержка прокси** (SOCKS5, HTTP) для обхода блокировок
- **Мониторинг и логирование** работы бота
- **Автоматический перезапуск** при сбоях

## 📋 Требования

- Python 3.8+
- Telegram Bot Token
- Исходный и целевой каналы
- Прокси (рекомендуется для продакшена)

## 🛠 Установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/telegram-relay-bot.git
cd telegram-relay-bot
```

### 2. Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка конфигурации
```bash
cp env.example .env
nano .env  # отредактируйте настройки
```

## ⚙️ Конфигурация

Создайте файл `.env` на основе `env.example`:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here
SOURCE_CHANNEL_ID=
TARGET_CHANNEL_ID=

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

### Получение Bot Token

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `.env`

### Получение ID каналов

1. Добавьте бота в канал как администратора
2. Отправьте любое сообщение в канал
3. Перешлите это сообщение боту [@userinfobot](https://t.me/userinfobot)
4. Скопируйте ID канала в `.env`

## 🚀 Запуск

### Локальный запуск (для тестирования)
```bash
python run.py
```

### Запуск на сервере (systemd)
```bash
# Создание systemd сервиса
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
WorkingDirectory=/path/to/telegram-relay-bot
ExecStart=/path/to/telegram-relay-bot/venv/bin/python /path/to/telegram-relay-bot/run.py
Restart=always
RestartSec=10
Environment=PATH=/path/to/telegram-relay-bot/venv/bin

[Install]
WantedBy=multi-user.target
```

```bash
# Запуск сервиса
sudo systemctl daemon-reload
sudo systemctl enable telegram-relay-bot
sudo systemctl start telegram-relay-bot

# Проверка статуса
sudo systemctl status telegram-relay-bot

# Просмотр логов
journalctl -u telegram-relay-bot -f
```

## 🔧 Управление сервисом

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

## 🔒 Безопасность

- **Никогда не коммитьте .env файл** в git
- **Используйте надежные прокси** для продакшена
- **Регулярно обновляйте зависимости**
- **Мониторьте логи** на предмет подозрительной активности

## 📁 Структура проекта

```
telegram-relay-bot/
├── telegram_bot.py      # Основной код бота
├── run.py              # Точка входа
├── config.py           # Конфигурация
├── metadata_cleaner.py # Очистка метаданных
├── monitor.py          # Мониторинг
├── utils.py            # Утилиты
├── requirements.txt    # Зависимости Python
├── env.example         # Пример конфигурации
├── MIGRATION_README.md # Инструкция по миграции
└── README.md          # Документация
```

## 🐛 Устранение неполадок

### Бот не запускается
```bash
# Проверьте конфигурацию
python3 -c "from config import Config; Config.validate()"

# Проверьте логи
journalctl -u telegram-relay-bot -n 50
```

### Проблемы с прокси
```bash
# Тест подключения к прокси
curl --socks5 proxy.example.com:1080 https://api.telegram.org/bot<TOKEN>/getMe
```

### Проблемы с правами
```bash
# Проверьте права на файлы
ls -la /path/to/telegram-relay-bot/

# Исправьте права
sudo chown -R $USER:$USER /path/to/telegram-relay-bot/
chmod +x /path/to/telegram-relay-bot/run.py
```

## 📝 Лицензия

MIT License

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add some amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📞 Поддержка

Если у вас возникли вопросы или проблемы:

1. Проверьте [Issues](https://github.com/yourusername/telegram-relay-bot/issues)
2. Создайте новый Issue с подробным описанием проблемы
3. Приложите логи и конфигурацию (без чувствительных данных)

## ⚠️ Важные замечания

- Бот должен быть добавлен в оба канала как администратор
- Для продакшена обязательно используйте прокси
- Регулярно проверяйте логи на предмет ошибок
- Делайте резервные копии конфигурации
