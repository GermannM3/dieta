# 🔧 Исправление проблем с аутентификацией и доменами

## 📋 Проблемы:
1. ❌ Нельзя авторизоваться под админом (germannm@vk.com)
2. ❌ Сайт не открывается по доменам tvoi-kalkulyator.ru и твой-калькулятор.рф

## ✅ Решения:

### 1. Исправление аутентификации

**Проблема:** Веб-приложение использует неправильный API URL для аутентификации.

**Решение:**
- ✅ Обновлен `.env.production` - исправлен API URL
- ✅ Добавлено логирование в `AuthForm.jsx` для диагностики
- ✅ Добавлена кнопка тестирования API
- ✅ Исправлены пути к эндпоинтам аутентификации

### 2. Настройка доменов

**Проблема:** Nginx конфигурация не поддерживает оба домена.

**Решение:**
- ✅ Обновлен `nginx-prod.conf` для поддержки обоих доменов
- ✅ Добавлена поддержка SPA (React Router)
- ✅ Добавлено gzip сжатие
- ✅ Исправлен порт для фронтенда (3000 вместо 5173)
- ✅ Обновлен `frontend.service` для порта 3000

## 🚀 Команды для применения исправлений:

### Безопасный деплой (рекомендуется):

```bash
# Сделать скрипт исполняемым
chmod +x deploy_webapp_safe.sh

# Запустить безопасный деплой
./deploy_webapp_safe.sh
```

### Ручной деплой:

```bash
# 1. Остановить сервисы
sudo systemctl stop frontend
sudo systemctl stop nginx

# 2. Обновить код (git репозиторий в /opt/dieta)
cd /opt/dieta
git pull origin main

# 3. Перейти в папку веб-приложения
cd /opt/dieta/calorie-love-tracker

# 4. Установить зависимости и собрать
npm install
npm run build

# 5. Обновить nginx конфигурацию
sudo cp /opt/dieta/nginx-prod.conf /etc/nginx/sites-available/tvoi-kalkulyator
sudo ln -sf /etc/nginx/sites-available/tvoi-kalkulyator /etc/nginx/sites-enabled/

# 6. Обновить systemd сервис
sudo cp /opt/dieta/frontend.service /etc/systemd/system/
sudo systemctl daemon-reload

# 7. Проверить nginx конфигурацию
sudo nginx -t

# 8. Запустить сервисы
sudo systemctl start frontend
sudo systemctl start nginx

# 9. Проверить статус
sudo systemctl status frontend
sudo systemctl status nginx
```

## 🔍 Диагностика проблем:

### Запустить диагностику:

```bash
python3 diagnose_auth_issues.py
```

### Проверить логи:

```bash
# Логи API
sudo journalctl -u api -f

# Логи фронтенда
sudo journalctl -u frontend -f

# Логи nginx
sudo journalctl -u nginx -f
```

### Проверить порты:

```bash
# Проверить, какие порты слушают сервисы
sudo netstat -tlnp | grep -E ':(80|3000|8000)'
```

## 🌐 Проверка доменов:

После применения исправлений сайт должен быть доступен по адресам:
- ✅ http://tvoi-kalkulyator.ru
- ✅ http://твой-калькулятор.рф
- ✅ http://5.129.198.80

## 🔐 Тестирование аутентификации:

1. Откройте сайт
2. Нажмите "Войти / Регистрация"
3. Попробуйте войти под админом:
   - Email: germannm@vk.com
   - Пароль: Germ@nnM3
4. Если не работает, нажмите "🔧 Тест подключения к API"

## 📊 Ожидаемые результаты:

После исправлений:
- ✅ Админ сможет войти в систему
- ✅ Сайт будет доступен по доменам
- ✅ API будет корректно работать
- ✅ Улучшена диагностика проблем

## 🆘 Если проблемы остались:

1. Проверьте DNS настройки в панели управления доменами
2. Убедитесь, что порты 80 и 443 открыты
3. Проверьте, что сервисы запущены
4. Посмотрите логи для детальной диагностики
5. Запустите диагностический скрипт: `python3 diagnose_auth_issues.py`

## 🔄 Откат изменений:

Если что-то пошло не так, можно откатиться:

```bash
# Восстановить резервную копию nginx
sudo cp /etc/nginx/sites-available/tvoi-kalkulyator.backup /etc/nginx/sites-available/tvoi-kalkulyator

# Перезапустить nginx
sudo systemctl restart nginx
``` 