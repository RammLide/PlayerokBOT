# Подключение к серверу 144.31.147.33

## SSH подключение доступно!

Порт 22 открыт. Выполните следующие команды в PowerShell:

### 1. Подключение к серверу

```powershell
ssh root@144.31.147.33
```

Или если пользователь другой:
```powershell
ssh ubuntu@144.31.147.33
# или
ssh admin@144.31.147.33
```

Введите пароль когда попросит.

### 2. После успешного подключения, на сервере выполните:

```bash
# Клонирование проекта
git clone https://github.com/RammLide/PlayerokBOT.git
cd PlayerokBOT

# Выход из SSH
exit
```

### 3. Копирование config.py с вашего компьютера на сервер

Откройте новое окно PowerShell и выполните:

```powershell
# Переход в папку с проектом
cd "C:\Users\User\Desktop\Playerok BOT"

# Копирование config.py на сервер
scp config.py root@144.31.147.33:/root/PlayerokBOT/
```

Если пользователь не root:
```powershell
scp config.py ubuntu@144.31.147.33:/home/ubuntu/PlayerokBOT/
```

### 4. Снова подключитесь к серверу и запустите деплой

```powershell
ssh root@144.31.147.33
```

На сервере:
```bash
cd PlayerokBOT
chmod +x deploy.sh
./deploy.sh
```

## Альтернатива: Все в одном окне PowerShell

```powershell
# 1. Подключение и клонирование
ssh root@144.31.147.33 "git clone https://github.com/RammLide/PlayerokBOT.git"

# 2. Копирование config.py
scp "C:\Users\User\Desktop\Playerok BOT\config.py" root@144.31.147.33:/root/PlayerokBOT/

# 3. Деплой
ssh root@144.31.147.33 "cd PlayerokBOT && chmod +x deploy.sh && ./deploy.sh"
```

## Если нужен пароль

При первом подключении SSH может спросить:
```
The authenticity of host '144.31.147.33' can't be established.
Are you sure you want to continue connecting (yes/no)?
```

Введите: `yes`

Затем введите пароль от сервера.

## Проверка после деплоя

```powershell
# Проверка статуса бота
ssh root@144.31.147.33 "systemctl status playerok-bot"

# Просмотр логов
ssh root@144.31.147.33 "tail -f /root/PlayerokBOT/bot.log"
```
