# 🔧 Быстрое применение debug-фиксов

## 📋 Что изменено:

### 1. **Debug-логи в обработчике "Мои подписки"**
- Добавлены print-сообщения для отслеживания выполнения
- Логирование проверки подписок в базе данных
- Подробная информация об ошибках

### 2. **Debug-логи в PaymentManager.create_payment**
- Вывод всех YooKassa настроек
- Логирование процесса создания платежа
- Детальная информация об ошибках

### 3. **Обновлены YooKassa настройки**
- YOOKASSA_SHOP_ID=390540012
- YOOKASSA_SECRET_KEY=live_4nHajHuzYGMrBPFLXQojoRW1_6ay2jy7SqSBUl16JOA
- YOOKASSA_PAYMENT_TOKEN=390540012:LIVE:73839

## 🚀 Быстрое применение на сервере:

### 1. Остановить бота
```bash
sudo systemctl stop bot
```

### 2. Применить изменения
```bash
cd /opt/dieta
git pull origin main
```

### 3. Обновить .env на сервере
```bash
sudo nano /opt/dieta/.env
```

Заменить YooKassa настройки на:
```
YOOKASSA_SHOP_ID=390540012
YOOKASSA_SECRET_KEY=live_4nHajHuzYGMrBPFLXQojoRW1_6ay2jy7SqSBUl16JOA
YOOKASSA_PAYMENT_TOKEN=390540012:LIVE:73839
```

### 4. Перезапустить бота
```bash
sudo systemctl start bot
sudo systemctl status bot
```

## 🔍 Проверка работы:

### 1. Проверить логи бота
```bash
sudo journalctl -u bot -f
```

### 2. Протестировать "Мои подписки"
- Нажать кнопку "💳 Мои подписки" в боте
- В логах должны появиться debug-сообщения:
  ```
  DEBUG: my_subscriptions_handler called
  DEBUG: Checking subscriptions for user XXXXX
  DEBUG: diet_subscription found: False
  DEBUG: menu_subscription found: False
  DEBUG: Sending response: 📋 Ваши подписки:...
  ```

### 3. Протестировать создание платежа
- Нажать "Личный диетолог" или "Сгенерировать меню"
- В логах должны появиться debug-сообщения:
  ```
  DEBUG: PaymentManager.create_payment called
  DEBUG: YOOKASSA_SHOP_ID = 390540012
  DEBUG: YOOKASSA_SECRET_KEY = live_4nHajHuzYGMrBPFLXQojoRW1_6ay2jy7SqSBUl16JOA
  DEBUG: YOOKASSA_PAYMENT_TOKEN = 390540012:LIVE:73839
  DEBUG: Configuration.account_id = 390540012
  DEBUG: Configuration.secret_key = live_4nHajHuzYGMrBPFLXQojoRW1_6ay2jy7SqSBUl16JOA
  DEBUG: Creating payment for diet_consultant, amount: 200
  ```

## 🎯 Ожидаемый результат:

### ✅ "Мои подписки" должна работать:
- Показывать актуальную информацию о подписках
- Не показывать приветственное сообщение
- В логах должны быть debug-сообщения

### ✅ YooKassa должна работать:
- Создавать платежи без ошибки 401
- Использовать актуальные live-ключи
- В логах должны быть debug-сообщения о создании платежа

## 🚨 Если проблемы остаются:

### Проверить .env на сервере:
```bash
cat /opt/dieta/.env | grep YOOKASSA
```

### Проверить переменные окружения:
```bash
sudo systemctl show bot | grep Environment
```

### Проверить логи API:
```bash
sudo journalctl -u api -f
```

### Проверить статус сервисов:
```bash
sudo systemctl status bot api
```

## 📞 Если нужна помощь:
- Отправить логи с debug-сообщениями
- Указать какие именно функции не работают
- Приложить скриншоты ошибок 