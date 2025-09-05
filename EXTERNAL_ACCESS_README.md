# 🔗 Налаштування зовнішнього доступу для KavaCRM

## 🚨 ПРОБЛЕМА
При спробі зайти на `http://kava-crm.asuscomm.com/crm/` ви отримуєте помилку "Service Unavailable".

## ✅ РІШЕННЯ

### 🔍 ДІАГНОСТИКА

1. **Перевірте локальний доступ:**
   ```bash
   # Запустіть цей файл
   check_external_access.bat
   ```

2. **Основні причини помилки:**
   - Django сервер не запущений
   - Немає веб-сервера (Apache/Nginx) для проксі
   - Не налаштований Port Forwarding на роутері
   - Домен не вказує на ваш IP

### 🛠️ ШВИДКЕ НАЛАШТУВАННЯ

#### ВАРІАНТ 1: ПРОСТИЙ (Windows + Apache)
```bash
# Запустіть скрипт налаштування
setup_apache_windows.bat
```

#### ВАРІАНТ 2: ПРОДАКШН (Linux + Nginx)
```bash
# На вашому Linux сервері
sudo cp nginx.conf /etc/nginx/sites-available/kavacrm
sudo ln -sf /etc/nginx/sites-available/kavacrm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Для HTTPS
chmod +x setup_https.sh
sudo ./setup_https.sh
```

#### ВАРІАНТ 3: ТЕСТУВАННЯ (ngrok)
```bash
# Встановіть ngrok
npm install -g ngrok

# Запустіть тунель
ngrok http 8000

# Використовуйте отриманий HTTPS URL
```

### 🌐 ДОСТУПНІ АДРЕСИ

Після налаштування будуть доступні:

| Тип доступу | Адреса | Статус |
|-------------|--------|--------|
| Локальний | `http://localhost:8000/crm/` | ✅ Працює |
| Зовнішній IP | `http://ВАШ_IP:8000/crm/` | 🔧 Потрібен Port Forwarding |
| Домен | `http://kava-crm.asuscomm.com/crm/` | 🔧 Потрібен DNS + Port Forwarding |

### ⚙️ НАЛАШТУВАННЯ ПОРТІВ

#### На ASUS Router (для домену на роутері):
1. Зайдіть в **ASUS Router Admin Panel**
2. Перейдіть в **Advanced Settings → WAN → Port Forwarding**
3. Додайте правила:
   ```
   Service Name: KavaCRM
   External Port: 80
   Internal IP: ВАШ_КОМПЮТЕР_IP
   Internal Port: 8000
   Protocol: TCP
   ```

#### На Windows Firewall:
```cmd
# Додати правило для порту 8000
netsh advfirewall firewall add rule name="Django Server" dir=in action=allow protocol=TCP localport=8000

# Додати правило для порту 80 (якщо використовуєте Apache)
netsh advfirewall firewall add rule name="Web Server" dir=in action=allow protocol=TCP localport=80
```

### 🔒 HTTPS НАЛАШТУВАННЯ

Для захищеного доступу через HTTPS:

1. **З Let's Encrypt (безкоштовно):**
   ```bash
   # На Linux сервері
   sudo certbot --nginx -d kava-crm.asuscomm.com -d www.kava-crm.asuscomm.com
   ```

2. **Через ngrok:**
   ```bash
   ngrok http 8000  # Дає HTTPS автоматично
   ```

### 🐛 ВИРІШЕННЯ ПРОБЛЕМ

#### Помилка "Connection refused":
- Django сервер не запущений
- Рішення: `python manage.py runserver 0.0.0.0:8000`

#### Помилка "Service Unavailable":
- Немає веб-сервера або він не налаштований
- Рішення: Налаштуйте Apache/Nginx або Port Forwarding

#### Помилка "DNS_PROBE_FINISHED_NXDOMAIN":
- Домен не налаштований або не вказує на ваш IP
- Рішення: Перевірте DNS налаштування або використовуйте IP

### 📞 ДОДАТКОВА ДОПОМОГА

Якщо проблеми залишаються:

1. **Запустіть діагностику:**
   ```bash
   check_external_access.bat
   ```

2. **Перевірте логи:**
   - Django: `logs/django.log`
   - Apache: `C:\Apache24\logs\error.log`
   - Nginx: `/var/log/nginx/error.log`

3. **Тестові адреси:**
   - Локальний тест: `http://127.0.0.1:8000/crm/`
   - Зовнішній тест: Знайдіть свій IP через `curl ifconfig.me`

### 🎯 ШВИДКИЙ СТАРТ

1. Запустіть `setup_external_access_windows.bat`
2. Дотримуйтесь інструкцій на екрані
3. Відкрийте `http://kava-crm.asuscomm.com/crm/` в браузері

**🚀 Готово! Ваш KavaCRM тепер доступний ззовні!**
