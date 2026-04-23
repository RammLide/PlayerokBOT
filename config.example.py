# Конфигурация бота (ПРИМЕР)
# Скопируйте этот файл в config.py и заполните своими данными

# Telegram Bot Token (получить у @BotFather)
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Playerok Account Token
# Как получить:
# 1. Откройте playerok.com в браузере
# 2. Войдите в аккаунт
# 3. Откройте DevTools (F12)
# 4. Application/Storage → Cookies → найдите 'token'
PLAYEROK_TOKEN = "YOUR_PLAYEROK_TOKEN_HERE"

# User Agent для запросов
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"

# Прокси для Playerok (опционально, формат: "user:pass@ip:port" или "ip:port")
PROXY = None

# Прокси для Telegram (опционально, формат: "socks5://user:pass@ip:port" или "http://ip:port")
# Если Telegram заблокирован, укажите здесь прокси
TELEGRAM_PROXY = None

# ID администраторов бота (список Telegram ID)
# Как узнать свой ID: напишите боту @userinfobot
ADMIN_IDS = [123456789]
