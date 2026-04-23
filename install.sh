#!/bin/bash

# Скрипт установки зависимостей для Playerok Bot

echo "Установка зависимостей для Playerok Bot..."

# Обновление pip
python3 -m pip install --upgrade pip

# Установка зависимостей
pip3 install -r requirements.txt

echo "Установка завершена!"
