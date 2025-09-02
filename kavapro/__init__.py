# Ініціалізація Celery (опційно). Якщо Celery не встановлено — не падаємо.
try:
    from .celery import app as celery_app
except Exception:
    celery_app = None

__all__ = ('celery_app',)
