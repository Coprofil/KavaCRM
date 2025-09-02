"""
Приклад конфігурації для продакшн
Скопіюйте цей файл та налаштуйте змінні для вашого середовища
"""

# Django налаштування
SECRET_KEY = 'your-very-secure-secret-key-here-change-this'
DEBUG = False

# База даних PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'kavacrm',
        'USER': 'kavacrm_user',
        'PASSWORD': 'your-secure-db-password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Email налаштування
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'

# Redis для кешування та Celery
REDIS_URL = 'redis://127.0.0.1:6379/1'
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

# LLM API ключі
OPENAI_API_KEY = 'your-openai-api-key'
ANTHROPIC_API_KEY = 'your-anthropic-api-key'

# Моніторинг
HEALTHCHECK_URL = 'https://hc-ping.com/your-uuid'
TELEGRAM_BOT_TOKEN = 'your-telegram-bot-token'
TELEGRAM_CHAT_ID = 'your-telegram-chat-id'

# Бекапи
BACKUP_DIR = '/mnt/usb/backups'
BACKUP_RETENTION_DAYS = 30

# Cloudflare налаштування
CLOUDFLARE_API_TOKEN = 'your-cloudflare-api-token'
CLOUDFLARE_ZONE_ID = 'your-zone-id'
DOMAIN = 'yourdomain.com'

# SSL сертифікати
SSL_CERT_PATH = '/etc/letsencrypt/live/yourdomain.com/fullchain.pem'
SSL_KEY_PATH = '/etc/letsencrypt/live/yourdomain.com/privkey.pem'
