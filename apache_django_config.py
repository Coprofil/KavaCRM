#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Повна конфігурація Apache для Django
"""
import os
import sys

def find_apache_config():
    """Знаходимо конфігураційні файли Apache"""
    possible_paths = [
        r'C:\Apache24\conf\httpd.conf',
        r'C:\Apache2.4\conf\httpd.conf',
        r'C:\Program Files\Apache Group\Apache2\conf\httpd.conf',
        r'C:\Program Files\Apache Software Foundation\Apache2.4\conf\httpd.conf'
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None

def create_wsgi_file():
    """Створюємо WSGI файл для Django"""
    wsgi_content = '''"""
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
'''

    wsgi_path = r'C:\srv\kava\app\kavapro\kavapro\wsgi.py'
    try:
        with open(wsgi_path, 'w', encoding='utf-8') as f:
            f.write(wsgi_content)
        print(f"✅ Створено WSGI файл: {wsgi_path}")
        return True
    except Exception as e:
        print(f"❌ Помилка створення WSGI файлу: {e}")
        return False

def create_apache_config():
    """Створюємо конфігурацію Apache для Django"""
    apache_config = '''
# Django додаток KavaCRM
<VirtualHost *:80>
    ServerName kava-crm.asuscomm.com
    ServerAlias localhost 127.0.0.1 kava-crm.asuscomm.com www.kava-crm.asuscomm.com
    DocumentRoot "C:/srv/kava/app/kavapro"

    # WSGI налаштування
    WSGIScriptAlias /crm "C:/srv/kava/app/kavapro/kavapro/wsgi.py"
    WSGIPythonPath "C:/srv/kava/app/kavapro"

    # Статичні файли
    Alias /crm/static/ "C:/srv/kava/app/kavapro/staticfiles/"
    <Directory "C:/srv/kava/app/kavapro/staticfiles/">
        Require all granted
    </Directory>

    # Медіа файли
    Alias /crm/media/ "C:/srv/kava/app/kavapro/media/"
    <Directory "C:/srv/kava/app/kavapro/media/">
        Require all granted
    </Directory>

    # Доступ до проекту
    <Directory "C:/srv/kava/app/kavapro">
        <Files wsgi.py>
            Require all granted
        </Files>
        Require all granted
    </Directory>

    # Логи
    ErrorLog "C:/srv/kava/app/kavapro/logs/apache_error.log"
    CustomLog "C:/srv/kava/app/kavapro/logs/apache_access.log" common

    # Додаткові налаштування
    WSGIDaemonProcess kavacrm python-path="C:/srv/kava/app/kavapro" python-home="C:/srv/kava/app/kavapro/venv"
    WSGIProcessGroup kavacrm
    WSGIApplicationGroup %{GLOBAL}

    # Таймаути
    WSGISocketTimeout 30
    WSGIRetryTimeout 30
</VirtualHost>

# SSL конфігурація (якщо потрібна)
<VirtualHost *:443>
    ServerName localhost
    DocumentRoot "C:/srv/kava/app/kavapro"

    SSLEngine on
    SSLCertificateFile "C:/srv/kava/app/kavapro/ssl/cert.pem"
    SSLCertificateKeyFile "C:/srv/kava/app/kavapro/ssl/key.pem"

    WSGIScriptAlias / "C:/srv/kava/app/kavapro/kavapro/wsgi.py"
    WSGIPythonPath "C:/srv/kava/app/kavapro"

    <Directory "C:/srv/kava/app/kavapro">
        Require all granted
    </Directory>

    Alias /static/ "C:/srv/kava/app/kavapro/staticfiles/"
    <Directory "C:/srv/kava/app/kavapro/staticfiles/">
        Require all granted
    </Directory>
</VirtualHost>
'''

    config_path = r'C:\srv\kava\app\kavapro\apache_django.conf'
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(apache_config)
        print(f"✅ Створено конфігурацію Apache: {config_path}")
        return config_path
    except Exception as e:
        print(f"❌ Помилка створення конфігурації: {e}")
        return None

def update_main_apache_config(virtual_host_config):
    """Додаємо VirtualHost до основної конфігурації Apache"""
    httpd_conf = find_apache_config()
    if not httpd_conf:
        print("❌ httpd.conf не знайдено")
        return False

    try:
        with open(httpd_conf, 'r', encoding='utf-8') as f:
            content = f.read()

        # Перевіряємо чи вже додано наш VirtualHost
        if 'kavacrm' in content and 'wsgi.py' in content:
            print("✅ Конфігурація Django вже присутня в Apache")
            return True

        # Додаємо включення нашої конфігурації
        include_line = f'\n# Django KavaCRM\nInclude "{virtual_host_config}"\n'

        # Знаходимо місце для додавання
        if '#LoadModule' in content:
            # Додаємо після LoadModule секції
            lines = content.split('\n')
            insert_index = -1
            for i, line in enumerate(lines):
                if line.startswith('#LoadModule'):
                    continue
                elif not line.startswith('LoadModule') and insert_index == -1:
                    insert_index = i
                    break

            if insert_index > 0:
                lines.insert(insert_index, include_line)
                content = '\n'.join(lines)
            else:
                content += include_line
        else:
            content += include_line

        # Зберігаємо оновлену конфігурацію
        with open(httpd_conf, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Оновлено основну конфігурацію Apache: {httpd_conf}")
        return True

    except Exception as e:
        print(f"❌ Помилка оновлення конфігурації: {e}")
        return False

def main():
    print("=== КОНФІГУРАЦІЯ APACHE ДЛЯ DJANGO ===")

    # 1. Створюємо WSGI файл
    print("\n[1/4] Створюємо WSGI файл...")
    if not create_wsgi_file():
        return False

    # 2. Створюємо конфігурацію Apache
    print("\n[2/4] Створюємо конфігурацію Apache...")
    config_file = create_apache_config()
    if not config_file:
        return False

    # 3. Знаходимо основну конфігурацію Apache
    print("\n[3/4] Знаходимо основну конфігурацію Apache...")
    httpd_conf = find_apache_config()
    if httpd_conf:
        print(f"✅ Знайдено: {httpd_conf}")
    else:
        print("❌ httpd.conf не знайдено в стандартних місцях")
        print("Можливі місця:")
        print("- C:\\Apache24\\conf\\httpd.conf")
        print("- C:\\Apache2.4\\conf\\httpd.conf")
        print("- C:\\Program Files\\Apache*\\conf\\httpd.conf")
        return False

    # 4. Оновлюємо основну конфігурацію
    print("\n[4/4] Оновлюємо основну конфігурацію...")
    if update_main_apache_config(config_file):
        print("\n" + "="*50)
        print("КОНФІГУРАЦІЯ ЗАВЕРШЕНА!")
        print("="*50)
        print("\nНаступні кроки:")
        print("1. Перевірте конфігурацію: httpd -t")
        print("2. Перезапустіть Apache: net stop Apache2.4 && net start Apache2.4")
        print("3. Протестуйте: http://localhost/")
        print("4. Якщо помилки - перевірте логи:")
        print("   C:\\Apache24\\logs\\error.log")
        print("\nФайли створені:")
        print("- C:\\srv\\kava\\app\\kavapro\\kavapro\\wsgi.py")
        print("- C:\\srv\\kava\\app\\kavapro\\apache_django.conf")
        return True
    else:
        print("❌ Не вдалося оновити конфігурацію")
        return False

if __name__ == '__main__':
    main()
