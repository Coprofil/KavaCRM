"""
Celery configuration for KavaCRM
"""

import os
from celery import Celery
from django.conf import settings

# Встановлюємо Django settings модуль для celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kavapro.settings_production')

app = Celery('kavapro')

# Використовуємо Django settings для конфігурації Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматично знаходимо завдання в усіх Django apps
app.autodiscover_tasks()

# Налаштування для продакшн
app.conf.update(
    # Розклад завдань
    beat_schedule={
        'daily-backup': {
            'task': 'kavacrm.tasks.create_daily_backup',
            'schedule': 60.0 * 60.0 * 4.0,  # Щодня о 04:00
        },
        'daily-report': {
            'task': 'kavacrm.tasks.send_daily_report',
            'schedule': 60.0 * 60.0 * 8.0,  # Щодня о 08:00
        },
        'check-low-stock': {
            'task': 'kavacrm.tasks.check_low_stock',
            'schedule': 60.0 * 60.0 * 2.0,  # Кожні 2 години
        },
        'route-reminders': {
            'task': 'kavacrm.tasks.send_route_reminders',
            'schedule': 60.0 * 60.0 * 18.0,  # Щодня о 18:00
        },
        'cleanup-logs': {
            'task': 'kavacrm.tasks.cleanup_old_logs',
            'schedule': 60.0 * 60.0 * 24.0,  # Щодня
        },
    },
    
    # Налаштування черги
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Kiev',
    enable_utc=True,
    
    # Налаштування retry
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Налаштування результатів
    result_expires=3600,  # 1 година
    
    # Налаштування логування
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
