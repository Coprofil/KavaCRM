#!/usr/bin/env python3
"""
Простий скрипт для бекапу KavaCRM
"""

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def print_info(message):
    print(f"ℹ️  {message}")

def print_success(message):
    print(f"✅ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def print_error(message):
    print(f"❌ {message}")

def create_backup():
    """Створення бекапу"""
    print("💾 СТВОРЕННЯ БЕКАПУ KAVACRM")
    print("=" * 50)

    # Створюємо директорію для бекапів
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)

    # Часова мітка
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    backup_files = []

    # 1. Бекап бази даних
    print_info("Створення бекапу бази даних...")
    db_path = Path("db.sqlite3")
    if db_path.exists():
        backup_db = backup_dir / f"kavacrm_db_{timestamp}.sqlite3"
        shutil.copy2(db_path, backup_db)
        backup_files.append(backup_db)
        print_success(f"База даних скопійована: {backup_db.name}")
    else:
        print_warning("База даних не знайдена")

    # 2. Бекап медіа файлів
    print_info("Створення бекапу медіа файлів...")
    media_dir = Path("media")
    if media_dir.exists() and any(media_dir.iterdir()):
        backup_media = backup_dir / f"kavacrm_media_{timestamp}.zip"
        with zipfile.ZipFile(backup_media, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(media_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(media_dir.parent)
                    zipf.write(file_path, arcname)
        backup_files.append(backup_media)
        print_success(f"Медіа файли заархівовані: {backup_media.name}")
    else:
        print_warning("Медіа файли відсутні")

    # 3. Бекап статичних файлів
    print_info("Створення бекапу статичних файлів...")
    static_dir = Path("staticfiles")
    if static_dir.exists() and any(static_dir.iterdir()):
        backup_static = backup_dir / f"kavacrm_static_{timestamp}.zip"
        with zipfile.ZipFile(backup_static, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(static_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(static_dir.parent)
                    zipf.write(file_path, arcname)
        backup_files.append(backup_static)
        print_success(f"Статичні файли заархівовані: {backup_static.name}")
    else:
        print_warning("Статичні файли відсутні")

    # 4. Створення звіту
    print_info("Створення звіту...")
    report_file = backup_dir / f"backup_report_{timestamp}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=== ЗВІТ ПРО БЕКАП KAVACRM ===\n\n")
        f.write(f"Дата та час: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("СТВОРЕНІ ФАЙЛИ:\n")

        total_size = 0
        for backup_file in backup_files:
            if backup_file.exists():
                size_mb = backup_file.stat().st_size / 1024 / 1024
                f.write(".2f")
                total_size += backup_file.stat().st_size

        f.write(f"\nЗАГАЛЬНИЙ РОЗМІР: {total_size / 1024 / 1024:.2f} MB\n")

    backup_files.append(report_file)
    print_success(f"Звіт створено: {report_file.name}")

    # Підсумок
    print("\n" + "=" * 50)
    print("📋 ПІДСУМОК БЕКАПУ")
    print("=" * 50)

    print(f"📁 Директорія бекапів: {backup_dir.absolute()}")
    print(f"📊 Створено файлів: {len(backup_files)}")

    for backup_file in backup_files:
        if backup_file.exists():
            size_mb = backup_file.stat().st_size / 1024 / 1024
            print(".2f")

    print_success("🎉 БЕКАП ЗАВЕРШЕНО УСПІШНО!")

    return backup_files

if __name__ == '__main__':
    try:
        create_backup()
    except Exception as e:
        print_error(f"Критична помилка: {e}")
        import traceback
        traceback.print_exc()
