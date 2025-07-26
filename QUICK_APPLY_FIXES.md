# 🚀 Быстрое применение исправлений на сервере

## 📋 Что исправлено

1. **Токен YooKassa** - обновлен на новый из BotFather
2. **Логика профиля** - убрана зависимость от API
3. **Redis** - добавлен автоматический запуск

## ⚡ Быстрое применение (5 минут)

### 1. Подключение и обновление
```bash
ssh root@5.129.198.80
cd /opt/dieta
source venv/bin/activate
git pull origin main
```

### 2. Обновление настроек
```bash
nano .env
```

**Добавить в конец файла:**
```env
# ===== YOOKASSA НАСТРОЙКИ =====
YOOKASSA_SHOP_ID=390540012
YOOKASSA_SECRET_KEY=live_4nHajHuzYGMrBPFLXQojoRW1_6ay2jy7SqSBUl16JOA
YOOKASSA_PAYMENT_TOKEN=390540012:LIVE:73839
```

### 3. Перезапуск
```bash
# Redis
sudo snap start redis

# Бот
sudo systemctl stop bot
sudo pkill -f "python.*main"
sudo systemctl start bot

# Проверка
sudo systemctl status bot
```

### 4. Тестирование
```bash
# Логи бота
sudo journalctl -u bot -f
```

## 🎯 Проверка в Telegram

1. Отправьте `/start` боту
2. Отправьте `/profile` - должен показать форму
3. Отправьте `/diet_consultant` - должен показать платеж

## ✅ Готово!

Если все работает - исправления применены успешно!

---

**Время выполнения**: ~5 минут  
**Сложность**: Низкая  
**Риск**: Минимальный 