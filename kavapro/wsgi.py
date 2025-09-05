"""
WSGI config for kavapro project.
"""
import os
import sys

# Додаємо шлях до проекту
sys.path.insert(0, os.path.dirname(__file__))

# Налаштовуємо Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kavapro.settings')

# Ініціалізуємо Django
import django
django.setup()

# Імпортуємо WSGI додаток
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
