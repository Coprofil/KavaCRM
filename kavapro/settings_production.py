"""
Production settings for kavapro project.
"""

import os
import importlib
from pathlib import Path
from .settings import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-a3t=e*3zvqyptx=26%fkp&ad$&)*t4@f!7=ziu-a@5*nsrz4(j')

# Ensure logs directory exists
LOGS_DIR = (Path(__file__).resolve().parent.parent / 'logs')
try:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

# Hosts/domain names that are valid for this site
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '46.118.98.38',
    'kava-crm.asuscomm.com',
    # Додайте ваш домен тут
    # 'yourdomain.com',
    # 'www.yourdomain.com',
]

# HTTPS налаштування
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 рік
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# CSRF налаштування для HTTPS
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Session налаштування для HTTPS
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'

# Database - PostgreSQL для продакшн
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'kavacrm'),
        'USER': os.environ.get('DB_USER', 'kavacrm_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Email налаштування
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')

# Static files налаштування для продакшн
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/crm/static/'

# Публічний префікс застосунку за реверс‑проксі (Apache /crm)
FORCE_SCRIPT_NAME = '/crm'

# Media files
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/crm/media/'

# Логування для продакшн
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(LOGS_DIR / 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': str(LOGS_DIR / 'error.log'),
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'kavacrm': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Кешування - Redis для продакшн
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery налаштування для фонових завдань
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')

# Додаткові налаштування безпеки
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Налаштування для Cloudflare
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Налаштування для адмінки
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')  # Змінити шлях адмінки

# Налаштування для 2FA
TWO_FACTOR_CALL_GATEWAY = 'two_factor.gateways.fake.Fake'
TWO_FACTOR_SMS_GATEWAY = 'two_factor.gateways.fake.Fake'

# Налаштування для RAG/LLM
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# Налаштування для моніторингу
HEALTHCHECK_URL = os.environ.get('HEALTHCHECK_URL', '')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# Налаштування для бекапів
BACKUP_DIR = os.environ.get('BACKUP_DIR', '/mnt/usb/backups')
BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', '30'))

# Додаткові apps для продакшн (опційно, якщо встановлені)
def _available(pkg: str) -> bool:
    try:
        importlib.import_module(pkg)
        return True
    except Exception:
        return False

optional_apps = []
# 2FA
if _available('django_otp'):
    optional_apps += ['django_otp']
    if _available('django_otp.plugins.otp_totp'):
        optional_apps += ['django_otp.plugins.otp_totp']
    if _available('django_otp.plugins.otp_static'):
        optional_apps += ['django_otp.plugins.otp_static']
if _available('two_factor'):
    optional_apps += ['two_factor']

# Health check
if _available('health_check'):
    optional_apps += ['health_check']
    for sub in ['health_check.db', 'health_check.cache', 'health_check.storage']:
        if _available(sub):
            optional_apps += [sub]

# Celery DB schedulers (необов'язково)
for celery_pkg in ['django_celery_beat', 'django_celery_results']:
    if _available(celery_pkg):
        optional_apps += [celery_pkg]

INSTALLED_APPS += optional_apps

# Middleware для 2FA (якщо встановлено)
if 'django_otp' in optional_apps:
    MIDDLEWARE += [
        'django_otp.middleware.OTPMiddleware',
    ]

# Налаштування для 2FA
TWO_FACTOR_CALL_GATEWAY = 'two_factor.gateways.fake.Fake'
TWO_FACTOR_SMS_GATEWAY = 'two_factor.gateways.fake.Fake'
TWO_FACTOR_LOGIN_URL = 'two_factor:login'
TWO_FACTOR_SETUP_URL = 'two_factor:setup'
TWO_FACTOR_REMOVE_URL = 'two_factor:disable'

# Налаштування для адміністраторів
ADMINS = [
    ('Admin', 'admin@yourdomain.com'),
]

# Налаштування для Celery Beat
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
