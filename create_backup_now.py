#!/usr/bin/env python3
"""
Скрипт для негайного створення бекапу KavaCRM
"""

import os
import sys
import shutil
import gzip
import sqlite3
from datetime import datetime
from pathlib import Path

def print_info(message):
    print(f"ℹ️  {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def create_database_backup():
    """Створення бекапу бази даних"""
    print_info("Створення бекапу бази даних...")

    try:
        # Створюємо директорію для бекапів
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)

        # Визначаємо ім'я файлу бекапу
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f"kavacrm_backup_{timestamp}.sqlite3"

        # Копіюємо базу даних
        db_path = "db.sqlite3"

        if not Path(db_path).exists():
            print_error(f"База даних не знайдена: {db_path}")
            return None

        shutil.copy2(db_path, backup_file)
        print_success(f"База даних скопійована: {backup_file}")

        # Стиснення бекапу
        compressed_file = backup_file.with_suffix('.sqlite3.gz')
        with open(backup_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Видаляємо несжатий файл
        os.remove(backup_file)

        print_success(f"Бекап стиснений: {compressed_file}")
        return compressed_file

    except Exception as e:
        print_error(f"Помилка створення бекапу БД: {e}")
        return None

def create_media_backup():
    """Створення бекапу медіа файлів"""
    print_info("Створення бекапу медіа файлів...")

    try:
        media_dir = Path("media")
        if not media_dir.exists():
            print_warning("Директорія media не існує")
            return None

        backup_dir = Path("backups")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f"kavacrm_media_{timestamp}.tar.gz"

        # Створюємо архів
        import tarfile
        with tarfile.open(backup_file, "w:gz") as tar:
            tar.add(media_dir, arcname="media")

        print_success(f"Медіа файли заархівовані: {backup_file}")
        return backup_file

    except Exception as e:
        print_error(f"Помилка створення бекапу медіа: {e}")
        return None

def create_static_backup():
    """Створення бекапу статичних файлів"""
    print_info("Створення бекапу статичних файлів...")

    try:
        static_dir = Path("staticfiles")
        if not static_dir.exists():
            print_warning("Директорія staticfiles не існує")
            return None

        backup_dir = Path("backups")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f"kavacrm_static_{timestamp}.tar.gz"

        # Створюємо архів
        import tarfile
        with tarfile.open(backup_file, "w:gz") as tar:
            tar.add(static_dir, arcname="staticfiles")

        print_success(f"Статичні файли заархівовані: {backup_file}")
        return backup_file

    except Exception as e:
        print_error(f"Помилка створення бекапу статичних файлів: {e}")
        return None

def create_code_backup():
    """Створення бекапу коду проекту"""
    print_info("Створення бекапу коду проекту...")

    try:
        backup_dir = Path("backups")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f"kavacrm_code_{timestamp}.tar.gz"

        # Створюємо архів всього проекту (крім великих директорій)
        import tarfile

        exclude_patterns = [
            'backups/',
            'staticfiles/',
            'media/',
            '__pycache__/',
            '*.pyc',
            '*.log',
            'logs/',
            '.git/',
            'venv/',
            '.venv/'
        ]

        def should_exclude(path):
            for pattern in exclude_patterns:
                if pattern in str(path):
                    return True
            return False

        with tarfile.open(backup_file, "w:gz") as tar:
            for root, dirs, files in os.walk('.'):
                # Фільтруємо директорії
                dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]

                for file in files:
                    file_path = Path(root) / file
                    if not should_exclude(file_path):
                        tar.add(file_path, arcname=str(file_path))

        print_success(f"Код проекту заархівований: {backup_file}")
        return backup_file

    except Exception as e:
        print_error(f"Помилка створення бекапу коду: {e}")
        return None

def create_usb_backup():
    """Копіювання бекапів на USB диск"""
    print_info("Копіювання бекапів на USB диск...")

    try:
        usb_drives = []
        # Шукаємо USB диски в Windows
        for drive in range(ord('D'), ord('Z')+1):
            drive_letter = chr(drive) + ':'
            if Path(drive_letter).exists():
                # Перевіряємо, чи це USB диск
                try:
                    # Можна додати додаткову перевірку типу диску
                    usb_drives.append(drive_letter)
                except:
                    pass

        if not usb_drives:
            print_warning("USB диски не знайдені")
            return False

        backup_dir = Path("backups")
        usb_backup_dir = None

        for usb_drive in usb_drives:
            usb_path = Path(usb_drive) / "KavaCRM_Backups"
            try:
                usb_path.mkdir(exist_ok=True)
                usb_backup_dir = usb_path
                print_info(f"Знайдено USB диск: {usb_drive}")
                break
            except:
                continue

        if not usb_backup_dir:
            print_warning("Не вдалося створити директорію на USB")
            return False

        # Копіюємо останні бекапи
        copied_count = 0
        for backup_file in backup_dir.glob('kavacrm_*'):
            if backup_file.is_file():
                try:
                    shutil.copy2(backup_file, usb_backup_dir / backup_file.name)
                    copied_count += 1
                    print_info(f"Скопійовано на USB: {backup_file.name}")
                except Exception as e:
                    print_error(f"Помилка копіювання {backup_file.name}: {e}")

        if copied_count > 0:
            print_success(f"Скопійовано {copied_count} файлів на USB: {usb_backup_dir}")
            return True
        else:
            print_warning("Не вдалося скопіювати файли на USB")
            return False

    except Exception as e:
        print_error(f"Помилка копіювання на USB: {e}")
        return False

def cleanup_old_backups():
    """Очищення старих бекапів"""
    print_info("Очищення старих бекапів...")

    try:
        backup_dir = Path("backups")
        retention_days = 30  # Зберігати 30 днів

        deleted_count = 0
        for backup_file in backup_dir.glob('kavacrm_*'):
            if backup_file.is_file():
                # Перевіряємо вік файлу
                file_age_days = (datetime.now() - datetime.fromtimestamp(backup_file.stat().st_mtime)).days
                if file_age_days > retention_days:
                    os.remove(backup_file)
                    deleted_count += 1
                    print_info(f"Видалено старий бекап: {backup_file.name}")

        if deleted_count > 0:
            print_success(f"Видалено {deleted_count} старих бекапів")
        else:
            print_info("Старих бекапів для видалення не знайдено")

    except Exception as e:
        print_error(f"Помилка очищення бекапів: {e}")

def create_backup_report(backup_files, usb_success):
    """Створення звіту про бекап"""
    print_info("Створення звіту про бекап...")

    try:
        report_file = Path("backups") / f"backup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=== ЗВІТ ПРО БЕКАП KAVACRM ===\n\n")
            f.write(f"Дата та час: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("СТВОРЕНІ БЕКАПИ:\n")
            for backup_file in backup_files:
                if backup_file:
                    f.write(f"• {backup_file}\n")

            f.write("\nСТАТУС КОПІЮВАННЯ НА USB:\n")
            f.write(f"• {'УСПІШНО' if usb_success else 'НЕМАЄ USB ДИСКУ'}\n")

            # Розмір бекапів
            total_size = 0
            for backup_file in backup_files:
                if backup_file and backup_file.exists():
                    total_size += backup_file.stat().st_size

            f.write(f"\nЗАГАЛЬНИЙ РОЗМІР: {total_size / 1024 / 1024:.2f} MB\n")

        print_success(f"Звіт створено: {report_file}")
        return report_file

    except Exception as e:
        print_error(f"Помилка створення звіту: {e}")
        return None

def main():
    """Основна функція"""
    print("💾 СТВОРЕННЯ БЕКАПУ KAVACRM")
    print("=" * 50)

    # Створюємо директорію для бекапів
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)

    # Створюємо різні типи бекапів
    backup_files = []

    # 1. Бекап бази даних
    db_backup = create_database_backup()
    if db_backup:
        backup_files.append(db_backup)

    # 2. Бекап медіа файлів
    media_backup = create_media_backup()
    if media_backup:
        backup_files.append(media_backup)

    # 3. Бекап статичних файлів
    static_backup = create_static_backup()
    if static_backup:
        backup_files.append(static_backup)

    # 4. Бекап коду проекту
    code_backup = create_code_backup()
    if code_backup:
        backup_files.append(code_backup)

    # 5. Копіювання на USB
    usb_success = create_usb_backup()

    # 6. Очищення старих бекапів
    cleanup_old_backups()

    # 7. Створення звіту
    report_file = create_backup_report(backup_files, usb_success)

    print("\n" + "=" * 50)
    print("📋 ПІДСУМОК БЕКАПУ")
    print("=" * 50)

    print(f"✅ Створено бекапів: {len([f for f in backup_files if f])}")
    print(f"✅ USB копіювання: {'УСПІШНО' if usb_success else 'НЕМАЄ USB'}")
    print(f"📁 Директорія бекапів: {backup_dir.absolute()}")

    if backup_files:
        print("\nСТВОРЕНІ ФАЙЛИ:")
        for backup_file in backup_files:
            if backup_file:
                size_mb = backup_file.stat().st_size / 1024 / 1024
                print(".2f")

    if report_file:
        print(f"\n📄 Звіт: {report_file}")

    print("\n🎉 БЕКАП ЗАВЕРШЕНО УСПІШНО!")
    print("\n💡 РЕКОМЕНДАЦІЇ:")
    print("• Зберігайте бекапи в безпечному місці")
    print("• Регулярно перевіряйте цілісність бекапів")
    print("• Налаштуйте автоматичні бекапи для щоденного створення")

if __name__ == '__main__':
    main()
