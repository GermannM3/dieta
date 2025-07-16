# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package*.json ./
RUN npm ci --only=production

# Копируем исходный код
COPY . .

# Объявляем аргументы сборки для переменных окружения
ARG VITE_API_URL=http://5.129.198.80:8000
ARG VITE_APP_TITLE="Твой Диетолог - Персональный ИИ-помощник"
ARG VITE_APP_DESCRIPTION="Продвинутый телеграм-бот с личным диетологом"
ARG VITE_TELEGRAM_BOT_USERNAME=@tvoy_diet_bot

# Устанавливаем переменные окружения для сборки
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_APP_TITLE=$VITE_APP_TITLE
ENV VITE_APP_DESCRIPTION=$VITE_APP_DESCRIPTION
ENV VITE_TELEGRAM_BOT_USERNAME=$VITE_TELEGRAM_BOT_USERNAME

# Собираем приложение
RUN npm run build

# Production stage
FROM nginx:alpine

# Устанавливаем необходимые пакеты
RUN apk add --no-cache nodejs npm

# Копируем собранное приложение
COPY --from=builder /app/dist /usr/share/nginx/html

# Создаем конфигурацию nginx
COPY nginx.prod.conf /etc/nginx/conf.d/default.conf

# Expose port 3000
EXPOSE 3000

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"] 