#!/bin/bash

# Быстрый деплой через wget (скачивание config.py из интернета)

echo "==================================="
echo "Playerok Bot - Деплой через wget"
echo "==================================="
echo ""

# Клонирование проекта
echo "Клонирование проекта..."
git clone https://github.com/RammLide/PlayerokBOT.git
cd PlayerokBOT

# Создание config.py напрямую
echo "Создание config.py..."
cat > config.py << 'EOF'
# Конфигурация бота

# Telegram Bot Token (получить у @BotFather)
TELEGRAM_BOT_TOKEN = "8618435964:AAGVkbRFTjm51Zh4zf9m1y5e9Z2n_VSDmBA"

# Playerok Account Token
PLAYEROK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxZjEyYzM1My02MThhLTY2NzAtYjNmMi0yMTQ3NDk4YjAzMWUiLCJpZGVudGl0eSI6IjFmMTJjMzUzLTYxYzQtNmZmMC00MzJkLWFiMmQ3MzFkOTg1NSIsInJvbGUiOiJVU0VSIiwidiI6MSwiaWF0IjoxNzc0ODc0Mjk0LCJleHAiOjE4MDY0MTAyOTR9.BfIr7DlDC48Hj2DYTzmwaFGRyfl4S9ELrivEKJdtRFY"

# User Agent для запросов
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"

# Прокси для Playerok (опционально, формат: "user:pass@ip:port" или "ip:port")
PROXY = None

# Прокси для Telegram (опционально, формат: "socks5://user:pass@ip:port" или "http://ip:port")
TELEGRAM_PROXY = None

# ID администраторов бота (список Telegram ID)
ADMIN_IDS = [1121167993]
EOF

echo "✓ config.py создан"
echo ""

# Установка Python и зависимостей
echo "Установка зависимостей..."
sudo apt update
sudo apt install python3 python3-pip -y
pip3 install -r requirements.txt

echo "✓ Зависимости установлены"
echo ""

# Установка как системный сервис
echo "Установка systemd сервиса..."
CURRENT_DIR=$(pwd)

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

sudo systemctl daemon-reload
sudo systemctl enable playerok-bot
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
