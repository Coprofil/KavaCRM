# 🔒 HTTPS КОНФІГУРАЦІЯ KAVACRM

## 🚀 ШВИДКИЙ СТАРТ

### 1. Повний тест HTTPS (рекомендовано)
```cmd
https_full_test.bat
```

**Що робить:**
- Створює самопідписаний сертифікат
- Оновлює Django налаштування
- Запускає HTTPS сервер
- Тестує в браузері

### 2. Ручне налаштування

#### Створення сертифікату
```bash
python manage_https.py create --domain localhost --cert-dir certs
```

#### Оновлення Django
```bash
python manage_https.py django
```

#### Запуск HTTPS сервера
```bash
python manage.py runssl --cert-dir=certs --port=8443
```

#### Тестування в браузері
```bash
python test_https_browser.py --port 8443
```

## 📋 ДЕТАЛЬНИЙ ПРОЦЕС

### Крок 1: Створення сертифікату
```bash
# Самопідписаний сертифікат для тестування
python manage_https.py create --domain localhost --days 365

# Перевірка сертифікату
python manage_https.py check --domain localhost
```

### Крок 2: Налаштування Django
```bash
python manage_https.py django
```

**Додає до settings.py:**
```python
# HTTPS Безпека налаштування
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Крок 3: Запуск HTTPS сервера
```bash
python manage.py runssl --cert-dir=certs --port=8443
```

**Доступні URL:**
- Головна: https://localhost:8443/crm/
- Адмін: https://localhost:8443/secure-admin-panel-2024/
- API: https://localhost:8443/api/

### Крок 4: Тестування
```bash
# Створити тестову сторінку
python test_https_browser.py --create-test-page

# Протестувати в браузері
python test_https_browser.py --port 8443
```

## 🔐 РОБОТА З СЕРТИФІКАТАМИ

### Перегляд інформації про сертифікат
```bash
python manage_https.py check --domain localhost
```

### Створення нових сертифікатів
```bash
# Для іншого домену
python manage_https.py create --domain kavacrm.local --days 365

# Для продакшн (Let's Encrypt буде автоматично)
python manage_https.py create --domain yourdomain.com --days 90
```

### Структура каталогів
```
certs/
├── localhost.crt          # Сертифікат
├── localhost.key          # Приватний ключ
├── localhost.pfx          # Для Windows/IIS
└── localhost_info.json    # Інформація про сертифікат
```

## 🌐 ПРОДАКШН КОНФІГУРАЦІЯ

### Nginx конфігурація
```bash
python manage_https.py nginx --domain yourdomain.com
```

Створює: `nginx/yourdomain.com.conf`

### Apache конфігурація
```bash
python manage_https.py apache --domain yourdomain.com
```

Створює: `apache/yourdomain.com.conf`

### Let's Encrypt сертифікати
```bash
# На сервері з встановленим Certbot
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 🔍 ДІАГНОСТИКА ПРОБЛЕМ

### Сертифікат не працює
```bash
# Перевірити файли сертифікату
python manage_https.py check --domain localhost

# Перестворити сертифікат
python manage_https.py create --domain localhost --cert-dir certs
```

### Django не перенаправляє на HTTPS
```bash
# Перевірити settings.py
grep "SECURE_SSL_REDIRECT" kavapro/settings.py

# Оновити налаштування
python manage_https.py django
```

### Браузер показує помилку сертифікату
```
Це нормально для самопідписаних сертифікатів!
Натисніть "Просунути" або "Додати виняток"
```

### Сервер не запускається
```bash
# Перевірити порт
netstat -an | find "8443"

# Спробувати інший порт
python manage.py runssl --port 8444
```

## ⚠️ ВАЖЛИВІ ПОПЕРЕДЖЕННЯ

### Для розробки (localhost):
- ✅ Використовуйте самопідписані сертифікати
- ✅ Приймайте попередження браузера
- ✅ Тестуйте всі функції

### Для продакшн:
- ❌ НЕ використовуйте самопідписані сертифікати
- ✅ Отримайте сертифікати від Let's Encrypt
- ✅ Налаштуйте автоматичне оновлення
- ✅ Використовуйте сильні шифри

## 🚀 ПРОДАКШН ЗАПУСК

### На Ubuntu/Debian сервері:
```bash
# 1. Оновити систему
sudo apt update && sudo apt upgrade -y

# 2. Встановити Nginx
sudo apt install nginx -y

# 3. Встановити Certbot
sudo apt install certbot python3-certbot-nginx -y

# 4. Отримати сертифікат
sudo certbot --nginx -d yourdomain.com

# 5. Створити Nginx конфігурацію
sudo cp nginx/yourdomain.com.conf /etc/nginx/sites-available/
sudo ln -s ../sites-available/yourdomain.com.conf /etc/nginx/sites-enabled/

# 6. Перевірити конфігурацію
sudo nginx -t

# 7. Перезавантажити Nginx
sudo systemctl reload nginx

# 8. Запустити Django з Gunicorn
gunicorn kavapro.wsgi:application --bind 127.0.0.1:8000
```

## 📊 МОНИТОРИНГ HTTPS

### Перевірка статусу сертифікату
```bash
# Локально
openssl s_client -connect localhost:8443 -servername localhost

# Онлайн інструменти
# SSL Labs: https://www.ssllabs.com/ssltest/
# DigiCert: https://www.digicert.com/help/
```

### Автоматичне оновлення
```bash
# Certbot автоматично оновлює сертифікати
sudo systemctl status certbot.timer
sudo systemctl enable certbot.timer
```

## 🛠️ ДОДАТКОВІ ІНСТРУМЕНТИ

### Перевірка конфігурації
```bash
# Django settings
python -c "from kavapro.settings import *; print('SSL redirect:', SECURE_SSL_REDIRECT)"

# Nginx config
sudo nginx -t

# Apache config
sudo apache2ctl configtest
```

### Логування
```bash
# Django логи
tail -f logs/django.log

# Nginx логи
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## 🎯 ПІДСУМОК

**Для тестування:**
```cmd
https_full_test.bat
```

**Для продакшн:**
1. Отримайте домен
2. Налаштуйте DNS
3. Запустіть `setup_https.sh` на сервері
4. Налаштуйте моніторинг

HTTPS конфігурація готова! 🔒✨
