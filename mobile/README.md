# Твой Диетолог — Android (Flutter)

Мобильное приложение с тем же дизайном, что и веб-версия `calorie-love-tracker`.

## Функции

- Вход / регистрация (JWT)
- Дашборд: калории, БЖУ, вода, настроение
- Добавление еды с ИИ-расчётом (`/api/search_food`, `/api/calculate_calories`)
- ИИ-диетолог (`/api/web/dietolog`)
- Профиль с формулой Миффлина–Сан Жеора

## Секреты и сборка

**Ключи AI (GigaChat, Mistral) не зашиваются в APK** — приложение ходит на ваш backend API, где ключи уже настроены.

В APK при сборке подставляется только:

| Переменная | Описание |
|------------|----------|
| `API_BASE_URL` | URL backend (например `http://5.129.198.80:8000`) |
| `APP_NAME` | Название приложения |

Файл `dart_defines.json` **не коммитится** — генерируется в GitHub Actions из Secrets.

### GitHub Secrets (Settings → Secrets → Actions)

```
API_BASE_URL=http://5.129.198.80:8000
APP_NAME=Твой Диетолог
```

## Сборка на GitHub (не локально)

1. Запушьте код в репозиторий
2. Добавьте Secrets (см. выше)
3. Запустите workflow:
   - **Автоматически:** создайте тег `android-v1.0.0`
   - **Вручную:** Actions → Android Release → Run workflow

```bash
git tag android-v1.0.0
git push origin android-v1.0.0
```

4. APK и AAB появятся в [Releases](https://github.com/GermannM3/dieta/releases)

## Локальная разработка (опционально)

```bash
cd mobile
cp dart_defines.example.json dart_defines.json
flutter pub get
flutter run --dart-define-from-file=dart_defines.json
```

## Android permissions

- `INTERNET` — API
- `ACCESS_NETWORK_STATE` — проверка сети
- `usesCleartextTraffic=true` — HTTP API на сервере
