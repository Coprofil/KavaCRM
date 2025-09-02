#!/bin/bash

# Скрипт для налаштування HTTPS з Let's Encrypt

set -e

DOMAIN="yourdomain.com"
EMAIL="your-email@example.com"
NGINX_CONF="/etc/nginx/sites-available/kavacrm"
PROJECT_PATH="/path/to/your/project"

echo "🔧 Налаштування HTTPS для домену: $DOMAIN"

# Оновлення системи
echo "📦 Оновлення системи..."
sudo apt update && sudo apt upgrade -y

# Встановлення Nginx
echo "🌐 Встановлення Nginx..."
sudo apt install nginx -y

# Встановлення Certbot
echo "🔐 Встановлення Certbot..."
sudo apt install certbot python3-certbot-nginx -y

# Створення базової конфігурації Nginx
echo "⚙️ Створення конфігурації Nginx..."
sudo tee $NGINX_CONF > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Активація сайту
sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Отримання SSL сертифікату
echo "🔒 Отримання SSL сертифікату..."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive

# Налаштування автоматичного оновлення сертифікатів
echo "🔄 Налаштування автоматичного оновлення..."
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Створення повної конфігурації Nginx з HTTPS
echo "🔧 Оновлення конфігурації Nginx..."
sudo tee $NGINX_CONF > /dev/null <<EOF
# Перенаправлення HTTP на HTTPS
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS конфігурація
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL сертифікати
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL налаштування
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Безпека заголовків
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Статичні файли
    location /static/ {
        alias $PROJECT_PATH/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Медіа файли
    location /media/ {
        alias $PROJECT_PATH/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Основне проксування до Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
        
        # Таймаути
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Буферизація
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Health check endpoint
    location /health/ {
        proxy_pass http://127.0.0.1:8000/health/;
        access_log off;
    }

    # Логи
    access_log /var/log/nginx/kavacrm_access.log;
    error_log /var/log/nginx/kavacrm_error.log;
}
EOF

# Перевірка та перезавантаження Nginx
sudo nginx -t
sudo systemctl reload nginx

echo "✅ HTTPS налаштування завершено!"
echo "🌐 Ваш сайт доступний за адресою: https://$DOMAIN"
echo "🔒 SSL сертифікат автоматично оновлюватиметься"
