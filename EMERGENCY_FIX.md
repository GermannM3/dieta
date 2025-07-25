# 🚨 ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ СЕРВИСА

## 🔥 Проблема: 6 копий бота = полный крах

### Текущее состояние:
- ❌ **6 копий бота** → `TelegramConflictError`
- ❌ **Подписки не работают** → бот не видит `is_premium`
- ❌ **Команды сломаны** → "введите воду" вместо статистики

---

## ⚡ ЭКСТРЕННЫЕ КОМАНДЫ (выполнить СЕЙЧАС)

### 1. УБИТЬ ВСЕ КОПИИ БОТА
```bash
# Остановить все процессы бота
sudo pkill -f "python.*main.py"
sudo pkill -f "python.*main"

# Проверить что все убиты
ps aux | grep 'main.py' | grep -v grep
# Должно быть ПУСТО!
```

### 2. СОЗДАТЬ SYSTEMD UNIT ДЛЯ БОТА
```bash
sudo tee /etc/systemd/system/bot.service > /dev/null <<'EOF'
[Unit]
Description=Dieta Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/dieta
ExecStart=/opt/dieta/venv/bin/python main.py
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### 3. ЗАПУСТИТЬ БОТА ЧЕРЕЗ SYSTEMD
```bash
# Перезагрузить systemd
sudo systemctl daemon-reload

# Включить и запустить бота
sudo systemctl enable --now bot

# Проверить статус
sudo systemctl status bot
```

### 4. ПРОВЕРИТЬ ЧТО ТОЛЬКО ОДИН ПРОЦЕСС
```bash
# Должна быть ТОЛЬКО ОДНА строка
ps aux | grep 'main.py' | grep -v grep

# Проверить логи
sudo journalctl -u bot -f
```

---

## ✅ ПРОВЕРКА РАБОТОСПОСОБНОСТИ

### Тест 1: Бот отвечает
```bash
# В Telegram: /start
# Должен ответить приветствием
```

### Тест 2: Профиль работает
```bash
# В Telegram: /profile
# НЕ должно просить "введите воду"
# Должна показать статистику
```

### Тест 3: Меню премиум
```bash
# В Telegram: /menu
# Если премиум → открывается меню
# Если нет премиум → предложение купить
```

### Тест 4: Статистика
```bash
# В Telegram: /stats
# Должна показать баллы и день-стрек
# НЕ "введите воду"
```

---

## 🔧 ДОПОЛНИТЕЛЬНЫЕ ИСПРАВЛЕНИЯ

### Если бот не запускается:
```bash
# Проверить логи
sudo journalctl -u bot -n 50

# Проверить .env файл
cat .env | grep -E "(TG_TOKEN|ADMIN_ID)"
```

### Если подписки не работают:
```bash
# Проверить YooKassa настройки
cat .env | grep -E "(YOOKASSA|1097156)"

# Перезапустить API
sudo systemctl restart api
```

### Если команды не работают:
```bash
# Перезапустить бота
sudo systemctl restart bot

# Проверить логи
sudo journalctl -u bot -f
```

---

## 📊 МОНИТОРИНГ

### Проверка процессов
```bash
# Все процессы Python
ps aux | grep python | grep -v grep

# Только бот
ps aux | grep 'main.py' | grep -v grep

# Порты
netstat -tlnp | grep -E "(8000|5173|80)"
```

### Просмотр логов
```bash
# Бот
sudo journalctl -u bot -f

# API
sudo journalctl -u api -f

# Nginx
sudo journalctl -u nginx -f
```

---

## 🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После исправления:
- ✅ **1 процесс бота** (не 6!)
- ✅ **Подписки работают** (видит `is_premium`)
- ✅ **Команды работают** (не "введите воду")
- ✅ **Платежи работают** (YooKassa 1097156)

---

## 🚨 ЕСЛИ НИЧЕГО НЕ ПОМОГЛО

### Полная перезагрузка системы:
```bash
# Остановить все
sudo systemctl stop api frontend nginx bot
sudo pkill -f python
sudo pkill -f npm

# Подождать
sleep 10

# Запустить заново
sudo systemctl start api frontend nginx bot

# Проверить
sudo systemctl status api frontend nginx bot
```

### Проверка конфигурации:
```bash
# Service файлы
sudo cat /etc/systemd/system/bot.service
sudo cat /etc/systemd/system/api.service
sudo cat /etc/systemd/system/frontend.service

# Nginx
sudo nginx -t
sudo cat /etc/nginx/sites-enabled/tvoi-kalkulyator
``` 