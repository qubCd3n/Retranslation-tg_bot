# Инструкция по загрузке на GitHub

## 🚀 Подготовка к загрузке

### 1. Инициализация Git репозитория
```bash
git init
git add .
git commit -m "Initial commit: Telegram Relay Bot"
```

### 2. Создание репозитория на GitHub
1. Перейдите на [GitHub](https://github.com)
2. Нажмите "New repository"
3. Название: `telegram-relay-bot`
4. Описание: `Telegram bot for relaying messages between channels with proxy support`
5. Выберите "Public" или "Private"
6. **НЕ** добавляйте README, .gitignore или лицензию (они уже есть)
7. Нажмите "Create repository"

### 3. Подключение к GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/telegram-relay-bot.git
git branch -M main
git push -u origin main
```

## 📁 Структура репозитория

```
telegram-relay-bot/
├── .gitignore              # Исключения для Git
├── README.md               # Основная документация
├── SECURITY.md             # Политика безопасности
├── MIGRATION_README.md     # Инструкция по миграции
├── GITHUB_SETUP.md         # Эта инструкция
├── telegram_bot.py         # Основной код бота
├── run.py                  # Точка входа
├── config.py               # Конфигурация
├── metadata_cleaner.py     # Очистка метаданных
├── monitor.py              # Мониторинг
├── utils.py                # Утилиты
├── requirements.txt        # Зависимости Python
└── env.example             # Пример конфигурации
```

## 🔒 Безопасность

### ✅ Что включено в репозиторий:
- Код бота (без чувствительных данных)
- Документация
- Примеры конфигурации
- .gitignore для защиты

### ❌ Что НЕ включено:
- .env файлы
- Токены ботов
- Пароли прокси
- ID каналов
- Лог файлы
- Виртуальное окружение

## 📋 Чек-лист перед загрузкой

- [ ] Все чувствительные данные удалены
- [ ] .env файл добавлен в .gitignore
- [ ] env.example содержит безопасные примеры
- [ ] README.md обновлен для GitHub
- [ ] SECURITY.md создан
- [ ] Все файлы протестированы
- [ ] Git репозиторий инициализирован

## 🚀 После загрузки

### 1. Настройте репозиторий
- Добавьте описание
- Настройте темы (topics)
- Добавьте лицензию (MIT рекомендуется)
- Настройте Issues и Wiki

### 2. Создайте релиз
1. Перейдите в "Releases"
2. Нажмите "Create a new release"
3. Тег: `v1.0.0`
4. Название: `Telegram Relay Bot v1.0.0`
5. Описание: краткое описание изменений
6. Нажмите "Publish release"

### 3. Настройте автоматизацию
- GitHub Actions для CI/CD
- Dependabot для обновления зависимостей
- Code scanning для безопасности

## 📝 Рекомендации

### 1. Коммиты
- Используйте понятные сообщения коммитов
- Делайте небольшие, логические коммиты
- Используйте conventional commits

### 2. Ветки
- `main` - стабильная версия
- `develop` - разработка
- `feature/*` - новые функции
- `hotfix/*` - исправления

### 3. Pull Requests
- Всегда создавайте PR для изменений
- Добавляйте описания и тесты
- Используйте шаблоны PR

## 🔧 Полезные команды Git

```bash
# Проверка статуса
git status

# Добавление файлов
git add .
git add specific_file.py

# Коммит
git commit -m "Add new feature"

# Пуш
git push origin main

# Создание ветки
git checkout -b feature/new-feature

# Слияние веток
git merge feature/new-feature

# Отмена изменений
git checkout -- file.py
git reset HEAD file.py
```

## 📞 Поддержка

После загрузки на GitHub:

1. Создайте Issues для багов и предложений
2. Настройте Discussions для вопросов
3. Добавьте CONTRIBUTING.md для участников
4. Настройте CODE_OF_CONDUCT.md

---

**Готово! Ваш проект готов к публикации на GitHub! 🎉**
