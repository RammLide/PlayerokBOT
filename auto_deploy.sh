#!/bin/bash

# Полностью автоматический деплой с настройкой через аргументы командной строки

echo "==================================="
echo "Playerok Bot - Автоматический деплой"
echo "==================================="
echo ""

# Проверка аргументов
if [ "$#" -ne 3 ]; then
    echo "Использование: ./auto_deploy.sh <TELEGRAM_TOKEN> <PLAYEROK_TOKEN> <ADMIN_ID>"
    echo ""
    echo "Пример:"
    echo "./auto_deploy.sh \"123456:ABC-DEF...\" \"eyJhbGc...\" \"123456789\""
    exit 1
fi

TELEGRAM_TOKEN="$1"
PLAYEROK_TOKEN="$2"
ADMIN_ID="$3"

echo "Создание config.py..."
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

echo "✓ config.py создан"
echo ""

# Проверка Python
echo "Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 не найден. Установка..."
    sudo apt update
    sudo apt install python3 python3-pip -y
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ $PYTHON_VERSION установлен"
echo ""

# Установка зависимостей
echo "Установка зависимостей..."
pip3 install -r requirements.txt
echo "✓ Зависимости установлены"
echo ""

# Установка как системный сервис
echo "Установка systemd сервиса..."

# Получаем текущий путь
CURRENT_DIR=$(pwd)

# Создаем service файл с правильными путями
sudo bash -c "cat > /etc/systemd/system/playerok-bot.service << EOF
[Unit]
Description=Playerok Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 $CURRENT_DIR/bot.py
Restart=always
RestartSec=10
StandardOutput=append:$CURRENT_DIR/bot.log
StandardError=append:$CURRENT_DIR/bot.log

[Install]
WantedBy=multi-user.target
EOF"

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable playerok-bot

# Запуск сервиса
sudo systemctl start playerok-bot

echo "✓ Сервис установлен и запущен"
echo ""

# Показываем статус
echo "Статус бота:"
sudo systemctl status playerok-bot --no-pager -l

echo ""
echo "==================================="
echo "Деплой завершен!"
echo "==================================="
echo ""
echo "Управление ботом:"
echo "  sudo systemctl status playerok-bot   - статус"
echo "  sudo systemctl restart playerok-bot  - перезапуск"
echo "  sudo systemctl stop playerok-bot     - остановка"
echo "  tail -f bot.log                      - логи"
echo ""
