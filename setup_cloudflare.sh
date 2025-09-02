#!/bin/bash

# Скрипт для налаштування Cloudflare DNS та безпеки

set -e

DOMAIN="yourdomain.com"
CLOUDFLARE_API_TOKEN="your-cloudflare-api-token"
CLOUDFLARE_ZONE_ID="your-zone-id"

echo "☁️ Налаштування Cloudflare для домену: $DOMAIN"

# Встановлення Cloudflare CLI
echo "📦 Встановлення Cloudflare CLI..."
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb
rm cloudflared.deb

# Налаштування DNS записів через API
echo "🌐 Налаштування DNS записів..."

# A запис для основного домену
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records" \
     -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{
       "type": "A",
       "name": "'$DOMAIN'",
       "content": "YOUR_SERVER_IP",
       "ttl": 1,
       "proxied": true
     }'

# CNAME запис для www
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records" \
     -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{
       "type": "CNAME",
       "name": "www",
       "content": "'$DOMAIN'",
       "ttl": 1,
       "proxied": true
     }'

# Налаштування Page Rules для безпеки
echo "🔒 Налаштування Page Rules..."

# Redirect HTTP to HTTPS
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/pagerules" \
     -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{
       "targets": [
         {
           "target": "url",
           "constraint": {
             "operator": "matches",
             "value": "http://*.'$DOMAIN'/*"
           }
         }
       ],
       "actions": [
         {
           "id": "forwarding_url",
           "value": {
             "url": "https://$1.'$DOMAIN'/$2",
             "status_code": 301
           }
         }
       ],
       "priority": 1,
       "status": "active"
     }'

# Налаштування Security Level
echo "🛡️ Налаштування рівня безпеки..."
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/settings/security_level" \
     -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{
       "value": "high"
     }'

# Увімкнення Bot Fight Mode
echo "🤖 Увімкнення Bot Fight Mode..."
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/settings/bot_fight_mode" \
     -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{
       "value": "on"
     }'

# Увімкнення WAF
echo "🔥 Увімкнення WAF..."
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/settings/waf" \
     -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{
       "value": "on"
     }'

# Налаштування Always Use HTTPS
echo "🔐 Налаштування Always Use HTTPS..."
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/settings/always_use_https" \
     -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{
       "value": "on"
     }'

# Налаштування HSTS
echo "🛡️ Налаштування HSTS..."
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/settings/security_headers" \
     -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{
       "value": {
         "strict_transport_security": {
           "enabled": true,
           "max_age": 31536000,
           "include_subdomains": true,
           "preload": true
         }
       }
     }'

echo "✅ Cloudflare налаштування завершено!"
echo "☁️ Домен захищений Cloudflare"
echo "🔒 Включені: WAF, Bot Fight Mode, HSTS, Always Use HTTPS"
