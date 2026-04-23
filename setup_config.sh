#!/bin/bash

# Скрипт быстрой настройки config.py через переменные окружения

echo "==================================="
echo "Настройка конфигурации бота"
echo "==================================="
echo ""

# Запрашиваем данные
read -p "Введите Telegram Bot Token: " TELEGRAM_TOKEN
read -p "Введите Playerok Token: " PLAYEROK_TOKEN
read -p "Введите ваш Telegram ID: " ADMIN_ID

# Создаем config.py
cat > config.py << EOF
# Конфигурация бота

# Telegram Bot Token (получить у @BotFather)
TELEGRAM_BOT_TOKEN = "$TELEGRAM_TOKEN"

# Playerok Account Token
PLAYEROK_TOKEN = "$PLAYEROK_TOKEN"

# User Agent для запросов
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"

# Прокси для Playerok (опционально, формат: "user:pass@ip:port" или "ip:port")
PROXY = None

# Прокси для Telegram (опционально, формат: "socks5://user:pass@ip:port" или "http://ip:port")
# Если Telegram заблокирован, укажите здесь прокси
TELEGRAM_PROXY = None

# ID администраторов бота (список Telegram ID)
ADMIN_IDS = [$ADMIN_ID]
EOF

echo ""
echo "✓ Файл config.py создан!"
echo ""
