#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Управління HTTPS сертифікатами та налаштуваннями для KavaCRM
"""

import os
import sys
import ssl
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta

def print_header(text):
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def print_success(text):
    print(f"✅ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def create_self_signed_cert(cert_dir="certs", domain="localhost", days=365):
    """Створення самопідписаного сертифікату"""
    print_header("СТВОРЕННЯ САМОПІДПИСАНОГО СЕРТИФІКАТУ")

    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend

        # Створюємо директорію
        cert_path = Path(cert_dir)
        cert_path.mkdir(exist_ok=True)

        cert_file = cert_path / f"{domain}.crt"
        key_file = cert_path / f"{domain}.key"
        pfx_file = cert_path / f"{domain}.pfx"

        # Генеруємо приватний ключ
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Створюємо сертифікат
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "UA"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Kyiv"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Kyiv"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "KavaCRM"),
            x509.NameAttribute(NameOID.COMMON_NAME, domain),
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            subject  # Самопідписаний
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=days)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(domain),
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256(), default_backend())

        # Зберігаємо сертифікат (PEM)
        with open(cert_file, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        # Зберігаємо приватний ключ (PEM)
        with open(key_file, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Створюємо PFX файл для Windows/IIS
        try:
            pfx_data = cert.public_bytes(serialization.Encoding.PEM) + private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            with open(pfx_file, 'wb') as f:
                f.write(pfx_data)

            print_success(f"PFX файл створено: {pfx_file}")
        except:
            print_warning("Не вдалося створити PFX файл")

        print_success(f"Сертифікат: {cert_file}")
        print_success(f"Ключ: {key_file}")
        print_info(f"Дійсний до: {datetime.utcnow() + timedelta(days=days)}")

        # Інформація про сертифікат
        cert_info = {
            "domain": domain,
            "created": datetime.utcnow().isoformat(),
            "expires": (datetime.utcnow() + timedelta(days=days)).isoformat(),
            "cert_file": str(cert_file),
            "key_file": str(key_file),
            "self_signed": True
        }

        # Зберігаємо інформацію
        info_file = cert_path / f"{domain}_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(cert_info, f, indent=2, ensure_ascii=False)

        print_success(f"Інформація збережена: {info_file}")

        return {
            "cert_file": cert_file,
            "key_file": key_file,
            "info": cert_info
        }

    except ImportError:
        print_error("cryptography не встановлена!")
        print_info("Встановіть: pip install cryptography")
        return None
    except Exception as e:
        print_error(f"Помилка створення сертифікату: {e}")
        return None

def check_cert_info(cert_dir="certs", domain="localhost"):
    """Перевірка інформації про сертифікат"""
    print_header("ПЕРЕВІРКА СЕРТИФІКАТУ")

    info_file = Path(cert_dir) / f"{domain}_info.json"
    cert_file = Path(cert_dir) / f"{domain}.crt"

    if info_file.exists():
        with open(info_file, 'r', encoding='utf-8') as f:
            info = json.load(f)

        print_info("Інформація про сертифікат:")
        print(f"  Домен: {info['domain']}")
        print(f"  Створено: {info['created']}")
        print(f"  Дійсний до: {info['expires']}")
        print(f"  Самопідписаний: {'Так' if info['self_signed'] else 'Ні'}")

        # Перевіряємо термін дії
        expires = datetime.fromisoformat(info['expires'])
        days_left = (expires - datetime.utcnow()).days

        if days_left > 30:
            print_success(f"Дійсний ще {days_left} днів")
        elif days_left > 0:
            print_warning(f"Закінчується через {days_left} днів")
        else:
            print_error("Сертифікат прострочений!")

    if cert_file.exists():
        print_success(f"Файл сертифікату існує: {cert_file}")

        # Спробуємо завантажити сертифікат
        try:
            with open(cert_file, 'rb') as f:
                cert_data = f.read()

            cert = ssl.load_certificate(ssl.Purpose.CLIENT_AUTH, cert_data)
            subject = dict(cert.get_subject().get_components())
            issuer = dict(cert.get_issuer().get_components())

            print_info("Суб'єкт сертифікату:")
            for key, value in subject.items():
                print(f"  {key.decode()}: {value.decode()}")

            print_info("Видавець:")
            for key, value in issuer.items():
                print(f"  {key.decode()}: {value.decode()}")

        except Exception as e:
            print_error(f"Помилка читання сертифікату: {e}")
    else:
        print_error(f"Файл сертифікату не знайдено: {cert_file}")

def update_django_settings_for_https():
    """Оновлення Django налаштувань для HTTPS"""
    print_header("ОНОВЛЕННЯ DJANGO НАЛАШТУВАНЬ")

    settings_file = Path("kavapro/settings.py")

    if not settings_file.exists():
        print_error("settings.py не знайдено!")
        return

    # Читаємо поточний вміст
    with open(settings_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Перевіряємо наявність HTTPS налаштувань
    https_settings = [
        "SECURE_SSL_REDIRECT = True",
        "SECURE_HSTS_SECONDS = 31536000",
        "SECURE_HSTS_INCLUDE_SUBDOMAINS = True",
        "SECURE_HSTS_PRELOAD = True",
        "SECURE_CONTENT_TYPE_NOSNIFF = True",
        "SECURE_BROWSER_XSS_FILTER = True",
        "SESSION_COOKIE_SECURE = True",
        "CSRF_COOKIE_SECURE = True"
    ]

    missing_settings = []
    for setting in https_settings:
        if setting not in content:
            missing_settings.append(setting)

    if missing_settings:
        print_warning("Знайдені відсутні HTTPS налаштування:")

        # Створюємо резервну копію
        backup_file = settings_file.with_suffix('.backup')
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print_success(f"Резервна копія створена: {backup_file}")

        # Додаємо відсутні налаштування
        https_block = "\n# HTTPS Безпека налаштування\n"
        for setting in missing_settings:
            https_block += f"{setting}\n"

        # Знаходимо місце для вставки (перед останнім рядком)
        lines = content.split('\n')
        insert_index = len(lines) - 1

        # Шукаємо кінець файлу
        for i, line in enumerate(lines):
            if line.strip() == "":
                continue
            if not line.startswith('#') and not line.startswith(' ') and not line.startswith('\t'):
                insert_index = i + 1

        # Вставляємо HTTPS налаштування
        lines.insert(insert_index, https_block)

        # Записуємо оновлений файл
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print_success("HTTPS налаштування додано до settings.py")
        print_info("Додані налаштування:")
        for setting in missing_settings:
            print(f"  • {setting}")
    else:
        print_success("Всі HTTPS налаштування вже присутні")

def create_nginx_config(domain="kavacrm.local", port=8000):
    """Створення Nginx конфігурації"""
    print_header("СТВОРЕННЯ NGINX КОНФІГУРАЦІЇ")

    nginx_dir = Path("nginx")
    nginx_dir.mkdir(exist_ok=True)

    config_file = nginx_dir / f"{domain}.conf"

    config_content = f"""# KavaCRM HTTPS конфігурація для {domain}

# Перенаправлення HTTP на HTTPS
server {{
    listen 80;
    server_name {domain} www.{domain};
    return 301 https://$server_name$request_uri;
}}

# HTTPS конфігурація
server {{
    listen 443 ssl http2;
    server_name {domain} www.{domain};

    # SSL сертифікати
    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;

    # SSL налаштування
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Безпека заголовків
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Статичні файли
    location /crm/static/ {{
        alias /path/to/your/project/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}

    # Медіа файли
    location /crm/media/ {{
        alias /path/to/your/project/media/;
        expires 1y;
        add_header Cache-Control "public";
    }}

    # Основне проксування до Django
    location / {{
        proxy_pass http://127.0.0.1:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;

        # Таймаути
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Буферизація
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }}

    # Health check endpoint
    location /health/ {{
        proxy_pass http://127.0.0.1:{port}/health/;
        access_log off;
    }}

    # Логи
    access_log /var/log/nginx/{domain}_access.log;
    error_log /var/log/nginx/{domain}_error.log;
}}

# Let's Encrypt challenge
server {{
    listen 80;
    server_name {domain} www.{domain};
    location /.well-known/acme-challenge/ {{
        root /var/www/certbot;
    }}
}}
"""

    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)

    print_success(f"Nginx конфігурація створена: {config_file}")
    print_info("Для використання:")
    print("1. Замініть /path/to/your/project/ на реальний шлях")
    print("2. Скопіюйте файл до /etc/nginx/sites-available/")
    print("3. Створіть symlink: ln -s ../sites-available/{domain}.conf .")
    print("4. Перевірте: nginx -t")
    print("5. Перезавантажте: systemctl reload nginx")

def create_apache_config(domain="kavacrm.local", port=8000):
    """Створення Apache конфігурації"""
    print_header("СТВОРЕННЯ APACHE КОНФІГУРАЦІЇ")

    apache_dir = Path("apache")
    apache_dir.mkdir(exist_ok=True)

    config_file = apache_dir / f"{domain}.conf"

    config_content = f"""# KavaCRM HTTPS конфігурація для {domain}

<VirtualHost *:80>
    ServerName {domain}
    ServerAlias www.{domain}

    # Перенаправлення на HTTPS
    Redirect permanent / https://{domain}/
</VirtualHost>

<VirtualHost *:443>
    ServerName {domain}
    ServerAlias www.{domain}

    # SSL конфігурація
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/{domain}/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/{domain}/privkey.pem

    # HSTS
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"

    # Безпека заголовків
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"

    # Статичні файли
    Alias /crm/static/ /path/to/your/project/staticfiles/
    <Directory "/path/to/your/project/staticfiles/">
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 1 year"
        Header set Cache-Control "public, immutable"
    </Directory>

    # Медіа файли
    Alias /crm/media/ /path/to/your/project/media/
    <Directory "/path/to/your/project/media/">
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 1 year"
        Header set Cache-Control "public"
    </Directory>

    # Проксування до Django
    ProxyPass / http://127.0.0.1:{port}/
    ProxyPassReverse / http://127.0.0.1:{port}/

    # Заголовки для проксі
    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-Host %{HTTP_HOST}s
    RequestHeader set X-Forwarded-Port 443

    # Таймаути
    ProxyTimeout 60

    # Логи
    ErrorLog ${{APACHE_LOG_DIR}}/{domain}_error.log
    CustomLog ${{APACHE_LOG_DIR}}/{domain}_access.log combined
</VirtualHost>
"""

    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)

    print_success(f"Apache конфігурація створена: {config_file}")
    print_info("Для використання:")
    print("1. Замініть /path/to/your/project/ на реальний шлях")
    print("2. Скопіюйте файл до /etc/apache2/sites-available/")
    print("3. Активуйте: a2ensite {domain}")
    print("4. Перевірте: apache2ctl configtest")
    print("5. Перезавантажте: systemctl reload apache2")

def main():
    """Основна функція"""
    parser = argparse.ArgumentParser(description='Управління HTTPS сертифікатами')
    parser.add_argument('action', choices=['create', 'check', 'django', 'nginx', 'apache'],
                       help='Дія для виконання')
    parser.add_argument('--domain', default='localhost',
                       help='Домен для сертифікату (default: localhost)')
    parser.add_argument('--cert-dir', default='certs',
                       help='Директорія для сертифікатів (default: certs)')
    parser.add_argument('--days', type=int, default=365,
                       help='Термін дії сертифікату в днях (default: 365)')

    args = parser.parse_args()

    if args.action == 'create':
        result = create_self_signed_cert(args.cert_dir, args.domain, args.days)
        if result:
            print_success("Сертифікат успішно створено!")
        else:
            print_error("Не вдалося створити сертифікат")

    elif args.action == 'check':
        check_cert_info(args.cert_dir, args.domain)

    elif args.action == 'django':
        update_django_settings_for_https()

    elif args.action == 'nginx':
        create_nginx_config(args.domain)

    elif args.action == 'apache':
        create_apache_config(args.domain)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Інтерактивний режим
        print_header("УПРАВЛІННЯ HTTPS СЕРТИФІКАТАМИ")

        while True:
            print("\nОберіть дію:")
            print("1. Створити самопідписаний сертифікат")
            print("2. Перевірити сертифікат")
            print("3. Оновити Django налаштування")
            print("4. Створити Nginx конфігурацію")
            print("5. Створити Apache конфігурацію")
            print("6. Вихід")

            choice = input("\nВаш вибір (1-6): ").strip()

            if choice == '1':
                domain = input("Домен (default: localhost): ").strip() or "localhost"
                cert_dir = input("Директорія (default: certs): ").strip() or "certs"
                days = input("Днів дії (default: 365): ").strip() or "365"
                create_self_signed_cert(cert_dir, domain, int(days))

            elif choice == '2':
                domain = input("Домен (default: localhost): ").strip() or "localhost"
                cert_dir = input("Директорія (default: certs): ").strip() or "certs"
                check_cert_info(cert_dir, domain)

            elif choice == '3':
                update_django_settings_for_https()

            elif choice == '4':
                domain = input("Домен (default: kavacrm.local): ").strip() or "kavacrm.local"
                create_nginx_config(domain)

            elif choice == '5':
                domain = input("Домен (default: kavacrm.local): ").strip() or "kavacrm.local"
                create_apache_config(domain)

            elif choice == '6':
                print_success("До побачення!")
                break

            else:
                print_error("Невірний вибір!")
    else:
        main()
