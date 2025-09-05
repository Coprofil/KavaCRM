#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Альтернативні способи доступу до сервера
"""
import requests
import subprocess
import sys

def run_command(cmd):
    """Виконання команди"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def create_alternative_access():
    print("=== АЛЬТЕРНАТИВНІ СПОСОБИ ДОСТУПУ ===")

    # 1. Перевірка доступних портів
    print("\n[1/4] Перевірка доступних портів...")
    ports_to_try = [80, 8080, 3000, 5000, 9000]

    for port in ports_to_try:
        code, out, err = run_command(f'netstat -ano | findstr :{port}')
        if code != 0:
            print(f"   ✅ Порт {port} вільний")
        else:
            print(f"   ❌ Порт {port} зайнятий")

    # 2. Створення альтернативної конфігурації
    print("\n[2/4] Створення альтернативної конфігурації...")

    alt_config = f'''# Альтернативна конфігурація сервера
# Для використання якщо порт 8000 недоступний

# Варіант 1: Порт 8080
# python manage.py runserver 0.0.0.0:8080

# Варіант 2: Порт 80 (потребує прав адміністратора)
# python manage.py runserver 0.0.0.0:80

# Варіант 3: З HTTPS (якщо налаштований сертифікат)
# python manage.py runserver_plus 0.0.0.0:8443 --cert-file cert.pem --key-file key.pem
'''

    with open('alternative_server_config.txt', 'w', encoding='utf-8') as f:
        f.write(alt_config)

    print("   ✅ Альтернативна конфігурація створена")

    # 3. Тестування альтернативних портів
    print("\n[3/4] Тестування альтернативних портів...")

    # Спробуємо запустити сервер на порту 8080
    print("   Перевірка порту 8080...")
    code, out, err = run_command('netstat -ano | findstr :8080')
    if code != 0:
        print("   ✅ Порт 8080 вільний - можна використовувати")

        # Створюємо альтернативний бат файл
        alt_batch = '''@echo off
cd /d C:\\srv\\kava\\app\\kavapro
set DJANGO_SETTINGS_MODULE=kavapro.settings
set PYTHONPATH=C:\\srv\\kava\\app\\kavapro
python manage.py runserver 0.0.0.0:8080 --noreload --insecure --skip-checks --verbosity=0
'''

        with open('start_server_alt.bat', 'w', encoding='utf-8') as f:
            f.write(alt_batch)

        print("   ✅ Альтернативний бат файл створено: start_server_alt.bat")
    else:
        print("   ❌ Порт 8080 зайнятий")

    # 4. Створення VPN рішення (якщо потрібно)
    print("\n[4/4] Створення VPN інструкцій...")

    vpn_guide = '''
АЛЬТЕРНАТИВНЕ РІШЕННЯ: VPN ДОСТУП

Якщо Port Forwarding не працює, налаштуйте VPN:

1. В роутері увімкніть VPN Server:
   - Advanced Settings → VPN → VPN Server
   - Протокол: OpenVPN або WireGuard
   - Створіть користувача та пароль

2. Підключіться до VPN з зовнішньої мережі

3. Після підключення використовуйте:
   - http://192.168.50.61:8000/ (локальна мережа через VPN)
   - http://localhost:8000/ (якщо VPN налаштований правильно)

Переваги VPN:
+ Безпечніше ніж Port Forwarding
+ Доступ до всіх внутрішніх ресурсів
- Потрібно встановлювати VPN клієнт
'''

    with open('vpn_access_guide.txt', 'w', encoding='utf-8') as f:
        f.write(vpn_guide)

    print("   ✅ VPN інструкції створені: vpn_access_guide.txt")

    # 5. Підсумок
    print("\n" + "="*50)
    print("АЛЬТЕРНАТИВНІ ВАРІАНТИ ДОСТУПУ:")
    print("="*50)
    print()
    print("1. ЗМІНИТИ ПОРТ:")
    print("   - Запустіть: start_server_alt.bat")
    print("   - Протестуйте: http://46.118.98.38:8080/")
    print()
    print("2. VPN ДОСТУП:")
    print("   - Прочитайте: vpn_access_guide.txt")
    print("   - Налаштуйте VPN в роутері")
    print()
    print("3. ПРОКСІ СЕРВЕР:")
    print("   - Використовуйте Cloudflare Tunnel або ngrok")
    print("   - Безкоштовний HTTPS доступ")
    print()
    print("4. ДИНАМІЧНИЙ DNS:")
    print("   - Якщо ASUS DDNS не працює, використовуйте:")
    print("   - noip.com, dyndns.org, або duckdns.org")
    print()
    print("="*50)

if __name__ == '__main__':
    create_alternative_access()
