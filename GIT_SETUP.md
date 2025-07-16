# 🔗 Настройка GitHub репозитория

## 📋 Пошаговая инструкция

### 1. Добавление удаленного репозитория
```bash
git remote add origin https://github.com/GermannM3/dieta.git
```

### 2. Проверка настроек
```bash
git remote -v
```

### 3. Первый push
```bash
git push -u origin main
```

### 4. Для последующих обновлений
```bash
git add .
git commit -m "Описание изменений"
git push
```

## 🚀 Автоматический деплой

После каждого push в GitHub, для обновления на сервере:

```bash
# Подключение к серверу
ssh root@5.129.198.80

# Автоматическое обновление
cd /opt/dieta && ./auto-deploy.sh
```

## 🔧 Настройка webhook (опционально)

Для полностью автоматического деплоя при push можно настроить GitHub webhook:

1. В настройках репозитория: Settings → Webhooks
2. Payload URL: `http://5.129.198.80:9000/webhook`
3. Content type: `application/json`
4. Trigger: `Just the push event`

Это автоматически будет запускать деплой при каждом push. 