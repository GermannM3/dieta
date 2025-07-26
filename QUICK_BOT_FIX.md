# 🚀 Быстрое исправление проблем с ботом

## 🚨 Текущие проблемы:
- **Профиль**: Бот не вытаскивает профиль из БД, пытается создать новый
- **Платежи**: Ошибки при попытках оплаты, старый токен YooKassa

## ✅ Пошаговое исправление:

### 1. Подключение к серверу
```bash
ssh root@5.129.198.80
cd /opt/dieta
source venv/bin/activate
```

### 2. Обновление кода
```bash
# Пул последних изменений
git pull origin main

# Проверяем что файлы обновились
ls -la components/payment_system/
ls -la components/handlers/user_handlers.py
```

### 3. Обновление настроек YooKassa
```bash
# Редактируем .env файл
nano .env
```

**Добавить/обновить строки:**
```env
# ===== YOOKASSA НАСТРОЙКИ =====
YOOKASSA_SHOP_ID=390540012
YOOKASSA_SECRET_KEY=live_4nHajHuzYGMrBPFLXQojoRW1_6ay2jy7SqSBUl16JOA
YOOKASSA_PAYMENT_TOKEN=390540012:LIVE:73839
```

### 4. Исправление Redis
```bash
# Проверяем Redis
sudo snap services redis

# Если не работает, запускаем
sudo snap start redis

# Если snap не работает, используем Docker
sudo docker run -d --name redis -p 6379:6379 redis:alpine
```

### 5. Перезапуск бота
```bash
# Останавливаем бота
sudo systemctl stop bot

# Убиваем все процессы Python
sudo pkill -f "python.*main"

# Проверяем что только один процесс
ps aux | grep "python.*main"

# Запускаем бота
sudo systemctl start bot

# Проверяем статус
sudo systemctl status bot
```

### 6. Проверка логов
```bash
# Смотрим логи бота
sudo journalctl -u bot -f

# Если есть ошибки, проверяем детали
sudo journalctl -u bot --tail=50
```

## 🔍 Проверка работоспособности

### Тест профиля
1. Отправьте `/start` боту
2. Отправьте `/profile` 
3. Должен показать форму создания профиля

### Тест платежей
1. Отправьте `/diet_consultant`
2. Должен показать информацию о подписке
3. Нажмите кнопку оплаты
4. Должен открыться платежный интерфейс

## 🎯 Ожидаемый результат

После исправления:
- ✅ **Профиль**: Бот корректно работает с профилем
- ✅ **Платежи**: Платежи работают с новым токеном YooKassa
- ✅ **Redis**: Работает через snap или Docker
- ✅ **Бот**: Один процесс, без ошибок

## 🚨 Если проблемы остаются

### Полная перезагрузка
```bash
# Останавливаем все
sudo systemctl stop bot
sudo pkill -f python
sudo pkill -f redis

# Подождать
sleep 5

# Запускаем заново
sudo snap start redis
sudo systemctl start bot
```

### Проверка конфигурации
```bash
# Проверяем переменные окружения
grep YOOKASSA .env

# Проверяем что Redis работает
redis-cli ping

# Проверяем процессы
ps aux | grep -E "(python|redis)"
```

### Автоматическое исправление
```bash
# Запускаем скрипт автоматического исправления
python quick_fix_bot_issues.py
```

## 📞 Поддержка

Если проблемы не решаются:
1. Проверьте логи: `sudo journalctl -u bot -f`
2. Проверьте статус сервисов: `sudo systemctl status bot redis`
3. Проверьте порты: `netstat -tlnp | grep -E "(6379|8000)"`

## ✅ Проверочный список

- [ ] Код обновлен (`git pull`)
- [ ] Настройки YooKassa обновлены в `.env`
- [ ] Redis работает (`redis-cli ping`)
- [ ] Бот перезапущен (`sudo systemctl restart bot`)
- [ ] Нет ошибок в логах (`sudo journalctl -u bot -f`)
- [ ] Профиль работает (`/profile`)
- [ ] Платежи работают (`/diet_consultant`) 