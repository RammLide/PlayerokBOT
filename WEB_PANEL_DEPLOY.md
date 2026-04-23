# Инструкция по деплою через веб-панель play2go.cloud

## Шаг 1: Войдите в панель управления

Откройте в браузере: https://play2go.cloud
Войдите с вашими учетными данными

## Шаг 2: Найдите веб-терминал/консоль

Ищите один из этих разделов:
- **Console** / Консоль
- **Terminal** / Терминал  
- **Shell** / Оболочка
- **SSH Access** / SSH доступ
- **Web Terminal** / Веб-терминал
- Кнопка с иконкой терминала (>_)

Обычно находится:
- В меню слева
- В верхней панели
- На странице вашего сервера/VPS

## Шаг 3: Откройте терминал

Кликните на терминал - откроется консоль прямо в браузере

## Шаг 4: Выполните команду деплоя

В открывшемся терминале скопируйте и вставьте:

```bash
wget -O - https://raw.githubusercontent.com/RammLide/PlayerokBOT/main/quick_deploy.sh | bash
```

Или если wget не работает:

```bash
curl -sSL https://raw.githubusercontent.com/RammLide/PlayerokBOT/main/quick_deploy.sh | bash
```

Или вручную:

```bash
git clone https://github.com/RammLide/PlayerokBOT.git
cd PlayerokBOT
chmod +x quick_deploy.sh
./quick_deploy.sh
```

## Шаг 5: Проверка

После завершения проверьте статус:

```bash
sudo systemctl status playerok-bot
```

Просмотр логов:

```bash
tail -f /root/PlayerokBOT/bot.log
```

## Альтернатива: File Manager

Если есть File Manager в панели:

1. Откройте File Manager
2. Загрузите файл config.py через веб-интерфейс
3. Откройте терминал
4. Выполните:
```bash
git clone https://github.com/RammLide/PlayerokBOT.git
cd PlayerokBOT
# config.py уже загружен
chmod +x deploy.sh
./deploy.sh
```

## Что искать в панели управления:

- Раздел "Servers" или "VPS" - выберите ваш сервер 144.31.147.33
- Кнопка "Console" или "Terminal" 
- Может быть кнопка "Launch Console" или "Open Terminal"
- Иногда нужно кликнуть на имя сервера, чтобы увидеть кнопку консоли

## Скриншот того, что нужно найти:

Ищите что-то похожее на:
```
┌─────────────────────────────────┐
│  Server: 144.31.147.33          │
│  [Console] [VNC] [Settings]     │
└─────────────────────────────────┘
```

Или:
```
Sidebar:
├── Dashboard
├── Servers
│   └── Your Server
│       ├── Overview
│       ├── Console  ← ЭТО!
│       ├── VNC
│       └── Settings
```

После того как найдете консоль, просто вставьте команду деплоя!
