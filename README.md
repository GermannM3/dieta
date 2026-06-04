# 🥗 Твой Диетолог - Telegram Bot

Персональный диетолог в твоем кармане! Умный телеграм-бот, который поможет следить за питанием, считать калории и достигать целей по здоровому образу жизни.

## 🌟 Возможности

### 📊 Умный подсчет калорий
- Автоматический расчет калорий через нейросеть GigaChat
- Анализ белков, жиров и углеводов
- Поддержка более 100,000 продуктов из базы FoodData Central
- Распознавание еды на фотографиях

### 👨‍⚕️ Персональный диетолог
- Консультации по питанию на основе вашего профиля
- Персональные рекомендации по рациону
- Генерация меню под ваши цели
- Мотивация и поддержка на пути к цели

### 📈 Полный трекинг здоровья
- Отслеживание воды и настроения
- Система баллов и достижений
- Статистика прогресса
- Шаблоны для быстрого добавления блюд

### 🌐 Веб-приложение
- Красивый интерфейс для управления питанием
- Синхронизация с телеграм-ботом
- Адаптивный дизайн для всех устройств

### 📱 Android-приложение (Flutter)
- Тот же дизайн, что и веб-версия (зелёно-синяя палитра shadcn)
- Сборка APK на GitHub Actions — локально Flutter не нужен
- Скачать последний релиз: **[Releases → Android](https://github.com/GermannM3/dieta/releases)**

| Файл | Описание |
|------|----------|
| `app-release.apk` | Установка на телефон напрямую |
| `app-release.aab` | Для Google Play |

**Как собрать релиз:**
```bash
git tag android-v1.0.0
git push origin android-v1.0.0
```
Или: Actions → **Android Release** → Run workflow.

Подробнее: [`mobile/README.md`](mobile/README.md)

## 🚀 Быстрый старт

### 1. Клонирование проекта
   ```bash
git clone https://github.com/GermannM3/dieta.git
cd dieta
   ```

### 2. Настройка окружения
     ```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
     venv\Scripts\activate

# Активация (Linux/Mac)
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Конфигурация
     ```bash
# Копирование примера конфигурации
cp env.example .env

# Отредактируйте .env файл, добавив ваши ключи:
# - TG_TOKEN от @BotFather
# - ADMIN_ID ваш ID в Telegram
# - DATABASE_URL подключение к базе данных
# - API ключи для GigaChat, Mistral и CalorieNinjas
```

### 4. Запуск

#### Простой способ (Windows):
   ```bash
start_without_docker.bat
```

#### Через Docker:
```bash
docker-compose up -d
```

#### Ручной запуск:
```bash
# В разных терминалах:
python improved_api_server.py  # API сервер
python main.py                 # Telegram бот
cd calorie-love-tracker && npm run dev  # Веб-приложение
```

## 🛠 Деплой на сервер

### Автоматический деплой с GitHub
   ```bash
# Создайте скрипт auto-deploy.sh на сервере:
curl -O https://raw.githubusercontent.com/GermannM3/dieta/main/auto-deploy.sh
chmod +x auto-deploy.sh
./auto-deploy.sh
```

### Ручной деплой
Подробные инструкции в файлах:
- `QUICK_DEPLOY.md` - быстрая памятка
- `MANUAL_DEPLOY.md` - пошаговое руководство
- `DEPLOYMENT_GUIDE.md` - полная документация

## 📁 Структура проекта

```
dieta/
├── main.py                 # Точка входа бота
├── improved_api_server.py  # FastAPI сервер
├── mobile/                 # Flutter Android-приложение
├── start_all_services.py   # Запуск всех сервисов
├── components/             # Компоненты бота
│   ├── handlers/          # Обработчики команд
│   ├── keyboards/         # Клавиатуры
│   └── states/           # FSM состояния
├── database/              # Работа с БД
├── api/                  # API для ИИ
├── calorie-love-tracker/ # React веб-приложение
└── docs/                # Документация
```

## 🔧 Настройка API ключей

### GigaChat (Сбер)
1. Регистрируйтесь на [developers.sber.ru](https://developers.sber.ru)
2. Создайте приложение и получите ключи
3. Добавьте в .env: `GIGACHAT_CLIENT_ID`, `GIGACHAT_AUTH_KEY`

### Mistral AI
1. Зарегистрируйтесь на [console.mistral.ai](https://console.mistral.ai)
2. Получите API ключ
3. Добавьте в .env: `MISTRAL_API_KEY`

### CalorieNinjas
1. Зарегистрируйтесь на [calorieninjas.com](https://calorieninjas.com)
2. Получите API ключ
3. Добавьте в .env: `CALORIE_NINJAS_API_KEY`

## 🌐 Доступные сервисы

После запуска будут доступны:
- **Telegram Bot**: @tvoy_diet_bot
- **API сервер**: http://localhost:8000
- **API документация**: http://localhost:8000/docs
- **Веб-приложение**: http://localhost:5173

## 📱 Основные команды бота

- `/start` - Начало работы с ботом
- `/profile` - Управление профилем
- `/addmeal` - Добавить прием пищи
- `/history` - История питания
- `/menu` - Сгенерировать персональное меню
- `/dietolog` - Консультация с диетологом
- `/water` - Трекер воды
- `/score` - Баллы и достижения

## 🤝 Разработка

Проект использует:
- **Backend**: Python 3.11+, aiogram 3.x, FastAPI
- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Database**: PostgreSQL / SQLite
- **AI**: GigaChat, Mistral AI, CalorieNinjas API
- **Deployment**: Docker, nginx

## 📄 Лицензия

MIT License - используйте свободно для своих проектов.

## 🐛 Поддержка

Если что-то не работает:
1. Проверьте настройки в `.env` файле
2. Убедитесь, что все API ключи корректны
3. Посмотрите логи в папке `logs/`
4. Создайте issue в GitHub репозитории

---

**Сделано с ❤️ для здорового образа жизни**