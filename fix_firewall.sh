#!/bin/bash

echo "🔧 Настройка файрвола и портов..."

echo "📡 Открываем порты 80 и 443:"
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
echo ""

echo "🌐 Проверяем статус UFW:"
sudo ufw status
echo ""

echo "🔒 Проверяем iptables:"
sudo iptables -L -n | grep -E '(80|443)'
echo ""

echo "📋 Проверяем что nginx слушает правильные порты:"
sudo netstat -tlnp | grep nginx
echo ""

echo "✅ Настройка завершена!" 