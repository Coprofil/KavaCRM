#!/usr/bin/env python3
"""
Скрипт для ініціалізації KavaCRM системи після розгортання
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description, cwd=None):
    """Виконання команди з обробкою помилок"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} - успішно")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - помилка:")
        print(e.stderr)
        return False

def setup_database():
    """Налаштування бази даних"""
    print("\n🗄️ Налаштування бази даних...")

    commands = [
        ("python manage.py makemigrations", "Створення міграцій"),
        ("python manage.py migrate", "Застосування міграцій"),
        ("python manage.py createinitialrevisions", "Створення ревізій (якщо потрібно)"),
    ]

    for command, description in commands:
        if not run_command(command, description):
            return False

    return True

def setup_static_files():
    """Налаштування статичних файлів"""
    print("\n📁 Налаштування статичних файлів...")

    return run_command("python manage.py collectstatic --noinput", "Збір статичних файлів")

def setup_admin_user():
    """Створення адміністратора"""
    print("\n👤 Створення адміністратора...")

    # Перевірка, чи існує суперкористувач
    result = subprocess.run(
        "python manage.py shell -c \"from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())\"",
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode == 0 and result.stdout.strip() == 'True':
        print("✅ Суперкористувач вже існує")
        return True

    # Створення суперкористувача
    print("Створення нового суперкористувача...")
    print("Логін: admin")
    print("Email: admin@kavacrm.com")
    print("Пароль: admin123")

    create_command = 'python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser(\'admin\', \'admin@kavacrm.com\', \'admin123\')"'

    return run_command(create_command, "Створення суперкористувача")

def setup_rag_system():
    """Ініціалізація RAG системи"""
    print("\n🤖 Ініціалізація RAG системи...")

    try:
        # Перевірка наявності RAG модуля
        from kavacrm.rag_system import RAGSystem

        # Ініціалізація системи
        rag = RAGSystem()

        # Створення тестового документа
        test_doc = {
            'title': 'Тестовий документ',
            'content': 'Це тестовий документ для перевірки RAG системи.',
            'content_type': 'manual',
            'object_id': None,
            'metadata': {'test': True}
        }

        # Додавання документа
        doc_id = rag.add_document(**test_doc)
        if doc_id:
            print(f"✅ Тестовий документ додано (ID: {doc_id})")

            # Тестовий пошук
            results = rag.search("тестовий документ", limit=5)
            if results:
                print(f"✅ Пошук працює: знайдено {len(results)} результатів")

            return True
        else:
            print("❌ Не вдалося додати тестовий документ")
            return False

    except ImportError:
        print("⚠️ RAG модуль недоступний - пропускаємо")
        return True
    except Exception as e:
        print(f"❌ Помилка ініціалізації RAG: {e}")
        return False

def setup_initial_data():
    """Створення початкових даних"""
    print("\n📊 Створення початкових даних...")

    # Створення тестового клієнта
    create_client_command = '''
python manage.py shell -c "
from kavacrm.models import Client
if not Client.objects.filter(name='Тестовий клієнт').exists():
    Client.objects.create(
        name='Тестовий клієнт',
        address='вул. Тестова, 1',
        comment='Тестовий клієнт для перевірки системи'
    )
    print('Тестовий клієнт створено')
else:
    print('Тестовий клієнт вже існує')
"
'''

    return run_command(create_client_command, "Створення тестового клієнта")

def setup_cron_jobs():
    """Налаштування cron завдань"""
    print("\n⏰ Налаштування cron завдань...")

    cron_commands = [
        "0 4 * * * /usr/local/bin/mount-usb-backup.sh",  # Щоденний бекап о 04:00
        "0 3 * * * /usr/local/bin/backup-postgresql.sh",  # Бекап БД о 03:00
        "*/5 * * * * /usr/local/bin/kavacrm-monitor.sh",  # Моніторинг кожні 5 хвилин
        "0 8 * * * curl -s https://yourdomain.com/health/detailed/ | jq -r '.application_stats' | /usr/local/bin/kavacrm-monitor.sh",  # Щоденний звіт
    ]

    # Створення crontab
    current_crontab = ""
    try:
        result = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            current_crontab = result.stdout
    except:
        pass

    # Додавання нових завдань
    for cron_cmd in cron_commands:
        if cron_cmd not in current_crontab:
            current_crontab += f"\n{cron_cmd}"

    # Оновлення crontab
    try:
        process = subprocess.Popen('crontab', stdin=subprocess.PIPE, text=True)
        process.communicate(current_crontab)
        if process.returncode == 0:
            print("✅ Cron завдання налаштовані")
            return True
        else:
            print("❌ Помилка налаштування cron")
            return False
    except Exception as e:
        print(f"❌ Помилка cron: {e}")
        return False

def setup_services():
    """Налаштування системних сервісів"""
    print("\n🔧 Налаштування системних сервісів...")

    services = [
        ("kavacrm-monitor.timer", "Моніторинг таймер"),
        ("postgresql", "PostgreSQL"),
        ("nginx", "Nginx"),
        ("redis-server", "Redis"),
    ]

    for service, description in services:
        try:
            result = subprocess.run(
                f"sudo systemctl is-enabled {service}",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ {description} - увімкнено")
            else:
                print(f"⚠️ {description} - не увімкнено")
        except:
            print(f"⚠️ {description} - сервіс недоступний")

    return True

def test_system():
    """Тестування системи"""
    print("\n🧪 Тестування системи...")

    # Тест Django
    if run_command("python manage.py check", "Перевірка Django конфігурації"):
        print("✅ Django конфігурація коректна")
    else:
        print("❌ Помилки в Django конфігурації")
        return False

    # Тест статичних файлів
    try:
        from django.conf import settings
        static_url = settings.STATIC_URL
        print(f"✅ Статичні файли налаштовані: {static_url}")
    except:
        print("⚠️ Статичні файли не налаштовані")

    return True

def main():
    """Основна функція"""
    print("🚀 ІНІЦІАЛІЗАЦІЯ KAVACRM СИСТЕМИ")
    print("="*60)

    # Встановлення шляху до проекту
    project_path = Path(__file__).resolve().parent
    os.chdir(project_path)

    # Додавання шляху до Python path
    sys.path.insert(0, str(project_path))

    # Встановлення Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kavapro.settings')

    # Ініціалізація Django
    import django
    django.setup()

    # Запуск ініціалізації
    steps = [
        ("База даних", setup_database),
        ("Статичні файли", setup_static_files),
        ("Адміністратор", setup_admin_user),
        ("RAG система", setup_rag_system),
        ("Початкові дані", setup_initial_data),
        ("Cron завдання", setup_cron_jobs),
        ("Системні сервіси", setup_services),
        ("Тестування", test_system),
    ]

    success_count = 0

    for step_name, step_func in steps:
        try:
            if step_func():
                success_count += 1
            else:
                print(f"⚠️ Крок '{step_name}' завершився з попередженнями")
        except Exception as e:
            print(f"❌ Помилка в кроці '{step_name}': {e}")

    print("\n" + "="*60)
    print(f"📊 РЕЗУЛЬТАТИ ІНІЦІАЛІЗАЦІЇ: {success_count}/{len(steps)} кроків успішно")

    if success_count == len(steps):
        print("🎉 СИСТЕМА ПОВНІСТЮ ІНІЦІАЛІЗОВАНА!")
        print("\n🌐 Доступ до системи:")
        print("• Адмін панель: /secure-admin-panel-2024/")
        print("• Основний сайт: /")
        print("• API: /api/")
        print("• Моніторинг: /health/")
        print("\n🔐 Адмін облікові дані:")
        print("Логін: admin")
        print("Пароль: admin123")
        print("\n⚠️ ОБОВ'ЯЗКОВО ЗМІНІТЬ ПАРОЛЬ ПІСЛЯ ПЕРШОГО ВХОДУ!")
    else:
        print("⚠️ ІНІЦІАЛІЗАЦІЯ ЗАВЕРШЕНА З ПОПЕРЕДЖЕННЯМИ")
        print("Перевірте логи вище та виправте проблеми")

    return success_count == len(steps)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
