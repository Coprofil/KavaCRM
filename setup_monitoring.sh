#!/bin/bash

# Скрипт для налаштування моніторингу KavaCRM

set -e

DOMAIN="yourdomain.com"
TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
TELEGRAM_CHAT_ID="your-telegram-chat-id"
HEALTHCHECK_URL="your-healthcheck-url"

echo "📊 Налаштування моніторингу для KavaCRM"

# Встановлення необхідних пакетів
echo "📦 Встановлення необхідних пакетів..."
sudo apt update
sudo apt install -y python3-psutil python3-requests curl jq

# Створення директорії для логів
echo "📁 Створення директорії для логів..."
sudo mkdir -p /var/log/kavacrm
sudo chown -R $USER:$USER /var/log/kavacrm

# Створення скрипта моніторингу системи
echo "📝 Створення скрипта моніторингу системи..."
sudo tee /usr/local/bin/kavacrm-monitor.sh > /dev/null <<EOF
#!/bin/bash

# Скрипт моніторингу KavaCRM
DOMAIN="$DOMAIN"
TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID"
HEALTHCHECK_URL="$HEALTHCHECK_URL"

LOG_FILE="/var/log/kavacrm/monitor.log"

# Функція логування
log_message() {
    echo "\$(date '+%Y-%m-%d %H:%M:%S') - \$1" >> \$LOG_FILE
}

# Функція відправки в Telegram
send_telegram() {
    local message="\$1"
    local level="\${2:-info}"
    
    local emoji="ℹ️"
    case \$level in
        "warning") emoji="⚠️" ;;
        "error") emoji="❌" ;;
        "critical") emoji="🚨" ;;
        "success") emoji="✅" ;;
    esac
    
    local formatted_message="\$emoji <b>KavaCRM Monitor</b>\n\n\$message"
    
    curl -s -X POST "https://api.telegram.org/bot\$TELEGRAM_BOT_TOKEN/sendMessage" \\
        -d chat_id="\$TELEGRAM_CHAT_ID" \\
        -d text="\$formatted_message" \\
        -d parse_mode="HTML" > /dev/null
}

# Перевірка доступності сайту
check_website() {
    local response=\$(curl -s -o /dev/null -w "%{http_code}" "https://\$DOMAIN/health/")
    
    if [ "\$response" = "200" ]; then
        log_message "Website health check: OK"
        return 0
    else
        log_message "Website health check: FAILED (HTTP \$response)"
        send_telegram "🌐 Сайт недоступний!\n\nHTTP код: \$response\nДомен: \$DOMAIN" "critical"
        return 1
    fi
}

# Перевірка дискового простору
check_disk_space() {
    local usage=\$(df / | awk 'NR==2 {print \$5}' | sed 's/%//')
    
    if [ "\$usage" -gt 90 ]; then
        log_message "Disk space warning: \$usage% used"
        send_telegram "💾 Критично мало місця на диску!\n\nВикористано: \$usage%" "critical"
        return 1
    elif [ "\$usage" -gt 80 ]; then
        log_message "Disk space warning: \$usage% used"
        send_telegram "💾 Мало місця на диску\n\nВикористано: \$usage%" "warning"
        return 0
    else
        log_message "Disk space: OK (\$usage% used)"
        return 0
    fi
}

# Перевірка пам'яті
check_memory() {
    local usage=\$(free | awk 'NR==2{printf "%.0f", \$3*100/\$2}')
    
    if [ "\$usage" -gt 90 ]; then
        log_message "Memory warning: \$usage% used"
        send_telegram "🧠 Критично висока використання пам'яті!\n\nВикористано: \$usage%" "critical"
        return 1
    elif [ "\$usage" -gt 80 ]; then
        log_message "Memory warning: \$usage% used"
        send_telegram "🧠 Висока використання пам'яті\n\nВикористано: \$usage%" "warning"
        return 0
    else
        log_message "Memory: OK (\$usage% used)"
        return 0
    fi
}

# Перевірка процесів Django
check_django_processes() {
    local processes=\$(pgrep -f "manage.py runserver" | wc -l)
    
    if [ "\$processes" -eq 0 ]; then
        log_message "Django processes: NOT RUNNING"
        send_telegram "🐍 Django сервер не працює!\n\nНе знайдено активних процесів" "critical"
        return 1
    else
        log_message "Django processes: OK (\$processes processes)"
        return 0
    fi
}

# Перевірка бази даних
check_database() {
    local response=\$(curl -s "https://\$DOMAIN/health/" | jq -r '.checks.database.status' 2>/dev/null)
    
    if [ "\$response" = "healthy" ]; then
        log_message "Database: OK"
        return 0
    else
        log_message "Database: FAILED"
        send_telegram "🗄️ Проблема з базою даних!\n\nСтатус: \$response" "critical"
        return 1
    fi
}

# Ping healthcheck.io
ping_healthcheck() {
    if [ -n "\$HEALTHCHECK_URL" ]; then
        curl -s "\$HEALTHCHECK_URL" > /dev/null
        log_message "Healthcheck ping: OK"
    fi
}

# Основна функція моніторингу
main() {
    log_message "Starting monitoring check..."
    
    local failed_checks=0
    
    check_website || ((failed_checks++))
    check_disk_space || ((failed_checks++))
    check_memory || ((failed_checks++))
    check_django_processes || ((failed_checks++))
    check_database || ((failed_checks++))
    ping_healthcheck
    
    if [ "\$failed_checks" -eq 0 ]; then
        log_message "All checks passed"
    else
        log_message "Failed checks: \$failed_checks"
    fi
    
    log_message "Monitoring check completed"
}

# Запуск моніторингу
main
EOF

sudo chmod +x /usr/local/bin/kavacrm-monitor.sh

# Створення systemd сервісу для моніторингу
echo "⚙️ Створення systemd сервісу для моніторингу..."
sudo tee /etc/systemd/system/kavacrm-monitor.service > /dev/null <<EOF
[Unit]
Description=KavaCRM System Monitor
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/kavacrm-monitor.sh
User=$USER
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Створення systemd таймера для моніторингу
echo "⏰ Створення systemd таймера..."
sudo tee /etc/systemd/system/kavacrm-monitor.timer > /dev/null <<EOF
[Unit]
Description=Run KavaCRM Monitor every 5 minutes
Requires=kavacrm-monitor.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
EOF

# Встановлення cron завдання для щоденного звіту
echo "📅 Налаштування cron завдання..."
(crontab -l 2>/dev/null; echo "0 8 * * * curl -s https://$DOMAIN/health/detailed/ | jq -r '.application_stats' | /usr/local/bin/kavacrm-monitor.sh") | crontab -

# Активація сервісів
echo "🔄 Активація сервісів..."
sudo systemctl daemon-reload
sudo systemctl enable kavacrm-monitor.timer
sudo systemctl start kavacrm-monitor.timer

# Створення скрипта для тестування моніторингу
echo "🧪 Створення тестового скрипта..."
sudo tee /usr/local/bin/test-monitoring.sh > /dev/null <<EOF
#!/bin/bash

echo "🧪 Тестування моніторингу KavaCRM"
echo "=================================="

echo "1. Тестування health check..."
curl -s "https://$DOMAIN/health/" | jq '.'

echo -e "\n2. Тестування детального health check..."
curl -s "https://$DOMAIN/health/detailed/" | jq '.'

echo -e "\n3. Тестування Telegram бота..."
/usr/local/bin/kavacrm-monitor.sh

echo -e "\n4. Перевірка логів..."
tail -10 /var/log/kavacrm/monitor.log

echo -e "\n✅ Тестування завершено"
EOF

sudo chmod +x /usr/local/bin/test-monitoring.sh

echo "✅ Моніторинг налаштування завершено!"
echo "📊 Health check доступний за адресою: https://$DOMAIN/health/"
echo "📈 Детальний health check: https://$DOMAIN/health/detailed/"
echo "⏰ Моніторинг запускається кожні 5 хвилин"
echo "📝 Логи зберігаються в: /var/log/kavacrm/monitor.log"
echo ""
echo "Команди для управління:"
echo "  Тестування: sudo /usr/local/bin/test-monitoring.sh"
echo "  Ручна перевірка: sudo /usr/local/bin/kavacrm-monitor.sh"
echo "  Статус таймера: sudo systemctl status kavacrm-monitor.timer"
echo "  Перегляд логів: sudo journalctl -u kavacrm-monitor.service"
