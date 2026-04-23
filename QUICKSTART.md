# Краткая инструкция по деплою на play2go.cloud

## Быстрый старт

### 1. Подключитесь к серверу через VNC

Откройте VNC клиент и подключитесь к вашему серверу на play2go.cloud

### 2. Откройте терминал

В VNC окне откройте терминал (обычно правый клик → Terminal или через меню)

### 3. Загрузите проект

```bash
# Установка git
sudo apt update && sudo apt install git -y

# Клонирование репозитория
git clone https://github.com/RammLide/PlayerokBOT.git
cd PlayerokBOT
```

### 4. Настройте конфигурацию

```bash
nano config.py
```

Укажите ваши токены:
- `TELEGRAM_BOT_TOKEN` - токен от @BotFather
- `PLAYEROK_TOKEN` - токен с сайта playerok.com
- `ADMIN_IDS` - ваш Telegram ID

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

### 5. Запустите автоматический деплой

```bash
chmod +x deploy.sh
./deploy.sh
```

Скрипт автоматически:
- Установит Python и зависимости
- Настроит systemd сервис
- Запустит бота

### 6. Проверьте работу

Откройте Telegram и отправьте боту `/start`

## Управление ботом

```bash
# Статус
sudo systemctl status playerok-bot

# Остановка
sudo systemctl stop playerok-bot

# Запуск
sudo systemctl start playerok-bot

# Перезапуск
sudo systemctl restart playerok-bot

# Логи в реальном времени
sudo journalctl -u playerok-bot -f

# Или просмотр файла логов
tail -f bot.log
```

## Обновление бота

```bash
cd PlayerokBOT
git pull
sudo systemctl restart playerok-bot
```

## Решение проблем

### Бот не запускается

```bash
# Проверьте логи
tail -50 bot.log

# Или через systemd
sudo journalctl -u playerok-bot -n 50
```

### Проверка токенов

```bash
# Убедитесь что токены правильные
cat config.py
```

### Переустановка зависимостей

```bash
pip3 install --force-reinstall -r requirements.txt
sudo systemctl restart playerok-bot
```

## Полная документация

Смотрите файл `DEPLOY.md` для подробной информации.
