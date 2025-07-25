#!/bin/bash

echo "Перезапуск сервисов после обновления конфигурации..."

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение и запуск frontend сервиса
sudo systemctl enable --now frontend

# Перезапуск nginx
sudo systemctl restart nginx

echo "Сервисы успешно перезапущены!"
echo "Статус сервисов:"
echo "Frontend: $(sudo systemctl is-active frontend)"
echo "Nginx: $(sudo systemctl is-active nginx)" 