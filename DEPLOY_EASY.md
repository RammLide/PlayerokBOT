# Быстрый деплой на play2go.cloud (без VNC копирования)

## Способ 1: Через SSH (если доступен)

Если на play2go.cloud есть SSH доступ:

```bash
# На вашем локальном компьютере
scp config.py user@your-server:/path/to/PlayerokBOT/
```

## Способ 2: Через wget/curl (рекомендуется)

### Шаг 1: Создайте временный приватный Gist

1. Откройте https://gist.github.com
2. Создайте **SECRET** gist с вашим config.py
3. Скопируйте ссылку на RAW файл

### Шаг 2: На сервере через VNC

```bash
# Клонирование проекта
git clone https://github.com/RammLide/PlayerokBOT.git
cd PlayerokBOT

# Скачивание config.py из gist
wget -O config.py "ССЫЛКА_НА_RAW_GIST"

# Автоматический деплой
chmod +x deploy.sh
./deploy.sh
```

### Шаг 3: Удалите Gist после деплоя!

## Способ 3: Через auto_deploy.sh (самый простой)

На сервере через VNC выполните одну команду:

```bash
git clone https://github.com/RammLide/PlayerokBOT.git && cd PlayerokBOT && chmod +x auto_deploy.sh && ./auto_deploy.sh "ВАШ_TELEGRAM_TOKEN" "ВАШ_PLAYEROK_TOKEN" "ВАШ_TELEGRAM_ID"
```

Замените:
- `ВАШ_TELEGRAM_TOKEN` - токен от @BotFather
- `ВАШ_PLAYEROK_TOKEN` - токен с playerok.com
- `ВАШ_TELEGRAM_ID` - ваш Telegram ID

Пример:
```bash
git clone https://github.com/RammLide/PlayerokBOT.git && cd PlayerokBOT && chmod +x auto_deploy.sh && ./auto_deploy.sh "8618435964:AAGVkbRFTjm51Zh4zf9m1y5e9Z2n_VSDmBA" "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." "1121167993"
```

## Способ 4: Через setup_config.sh (интерактивный)

```bash
git clone https://github.com/RammLide/PlayerokBOT.git
cd PlayerokBOT
chmod +x setup_config.sh
./setup_config.sh
# Введите токены когда попросит
chmod +x deploy.sh
./deploy.sh
```

## Способ 5: Через переменные окружения

```bash
git clone https://github.com/RammLide/PlayerokBOT.git
cd PlayerokBOT

# Установка через переменные окружения
export TELEGRAM_TOKEN="ваш_токен"
export PLAYEROK_TOKEN="ваш_токен"
export ADMIN_ID="ваш_id"

# Создание config.py
cat > config.py << EOF
TELEGRAM_BOT_TOKEN = "$TELEGRAM_TOKEN"
PLAYEROK_TOKEN = "$PLAYEROK_TOKEN"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
PROXY = None
TELEGRAM_PROXY = None
ADMIN_IDS = [$ADMIN_ID]
EOF

# Деплой
chmod +x deploy.sh
./deploy.sh
```

## Рекомендация

Используйте **Способ 3** - просто скопируйте одну длинную команду в терминал VNC. Это самый быстрый способ!
