# Инструкция по деплою на play2go.cloud

## Подготовка

1. Убедитесь, что у вас есть доступ к VNC на play2go.cloud
2. Убедитесь, что на сервере установлен Python 3.11 или выше

## Шаги деплоя

### 1. Подключение к серверу через VNC

Подключитесь к вашему серверу на play2go.cloud через VNC клиент.

### 2. Загрузка проекта на сервер

Есть несколько способов:

#### Способ 1: Через Git (рекомендуется)

```bash
# Установка git (если не установлен)
sudo apt update
sudo apt install git -y

# Клонирование репозитория
git clone https://github.com/RammLide/PlayerokBOT.git
cd PlayerokBOT
```

#### Способ 2: Через загрузку архива

1. Скачайте проект как ZIP с GitHub
2. Загрузите через VNC (перетащите файл в окно VNC)
3. Распакуйте архив:
```bash
unzip PlayerokBOT-main.zip
cd PlayerokBOT-main
```

### 3. Установка зависимостей

```bash
# Установка Python и pip (если не установлены)
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# Создание виртуального окружения
python3 -m venv .venv
source .venv/bin/activate

# Установка зависимостей
chmod +x install.sh
./install.sh
```

### 4. Настройка конфигурации

Отредактируйте файл `config.py`:

```bash
nano config.py
```

Убедитесь, что указаны правильные токены:
- `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота
- `PLAYEROK_TOKEN` - токен вашего аккаунта Playerok
- `ADMIN_IDS` - ваш Telegram ID

### 5. Запуск бота

#### Простой запуск (для тестирования)

```bash
chmod +x start.sh
./start.sh
```

#### Запуск в фоновом режиме с помощью screen

```bash
# Установка screen (если не установлен)
sudo apt install screen -y

# Создание новой сессии
screen -S playerok_bot

# Запуск бота
./start.sh

# Отключение от сессии (бот продолжит работать)
# Нажмите: Ctrl+A, затем D
```

Для возврата к сессии:
```bash
screen -r playerok_bot
```

#### Запуск как системный сервис (рекомендуется для продакшена)

Создайте файл сервиса:

```bash
sudo nano /etc/systemd/system/playerok-bot.service
```

Вставьте следующее содержимое (замените `/path/to/PlayerokBOT` на реальный путь):

```ini
[Unit]
Description=Playerok Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/PlayerokBOT
ExecStart=/path/to/PlayerokBOT/.venv/bin/python3 /path/to/PlayerokBOT/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запустите сервис:

```bash
# Перезагрузка конфигурации systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable playerok-bot

# Запуск сервиса
sudo systemctl start playerok-bot

# Проверка статуса
sudo systemctl status playerok-bot
```

Управление сервисом:
```bash
# Остановка
sudo systemctl stop playerok-bot

# Перезапуск
sudo systemctl restart playerok-bot

# Просмотр логов
sudo journalctl -u playerok-bot -f
```

### 6. Проверка работы

1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте команду `/start`
4. Проверьте, что бот отвечает

### 7. Просмотр логов

Логи бота сохраняются в файл `bot.log`:

```bash
# Просмотр последних строк
tail -f bot.log

# Просмотр всего файла
cat bot.log
```

## Обновление бота

Если вы используете Git:

```bash
cd PlayerokBOT
git pull
sudo systemctl restart playerok-bot
```

## Решение проблем

### Бот не запускается

1. Проверьте логи: `tail -f bot.log`
2. Убедитесь, что все зависимости установлены: `pip3 list`
3. Проверьте правильность токенов в `config.py`

### Бот не отвечает

1. Проверьте, что процесс запущен: `ps aux | grep bot.py`
2. Проверьте подключение к интернету
3. Убедитесь, что токены действительны

### Ошибки с зависимостями

```bash
# Переустановка зависимостей
pip3 install --force-reinstall -r requirements.txt
```

## Безопасность

⚠️ **ВАЖНО**: Не публикуйте файл `config.py` с реальными токенами в публичный репозиторий!

Рекомендуется:
1. Добавить `config.py` в `.gitignore`
2. Создать `config.example.py` с примерами значений
3. Хранить реальные токены только на сервере

## Автоматический перезапуск при сбое

Если вы используете systemd сервис, бот автоматически перезапустится при сбое (параметр `Restart=always`).

Если используете screen, можно создать скрипт мониторинга:

```bash
#!/bin/bash
# monitor.sh

while true; do
    if ! pgrep -f "python3 bot.py" > /dev/null; then
        echo "Бот не запущен, перезапуск..."
        cd /path/to/PlayerokBOT
        source .venv/bin/activate
        python3 bot.py &
    fi
    sleep 60
done
```

Запустите его в отдельной screen сессии:
```bash
screen -S monitor
./monitor.sh
```
