# KavaCRM - Система Управління Клієнтами

[![Django](https://img.shields.io/badge/Django-5.2.4-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Опис проекту

**KavaCRM** - це повнофункціональна CRM система для управління клієнтами, маршрутами та технічним обслуговуванням. Система включає сучасні технології моніторингу, безпеки та штучного інтелекту.

## ✨ Основні функції

### 👥 Управління клієнтами
- База клієнтів з сегментацією
- Управління телефонами та адресами
- Історія візитів та платежів
- Розрахунки з клієнтами

### 🚛 Система маршрутів
- Планувальник маршрутів для агентів
- Оптимізація маршрутів по днях тижня
- Відстеження виконання маршрутів
- Генерація звітів про візити

### 📦 Система відвантажень
- Управління запасами товарів
- Рекомендації по відвантаженнях
- Контроль залишків
- Автоматичне формування замовлень

### 🔧 Технічне обслуговування
- База запчастин та обладнання
- Система заявок на ремонт
- Наряди на роботи
- Складський облік

### 📊 Аналітика та звіти
- Аналітика продажів по агентах
- Статистика по клієнтах
- Звіти по відвантаженнях
- Експорт даних

### 🔒 Безпека
- Двофакторна аутентифікація (2FA)
- Захищений доступ до адмін панелі
- Шифрування чутливих даних
- Аудит дій користувачів

### 🤖 ШІ інтеграція (RAG)
- Пошук по документації
- Інтелектуальні рекомендації
- Автоматизація процесів
- Інтеграція з OpenAI та Anthropic

### 📡 Моніторинг
- Health checks системи
- Telegram сповіщення
- Автоматичні бекапи
- Логування подій

## 🛠 Технічний стек

- **Backend**: Django 5.2.4, Python 3.8+
- **Database**: PostgreSQL 15+ (з pgvector для RAG)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **AI/ML**: OpenAI GPT, Anthropic Claude, LangChain
- **Security**: django-two-factor-auth, HTTPS
- **Monitoring**: django-health-check, Telegram Bot API
- **Deployment**: Nginx, Gunicorn, systemd

## 🚀 Швидкий старт

### 1. Клонування репозиторію
```bash
git clone <repository-url>
cd kavapro
```

### 2. Встановлення залежностей
```bash
pip install -r requirements_production.txt
```

### 3. Налаштування бази даних
```bash
# Для розробки (SQLite)
python manage.py migrate

# Для продакшну (PostgreSQL)
# Налаштуйте settings_production.py та запустіть міграції
```

### 4. Створення адміністратора
```bash
python manage.py createsuperuser
```

### 5. Запуск сервера
```bash
# Розробка
python manage.py runserver

# Продакшн
./start_production.sh
```

## ⚙️ Конфігурація

### Змінні середовища
Створіть `.env` файл на основі `config_example.py`:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False

# Database
DB_NAME=kavacrm
DB_USER=kavacrm_user
DB_PASSWORD=your-password

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AI
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Monitoring
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

## 📁 Структура проекту

```
kavapro/
├── kavacrm/                 # Основний додаток
│   ├── models.py           # Моделі даних
│   ├── views.py            # Представлення
│   ├── templates/          # HTML шаблони
│   ├── static/            # Статичні файли
│   ├── management/        # Django команди
│   └── backup_utils.py    # Утиліти бекапів
├── kavapro/               # Налаштування Django
│   ├── settings.py        # Основні налаштування
│   ├── settings_production.py  # Продакшн налаштування
│   └── urls.py            # URL конфігурація
├── setup_*.sh            # Скрипти розгортання
├── requirements_*.txt    # Залежності
├── init_system.py        # Ініціалізація системи
├── start_production.sh   # Запуск в продакшн
└── deploy_check.py      # Перевірка готовності
```

## 🔧 Налаштування для продакшну

### 1. HTTPS налаштування
```bash
sudo ./setup_cloudflare.sh
sudo ./setup_https.sh
```

### 2. PostgreSQL + pgvector
```bash
sudo ./setup_postgresql_pgvector.sh
```

### 3. Моніторинг
```bash
sudo ./setup_monitoring.sh
```

### 4. USB бекапи
```bash
sudo ./setup_usb_backup.sh
```

## 💾 Бекапи

### Ручний бекап
```bash
# Простий бекап
python backup_simple.py

# Повний бекап через Django
python manage.py backup

# Windows бекап
create_backup.bat
```

### Автоматичні бекапи
- **USB диск**: щодня о 04:00
- **PostgreSQL**: щодня о 03:00
- **Ротація**: зберігання 30 днів

## 🔍 Моніторинг

### Health checks
- `https://yourdomain.com/health/` - базовий статус
- `https://yourdomain.com/health/detailed/` - детальна інформація

### Telegram сповіщення
- Сповіщення про помилки
- Щоденні звіти
- Алерти про низькі залишки

## 🤖 RAG система

### Налаштування
```bash
python manage.py init_rag_system
```

### API endpoints
- `POST /api/rag/question/` - запит до AI
- `GET /api/rag/search/` - пошук по документах
- `GET /api/rag/stats/` - статистика системи

## 📊 API документація

### REST API
Базова URL: `https://yourdomain.com/crm/api/`

#### Клієнти
- `GET /api/clients/` - список клієнтів
- `POST /api/clients/` - створення клієнта
- `GET /api/clients/{id}/` - деталі клієнта

#### Маршрути
- `GET /api/routes/` - список маршрутів
- `POST /api/routes/` - створення маршруту

#### Звіти
- `GET /api/reports/sales/` - звіт продажів
- `GET /api/reports/clients/` - звіт клієнтів

## 🐛 Troubleshooting

### Поширені проблеми

1. **Помилка бази даних**
   ```bash
   python manage.py dbshell
   # Перевірте з'єднання
   ```

2. **Проблеми з міграціями**
   ```bash
   python manage.py showmigrations
   python manage.py migrate --fake-initial
   ```

3. **Проблеми з статичними файлами**
   ```bash
   python manage.py collectstatic --clear
   ```

4. **Помилки 2FA**
   ```bash
   python manage.py migrate django_otp
   ```

## 📈 Розвиток

### Roadmap
- [ ] Інтеграція з Telegram ботом для клієнтів
- [ ] Мобільний додаток
- [ ] Інтеграція з 1C/ERP системами
- [ ] Розширена аналітика з ML
- [ ] API для зовнішніх інтеграцій

### Контрибʼюція
1. Fork репозиторій
2. Створіть feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit зміни (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Відкрийте Pull Request

## 📄 Ліцензія

Цей проект ліцензовано під MIT License - дивіться [LICENSE](LICENSE) файл для деталей.

## 📞 Підтримка

- **Email**: support@kavacrm.com
- **Документація**: [Wiki](wiki/)
- **Issues**: [GitHub Issues](issues/)

## 🙏 Подяки

- Django community
- PostgreSQL команда
- OpenAI та Anthropic за AI API
- Всі контрибʼютори проекту

---

**KavaCRM** - ваш надійний партнер в управлінні клієнтами! 🚀
