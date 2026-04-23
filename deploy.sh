#!/bin/bash

# Скрипт быстрого деплоя на play2go.cloud

echo "==================================="
echo "Playerok Bot - Быстрый деплой"
echo "==================================="
echo ""

# Проверка Python
echo "Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 не найден. Установка..."
    sudo apt update
    sudo apt install python3 python3-pip python3-venv -y
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ $PYTHON_VERSION установлен"
echo ""

# Установка зависимостей
echo "Установка зависимостей..."
pip3 install -r requirements.txt
echo "✓ Зависимости установлены"
echo ""

# Проверка конфигурации
echo "Проверка конфигурации..."
if grep -q "YOUR_BOT_TOKEN_HERE" config.py 2>/dev/null; then
    echo "⚠ ВНИМАНИЕ: Необходимо настроить config.py!"
    echo "Отредактируйте файл config.py и укажите:"
    echo "  - TELEGRAM_BOT_TOKEN"
    echo "  - PLAYEROK_TOKEN"
    echo "  - ADMIN_IDS"
    echo ""
    read -p "Нажмите Enter после настройки config.py..."
fi

# Установка как системный сервис
echo ""
read -p "Установить бота как системный сервис? (y/n): " install_service

if [ "$install_service" = "y" ] || [ "$install_service" = "Y" ]; then
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
    echo "Управление сервисом:"
    echo "  sudo systemctl status playerok-bot   - статус"
    echo "  sudo systemctl stop playerok-bot     - остановка"
    echo "  sudo systemctl restart playerok-bot  - перезапуск"
    echo "  sudo journalctl -u playerok-bot -f   - логи"
    echo ""
    
    # Показываем статус
    sudo systemctl status playerok-bot --no-pager
else
    echo ""
    echo "Запуск бота в обычном режиме..."
    echo "Для запуска используйте: ./start.sh"
    echo "Или: python3 bot.py"
fi

echo ""
echo "==================================="
echo "Деплой завершен!"
echo "==================================="
