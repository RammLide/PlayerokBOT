#!/bin/bash

# Скрипт запуска бота Playerok

echo "Запуск Playerok Bot..."

# Переход в директорию проекта
cd "$(dirname "$0")"

# Активация виртуального окружения (если есть)
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Запуск бота
python3 bot.py
