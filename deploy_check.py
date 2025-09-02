#!/usr/bin/env python3
"""
Скрипт для перевірки системи та готовності до розгортання KavaCRM
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Перевірка версії Python"""
    print("🐍 Перевірка Python...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Потрібна версія 3.8+")
        return False

def check_dependencies():
    """Перевірка встановлених залежностей"""
    print("\n📦 Перевірка залежностей...")

    required_packages = [
        'django',
        'psycopg2',
        'django_redis',
        'celery',
        'django_two_factor_auth',
        'django_otp',
        'qrcode',
        'django_health_check',
        'requests',
        'openai',
        'anthropic',
        'langchain',
        'pgvector',
        'pillow',
        'python_decouple'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            importlib.import_module(package.replace('_', '-'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️ Відсутні пакети: {', '.join(missing_packages)}")
        print("Встановіть їх командою: pip install -r requirements_production.txt")
        return False

    print("✅ Всі залежності встановлені")
    return True

def check_django_settings():
    """Перевірка Django налаштувань"""
    print("\n⚙️ Перевірка Django налаштувань...")

    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kavapro.settings')

        import django
        django.setup()

        from django.conf import settings

        # Перевірка INSTALLED_APPS
        required_apps = [
            'kavacrm',
            'django.contrib.admin',
            'django_otp',
            'two_factor'
        ]

        for app in required_apps:
            if app in settings.INSTALLED_APPS:
                print(f"✅ {app} - в INSTALLED_APPS")
            else:
                print(f"❌ {app} - відсутній в INSTALLED_APPS")
                return False

        # Перевірка SECRET_KEY
        if hasattr(settings, 'SECRET_KEY') and settings.SECRET_KEY:
            if 'django-insecure' in settings.SECRET_KEY:
                print("⚠️ SECRET_KEY містить 'django-insecure' - змініть для продакшн")
            else:
                print("✅ SECRET_KEY налаштований")
        else:
            print("❌ SECRET_KEY не налаштований")
            return False

        # Перевірка DEBUG
        if settings.DEBUG:
            print("⚠️ DEBUG=True - вимкніть для продакшн")
        else:
            print("✅ DEBUG=False")

        # Перевірка бази даних
        db_engine = settings.DATABASES['default']['ENGINE']
        if 'postgresql' in db_engine:
            print("✅ PostgreSQL налаштований")
        elif 'sqlite3' in db_engine:
            print("⚠️ SQLite використовується - рекомендується PostgreSQL для продакшн")
        else:
            print(f"❌ Непідтримуваний тип БД: {db_engine}")

        print("✅ Django налаштування перевірені")
        return True

    except Exception as e:
        print(f"❌ Помилка перевірки Django: {e}")
        return False

def check_database_connection():
    """Перевірка з'єднання з базою даних"""
    print("\n🗄️ Перевірка з'єднання з БД...")

    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result:
            print("✅ З'єднання з БД успішне")
            return True
        else:
            print("❌ Помилка з'єднання з БД")
            return False
    except Exception as e:
        print(f"❌ Помилка з'єднання з БД: {e}")
        return False

def check_static_files():
    """Перевірка статичних файлів"""
    print("\n📁 Перевірка статичних файлів...")

    try:
        from django.conf import settings
        from django.core.management import execute_from_command_line

        # Перевірка наявності директорії staticfiles
        static_root = Path(settings.STATIC_ROOT)
        if static_root.exists():
            print(f"✅ STATIC_ROOT існує: {static_root}")
        else:
            print(f"⚠️ STATIC_ROOT не існує: {static_root}")

        # Перевірка кількості файлів
        if static_root.exists():
            files_count = len(list(static_root.rglob('*')))
            print(f"📊 Знайдено {files_count} статичних файлів")

        return True

    except Exception as e:
        print(f"❌ Помилка перевірки статичних файлів: {e}")
        return False

def check_security_settings():
    """Перевірка налаштувань безпеки"""
    print("\n🔒 Перевірка налаштувань безпеки...")

    try:
        from django.conf import settings

        checks = [
            ('SECURE_SSL_REDIRECT', getattr(settings, 'SECURE_SSL_REDIRECT', False)),
            ('SECURE_HSTS_SECONDS', getattr(settings, 'SECURE_HSTS_SECONDS', 0)),
            ('SECURE_CONTENT_TYPE_NOSNIFF', getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False)),
            ('SECURE_BROWSER_XSS_FILTER', getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False)),
            ('X_FRAME_OPTIONS', getattr(settings, 'X_FRAME_OPTIONS', 'DENY')),
        ]

        for setting, value in checks:
            if isinstance(value, bool) and value:
                print(f"✅ {setting}: {value}")
            elif isinstance(value, int) and value > 0:
                print(f"✅ {setting}: {value}")
            elif isinstance(value, str) and value:
                print(f"✅ {setting}: {value}")
            else:
                print(f"⚠️ {setting}: {value}")

        # Перевірка CSRF trusted origins
        csrf_origins = getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])
        if csrf_origins:
            print(f"✅ CSRF_TRUSTED_ORIGINS налаштовані: {len(csrf_origins)} доменів")
        else:
            print("⚠️ CSRF_TRUSTED_ORIGINS не налаштовані")

        return True

    except Exception as e:
        print(f"❌ Помилка перевірки безпеки: {e}")
        return False

def check_optional_features():
    """Перевірка опціональних функцій"""
    print("\n🔧 Перевірка опціональних функцій...")

    features = [
        ('2FA', 'django_otp', 'two_factor'),
        ('Health checks', 'health_check'),
        ('Redis cache', 'django_redis'),
        ('Celery', 'celery'),
        ('OpenAI', 'openai'),
        ('Anthropic', 'anthropic'),
        ('LangChain', 'langchain'),
        ('PostgreSQL vector', 'pgvector'),
    ]

    for feature, *packages in features:
        available = True
        for package in packages:
            try:
                importlib.import_module(package)
            except ImportError:
                available = False
                break

        if available:
            print(f"✅ {feature} - доступний")
        else:
            print(f"⚠️ {feature} - недоступний")

def generate_report():
    """Генерація звіту про готовність системи"""
    print("\n" + "="*60)
    print("📋 ЗВІТ ПРО ГОТОВНІСТЬ SYSTЕМИ")
    print("="*60)

    checks = [
        ("Версія Python", check_python_version()),
        ("Залежності", check_dependencies()),
        ("Django налаштування", check_django_settings()),
        ("З'єднання з БД", check_database_connection()),
        ("Статичні файли", check_static_files()),
        ("Безпека", check_security_settings()),
    ]

    passed = 0
    total = len(checks)

    for check_name, result in checks:
        status = "✅ Пройдено" if result else "❌ Не пройдено"
        print("25")

        if result:
            passed += 1

    print(f"\n📊 Результати: {passed}/{total} перевірок пройдено")

    if passed == total:
        print("🎉 Система готова до розгортання!")
        return True
    else:
        print("⚠️ Є проблеми, які потрібно вирішити перед розгортанням")
        return False

def main():
    """Основна функція"""
    print("🚀 Перевірка готовності KavaCRM до розгортання")
    print("="*60)

    # Встановлення шляху до проекту
    project_path = Path(__file__).resolve().parent
    os.chdir(project_path)

    # Додавання шляху до Python path
    sys.path.insert(0, str(project_path))

    # Запуск перевірок
    success = generate_report()

    # Перевірка опціональних функцій
    check_optional_features()

    print("\n" + "="*60)
    if success:
        print("✅ СИСТЕМА ГОТОВА ДО РОЗГОРТАННЯ")
        print("\nНаступні кроки:")
        print("1. Налаштуйте змінні середовища (.env файл)")
        print("2. Запустіть міграції: python manage.py migrate")
        print("3. Зберіть статичні файли: python manage.py collectstatic")
        print("4. Створіть суперкористувача: python manage.py createsuperuser")
        print("5. Запустіть сервер: python manage.py runserver")
    else:
        print("❌ СИСТЕМА ПОТРЕБУЄ ДОНАЛАГОДЖЕННЯ")
        print("\nВиправте помилки та запустіть перевірку знову")

    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
