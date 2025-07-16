# 🚀 Быстрый запуск - Диетолог Бот

## ✅ Два способа запуска:

### 1. БЕЗ Docker (проще для Windows):
```bash
# Просто дважды кликните на файл:
start_without_docker.bat

# Для остановки:
stop_all.bat
```

### 2. С Docker (рекомендуется для продакшена):
```bash
# Сначала запустите Docker Desktop!

# Затем:
docker-compose -f docker-compose.dev.yml up -d
```

## 📋 Что должно работать после запуска:

1. **Telegram Bot** - @tvoy_diet_bot
2. **API Server** - http://localhost:8000
3. **API Docs** - http://localhost:8000/docs
4. **Web App** - http://localhost:5173

## 🔧 Если что-то не работает:

### React фронтенд не открывается:
```bash
cd calorie-love-tracker
npm install
npm run dev
```

### Бот не отвечает:
- Проверьте .env файл
- Убедитесь что TG_TOKEN правильный
- Проверьте логи в окне "Telegram Bot"

### API не работает:
- Проверьте DATABASE_URL в .env
- Проверьте логи в окне "API Server"

## 💡 Полезные команды:

### Проверить статус:
```bash
# Порты
netstat -an | findstr "8000 5173"

# Процессы
tasklist | findstr "python node"
```

### Логи:
- Каждый сервис открывается в отдельном окне CMD
- Там видны все логи в реальном времени

## 🎯 Готово!

Теперь вы можете:
1. Писать боту в Telegram
2. Открыть веб-приложение http://localhost:5173
3. Посмотреть API документацию http://localhost:8000/docs

---
*Для Docker инструкций смотрите DOCKER_DEPLOYMENT.md* 