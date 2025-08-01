# 🔄 РАБОЧИЙ БЭКАП СОСТОЯНИЯ БОТА

## 📅 Дата создания: 26.07.2025 13:14 MSK

## ✅ Что работает:

### 1. **Основные функции бота**
- ✅ Профиль пользователя (создание, обновление, получение)
- ✅ Добавление еды с расчетом калорий
- ✅ История приемов пищи
- ✅ Трекер воды
- ✅ Трекер жировой массы
- ✅ Баллы и прогресс
- ✅ Статистика
- ✅ Шаблоны еды

### 2. **Система подписок (тестовый режим)**
- ✅ Создание тестовых подписок без YooKassa
- ✅ Активация подписок "Личный диетолог"
- ✅ Активация подписок "Генерация меню"
- ✅ Проверка статуса подписок
- ✅ Доступ к премиум функциям

### 3. **Debug-логи**
- ✅ Логирование создания платежей
- ✅ Отслеживание YooKassa настроек
- ✅ Логирование активации подписок

## 🔧 Текущие настройки:

### YooKassa (live-ключи)
```
YOOKASSA_SHOP_ID=390540012
YOOKASSA_SECRET_KEY=live_4nHajHuzYGMrBPFLXQojoRW1_6ay2jy7SqSBUl16JOA
YOOKASSA_PAYMENT_TOKEN=390540012:LIVE:73839
```

### API настройки
```
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://5.129.198.80:3000
```

### База данных
```
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_wNt53iaxXIBq@ep-lively-hall-aduj1169-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
```

## 🚨 Известные проблемы:

### 1. **YooKassa аккаунт не активирован**
- Ошибка 401 при создании реальных платежей
- Используется тестовый режим для обхода
- Нужно активировать аккаунт в YooKassa

### 2. **Обработчик "Мои подписки"**
- Может не срабатывать из-за конфликта фильтров
- Добавлен debug-обработчик для диагностики

## 📁 Ключевые файлы:

### Основные компоненты
- `main.py` - главный файл бота
- `components/handlers/user_handlers.py` - обработчики пользователя
- `components/payment_system/payment_operations.py` - платежная система
- `components/payment_system/payment_handlers.py` - обработчики платежей
- `database/init_database.py` - инициализация БД

### Конфигурация
- `.env` - переменные окружения
- `improved_api_server.py` - API сервер
- `docker-compose.yml` - Docker конфигурация

## 🔄 Как восстановить это состояние:

### 1. Остановить бота
```bash
sudo systemctl stop bot
```

### 2. Применить изменения
```bash
cd /opt/dieta
git pull origin main
```

### 3. Проверить .env
```bash
cat /opt/dieta/.env | grep YOOKASSA
```

### 4. Перезапустить бота
```bash
sudo systemctl start bot
sudo systemctl status bot
```

### 5. Проверить логи
```bash
sudo journalctl -u bot -f
```

## 🎯 Ожидаемое поведение:

### При нажатии "Личный диетолог":
```
✅ Тестовая подписка активирована!
Ваша подписка на личного диетолога активна на 7 дней.
Теперь вы можете задавать любые вопросы о питании!
```

### При нажатии "Сгенерировать меню":
```
✅ Тестовая подписка активирована!
Ваша подписка на генерацию меню активна на 7 дней.
Теперь вы можете заказывать персональные меню!
```

### В логах должно быть:
```
DEBUG: PaymentManager.create_payment called
DEBUG: Using temporary test mode - creating subscription without YooKassa
DEBUG: Creating test subscription for diet_consultant, amount: 200
DEBUG: Test subscription created and activated for user XXXXX
```

## 🚀 Следующие шаги:

1. **Активировать аккаунт YooKassa** - связаться с поддержкой
2. **Протестировать "Мои подписки"** - проверить debug-логи
3. **Включить реальные платежи** - после активации YooKassa
4. **Убрать тестовый режим** - вернуть обычную работу с YooKassa

## 📞 Контакты для восстановления:
- GitHub репозиторий: https://github.com/GermannM3/dieta
- Коммит: `1f073ce` - "Добавлен тестовый режим для платежей и debug-логи"
- Дата: 26.07.2025 13:14 MSK

---
**⚠️ ВАЖНО: Этот бэкап создан в рабочем состоянии с тестовым режимом платежей.**
**Для продакшена нужно активировать YooKassa и убрать тестовый режим.** 