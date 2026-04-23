# Инструкция по подключению к play2go.cloud через PowerShell/SSH/RDP

## Способ 1: SSH через PowerShell (рекомендуется)

### Проверка доступности SSH

Откройте PowerShell и попробуйте подключиться:

```powershell
# Замените YOUR_SERVER_IP на IP адрес вашего сервера
ssh root@YOUR_SERVER_IP

# Или если у вас другой пользователь
ssh username@YOUR_SERVER_IP
```

Если SSH работает, вы сможете:
1. Подключиться к серверу
2. Скопировать config.py через SCP
3. Выполнить все команды удаленно

### Копирование config.py через SCP

```powershell
# Из папки с проектом на вашем компьютере
cd "C:\Users\User\Desktop\Playerok BOT"

# Копирование config.py на сервер
scp config.py root@YOUR_SERVER_IP:/root/

# Или в конкретную папку
scp config.py root@YOUR_SERVER_IP:/root/PlayerokBOT/
```

### Полный деплой через SSH

```powershell
# Подключение к серверу
ssh root@YOUR_SERVER_IP

# На сервере выполните:
git clone https://github.com/RammLide/PlayerokBOT.git
cd PlayerokBOT

# Выход из SSH (Ctrl+D или exit)
exit

# Копирование config.py с вашего компьютера
scp "C:\Users\User\Desktop\Playerok BOT\config.py" root@YOUR_SERVER_IP:/root/PlayerokBOT/

# Снова подключение к серверу
ssh root@YOUR_SERVER_IP

# Деплой
cd PlayerokBOT
chmod +x deploy.sh
./deploy.sh
```

## Способ 2: RDP (Remote Desktop Protocol)

### Проверка доступности RDP

```powershell
# Проверка порта RDP (3389)
Test-NetConnection -ComputerName YOUR_SERVER_IP -Port 3389
```

Если RDP доступен:

1. Нажмите `Win + R`
2. Введите `mstsc`
3. Введите IP адрес сервера
4. Введите логин/пароль
5. После подключения откройте браузер на сервере
6. Скачайте проект или используйте общий буфер обмена для копирования файлов

### Включение общего буфера обмена в RDP

В окне подключения RDP:
1. Нажмите "Показать параметры"
2. Вкладка "Локальные ресурсы"
3. Буфер обмена → Включить
4. Теперь можно копировать текст между компьютерами

## Способ 3: PowerShell Remoting (если включен WinRM)

```powershell
# Проверка доступности WinRM
Test-WSMan -ComputerName YOUR_SERVER_IP

# Если работает, подключение:
Enter-PSSession -ComputerName YOUR_SERVER_IP -Credential (Get-Credential)
```

## Способ 4: Через панель управления хостинга

Зайдите на https://play2go.cloud в панель управления и проверьте:

1. **SSH доступ** - обычно есть раздел "SSH Keys" или "Access"
2. **Web Terminal** - многие хостинги предоставляют веб-терминал
3. **File Manager** - можно загрузить config.py через веб-интерфейс
4. **Console/Shell** - встроенная консоль в браузере

## Способ 5: Создание SSH ключа (безопаснее пароля)

```powershell
# Генерация SSH ключа
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Копирование ключа на сервер
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh root@YOUR_SERVER_IP "cat >> ~/.ssh/authorized_keys"

# Теперь можно подключаться без пароля
ssh root@YOUR_SERVER_IP
```

## Что нужно узнать:

1. **IP адрес сервера** - должен быть в панели управления play2go.cloud
2. **Порт SSH** - обычно 22, но может быть другой
3. **Имя пользователя** - обычно `root` или `ubuntu`
4. **Пароль** - который вы получили при создании сервера

## Проверка доступных портов

```powershell
# Проверка SSH (порт 22)
Test-NetConnection -ComputerName YOUR_SERVER_IP -Port 22

# Проверка RDP (порт 3389)
Test-NetConnection -ComputerName YOUR_SERVER_IP -Port 3389

# Проверка VNC (порт 5900)
Test-NetConnection -ComputerName YOUR_SERVER_IP -Port 5900
```

## Если ничего не работает

Используйте VNC, но с упрощенным способом:

1. Подключитесь через VNC
2. Откройте терминал
3. Выполните:
```bash
git clone https://github.com/RammLide/PlayerokBOT.git
cd PlayerokBOT
nano config.py
```
4. Вставьте содержимое из config.example.py
5. Измените только значения токенов (короткие части)
6. Сохраните и запустите деплой

Или создайте config.py локально и используйте pastebin/gist для передачи.
