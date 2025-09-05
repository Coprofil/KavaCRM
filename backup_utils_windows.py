"""
Backup utilities for KavaCRM - Windows optimized version
Розширена версія з підтримкою Windows, ротації та моніторингу
"""

import os
import shutil
import subprocess
import gzip
import zipfile
import json
import configparser
from datetime import datetime, timedelta
from pathlib import Path
from django.conf import settings
import logging
import platform

logger = logging.getLogger(__name__)

class WindowsBackupManager:
    """Менеджер бекапів для Windows"""

    def __init__(self, config_file=None):
        self.config_file = Path(config_file or "backups/backup_config.ini")
        self.config = self._load_config()
        self.backup_dir = Path(self.config.get('BACKUP', 'backup_dir', fallback='backups'))
        # Старий формат - більше не використовується
        # self.usb_label = self.config.get('BACKUP', 'usb_drive_label', fallback='KAVA_BACKUP')
        self.usb_backup_dir = self.config.get('BACKUP', 'usb_backup_dir', fallback='kavacrm_backups')
        self.custom_backup_path = self.config.get('BACKUP', 'custom_backup_path', fallback='')
        self.secondary_backup_path = self.config.get('BACKUP', 'secondary_backup_path', fallback='')
        self.backup_frequency = self.config.get('BACKUP', 'backup_frequency', fallback='daily')
        self.schedule_time = self.config.get('BACKUP', 'schedule_time', fallback='04:00')
        self.weekly_days = self.config.get('BACKUP', 'weekly_days', fallback='[]')
        self.retention_days = int(self.config.get('BACKUP', 'retention_days', fallback='30'))
        self.compression_level = int(self.config.get('BACKUP', 'compression_level', fallback='6'))
        self.usb_backup_enabled = self.config.getboolean('BACKUP', 'usb_backup_enabled', fallback=False)

        # Створюємо директорії
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        (self.backup_dir / "logs").mkdir(exist_ok=True)
        (self.backup_dir / "temp").mkdir(exist_ok=True)

    def should_run_backup(self):
        """
        Перевіряє чи потрібно виконувати бекап згідно з розкладом
        """
        from datetime import datetime

        if self.backup_frequency == 'manual':
            return False

        now = datetime.now()
        current_time = now.strftime('%H:%M')
        current_day = now.weekday()  # 0 = Понеділок, 6 = Неділя

        # Перевіряємо час
        if current_time != self.schedule_time:
            return False

        # Перевіряємо періодичність
        if self.backup_frequency == 'daily':
            return True
        elif self.backup_frequency == 'weekly':
            try:
                weekly_days = json.loads(self.weekly_days) if isinstance(self.weekly_days, str) else self.weekly_days
                return str(current_day) in weekly_days
            except (json.JSONDecodeError, TypeError):
                return False
        elif self.backup_frequency == 'monthly':
            return now.day == 1  # Перший день місяця

        return False

    def _load_config(self):
        """Завантаження конфігурації"""
        config = configparser.ConfigParser()

        if self.config_file.exists():
            config.read(self.config_file, encoding='utf-8')
        else:
            # Створюємо конфігурацію за замовчуванням
            config.add_section('BACKUP')
            config.set('BACKUP', 'backup_dir', 'backups')
            config.set('BACKUP', 'usb_drive_label', 'KAVA_BACKUP')
            config.set('BACKUP', 'usb_backup_dir', 'kavacrm_backups')
            config.set('BACKUP', 'retention_days', '30')
            config.set('BACKUP', 'compression_level', '6')

            config.add_section('SCHEDULE')
            config.set('SCHEDULE', 'daily_time', '04:00')
            config.set('SCHEDULE', 'weekly_day', 'Sunday')
            config.set('SCHEDULE', 'monthly_day', '1')

            config.add_section('NOTIFICATIONS')
            config.set('NOTIFICATIONS', 'telegram_enabled', 'false')
            config.set('NOTIFICATIONS', 'email_enabled', 'false')

            with open(self.config_file, 'w', encoding='utf-8') as f:
                config.write(f)

        return config

    def _get_usb_drive(self):
        """Застарілий метод - більше не використовується"""
        try:
            if platform.system() == 'Windows':
                # Використовуємо PowerShell для пошуку USB
                cmd = [
                    'powershell',
                    '-Command',
                    f"Get-WmiObject Win32_Volume | Where-Object {{ $_.Label -eq '{self.usb_label}' }} | Select-Object -ExpandProperty DriveLetter"
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
                if result.returncode == 0 and result.stdout.strip():
                    drive_letter = result.stdout.strip()
                    if drive_letter and len(drive_letter) == 1:
                        return f"{drive_letter}:"
            else:
                # Для Linux/Unix систем
                result = subprocess.run(['lsblk', '-o', 'LABEL,MOUNTPOINT'],
                                      capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if self.usb_label in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            return parts[1]

        except Exception as e:
            logger.error(f"Error finding USB drive: {e}")

        return None

    def _get_drive_info(self, drive_path):
        """Отримання інформації про диск або директорію"""
        try:
            if platform.system() == 'Windows':
                # Windows: перевіряємо чи це буква диска чи повний шлях
                if len(drive_path) == 1 or drive_path[1:3] == ':\\':
                    # Це буква диска (наприклад 'D:' або 'D:\')
                    drive_letter = drive_path[0] + ':'
                    cmd = [
                        'powershell',
                        '-Command',
                        f"Get-WmiObject Win32_LogicalDisk -Filter \"DeviceID='{drive_letter}'\" | Select-Object Size,FreeSpace | Format-List"
                    ]
                else:
                    # Це мережевий шлях або повний шлях до директорії
                    # Спростимо перевірку - просто перевіряємо чи існує шлях
                    cmd = [
                        'powershell',
                        '-Command',
                        f"Get-Item '{drive_path}' | Select-Object Length | Format-List"
                    ]
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
                if result.returncode == 0:
                    output = result.stdout
                    # Парсимо вивід
                    length_line = [line for line in output.split('\n') if 'Length' in line]

                    if length_line:
                        # Для директорій повертаємо приблизні значення
                        # В майбутньому можна покращити цю логіку
                        return 1000000000, 500000000  # 1GB total, 500MB free (приблизно)
            else:
                # Linux: використовуємо df
                result = subprocess.run(['df', drive_path], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    if len(lines) >= 2:
                        parts = lines[1].split()
                        if len(parts) >= 4:
                            # Розмір в блоках, переводимо в байти
                            block_size = 1024  # df використовує 1K блоки
                            size = int(parts[1]) * block_size
                            free = int(parts[3]) * block_size
                            return size, free

        except Exception as e:
            logger.error(f"Error getting drive info: {e}")

        return None, None

    def create_database_backup(self):
        """Створення бекапу бази даних з Windows підтримкою"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = self.backup_dir

            if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
                # PostgreSQL бекап
                db_config = settings.DATABASES['default']
                backup_file = backup_dir / f"kavacrm_db_{timestamp}.sql"

                # Перевіряємо наявність pg_dump
                pg_dump_path = self._find_pg_dump()
                if not pg_dump_path:
                    raise Exception("pg_dump not found. Install PostgreSQL client tools.")

                cmd = [
                    pg_dump_path,
                    '-h', db_config['HOST'],
                    '-p', str(db_config['PORT']),
                    '-U', db_config['USER'],
                    '-d', db_config['NAME'],
                    '-f', str(backup_file)
                ]

                env = os.environ.copy()
                env['PGPASSWORD'] = db_config['PASSWORD']

                result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(f"pg_dump failed: {result.stderr}")

            else:
                # SQLite бекап
                db_path = Path(settings.DATABASES['default']['NAME'])
                backup_file = backup_dir / f"kavacrm_db_{timestamp}.sqlite3"
                shutil.copy2(db_path, backup_file)

            # Стиснення бекапу
            compressed_file = self._compress_file(backup_file)
            if compressed_file:
                os.remove(backup_file)  # Видаляємо оригінал після стиснення
                backup_file = compressed_file

            logger.info(f"Database backup created: {backup_file}")
            return backup_file

        except Exception as e:
            logger.error(f"Failed to create database backup: {str(e)}")
            raise

    def _find_pg_dump(self):
        """Пошук pg_dump в системі"""
        possible_paths = [
            'pg_dump',  # В PATH
            '/usr/bin/pg_dump',
            '/usr/local/bin/pg_dump',
            'C:\\Program Files\\PostgreSQL\\bin\\pg_dump.exe',
            'C:\\Program Files (x86)\\PostgreSQL\\bin\\pg_dump.exe',
        ]

        for path in possible_paths:
            try:
                result = subprocess.run([path, '--version'], capture_output=True)
                if result.returncode == 0:
                    return path
            except (subprocess.SubprocessError, FileNotFoundError):
                continue

        return None

    def create_media_backup(self):
        """Створення бекапу медіа файлів"""
        try:
            media_dir = Path(settings.MEDIA_ROOT)

            if not media_dir.exists():
                logger.warning("Media directory does not exist")
                return None

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_dir / f"kavacrm_media_{timestamp}.zip"

            # Створюємо ZIP архів для Windows сумісності
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED,
                               compresslevel=self.compression_level) as zipf:
                for file_path in media_dir.rglob('*'):
                    if file_path.is_file():
                        # Додаємо відносний шлях
                        relative_path = file_path.relative_to(media_dir.parent)
                        zipf.write(file_path, relative_path)

            logger.info(f"Media backup created: {backup_file}")
            return backup_file

        except Exception as e:
            logger.error(f"Failed to create media backup: {str(e)}")
            raise

    def create_static_backup(self):
        """Створення бекапу статичних файлів"""
        try:
            static_dir = Path(settings.STATIC_ROOT)

            if not static_dir.exists():
                logger.warning("Static directory does not exist")
                return None

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_dir / f"kavacrm_static_{timestamp}.zip"

            # Створюємо ZIP архів
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED,
                               compresslevel=self.compression_level) as zipf:
                for file_path in static_dir.rglob('*'):
                    if file_path.is_file():
                        # Додаємо відносний шлях
                        relative_path = file_path.relative_to(static_dir.parent)
                        zipf.write(file_path, relative_path)

            logger.info(f"Static backup created: {backup_file}")
            return backup_file

        except Exception as e:
            logger.error(f"Failed to create static backup: {str(e)}")
            raise

    def _compress_file(self, file_path):
        """Стиснення файлу (GZIP для SQL, ZIP для інших)"""
        try:
            file_path = Path(file_path)
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')

            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb', compresslevel=self.compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)

            return compressed_path

        except Exception as e:
            logger.error(f"Failed to compress file {file_path}: {e}")
            return None

    def cleanup_old_backups(self):
        """Видалення старих бекапів з покращеною ротацією"""
        try:
            retention_days = self.retention_days
            cutoff_date = datetime.now() - timedelta(days=retention_days)

            deleted_count = 0
            total_size_freed = 0

            # Очищаємо локальні бекапи
            for backup_file in self.backup_dir.glob('kavacrm_*'):
                if backup_file.is_file():
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        file_size = backup_file.stat().st_size
                        backup_file.unlink()
                        deleted_count += 1
                        total_size_freed += file_size
                        logger.info(f"Deleted old local backup: {backup_file}")

            # Очищаємо бекапи в custom_backup_path
            if self.custom_backup_path:
                custom_dir = Path(self.custom_backup_path)
                if custom_dir.exists():
                    for backup_file in custom_dir.glob('kavacrm_*'):
                        if backup_file.is_file():
                            file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                            if file_time < cutoff_date:
                                file_size = backup_file.stat().st_size
                                backup_file.unlink()
                                deleted_count += 1
                                total_size_freed += file_size
                                logger.info(f"Deleted old custom backup: {backup_file}")

            # Очищаємо логи старше 90 днів
            logs_dir = self.backup_dir / "logs"
            if logs_dir.exists():
                for log_file in logs_dir.glob('*.log'):
                    if log_file.is_file():
                        file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                        if file_time < datetime.now() - timedelta(days=90):
                            log_file.unlink()
                            logger.info(f"Deleted old log: {log_file}")

            logger.info(f"Cleaned up {deleted_count} backup files, freed {total_size_freed} bytes")

            return {
                'deleted_count': deleted_count,
                'size_freed': total_size_freed
            }

        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {str(e)}")
            raise

    def copy_to_usb(self):
        """Копіювання бекапів на зовнішній диск з перевірками (USB або користувацька директорія)"""
        try:
            usb_path = None
            usb_drive = None

            # Спробуємо використати основний шлях
            if self.custom_backup_path and self.custom_backup_path.strip():
                usb_path = Path(self.custom_backup_path.strip())
                usb_drive = str(usb_path)
                logger.info(f"Using primary backup path: {usb_path}")
            # Якщо основний шлях не заданий або недоступний, спробуємо резервний
            elif self.secondary_backup_path and self.secondary_backup_path.strip():
                usb_path = Path(self.secondary_backup_path.strip())
                usb_drive = str(usb_path)
                logger.info(f"Using secondary backup path: {usb_path}")
            else:
                logger.warning("No backup path specified")
                return {
                    'success': False,
                    'error': 'Backup path not specified. Please configure backup path in settings.',
                    'drive': None
                }

            if not usb_path.exists():
                try:
                    usb_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created backup path: {usb_path}")
                except Exception as e:
                    # Тихо ігноруємо помилки створення директорії щоб уникнути спаму в логах
                    # logger.error(f"Failed to create backup path {usb_path}: {e}")
                    return {
                        'success': False,
                        'error': f'Failed to create backup path: {e}',
                        'drive': usb_drive
                    }

            # Перевіряємо місце на диску
            drive_size, drive_free = self._get_drive_info(usb_drive)
            if drive_free is not None:
                # Перевіряємо що є принаймні 1GB вільного місця
                min_free_space = 1 * 1024 * 1024 * 1024  # 1GB
                if drive_free < min_free_space:
                    logger.warning(f"Insufficient space on USB drive: {drive_free} bytes free")
                    return {
                        'success': False,
                        'error': f'Insufficient space: {drive_free} bytes free',
                        'drive': usb_drive
                    }

            # Створюємо директорію для бекапів
            usb_backup_path = usb_path / self.usb_backup_dir
            usb_backup_path.mkdir(exist_ok=True)

            # Копіюємо сьогоднішні бекапи
            today = datetime.now().date()
            copied_count = 0
            copied_size = 0

            for backup_file in self.backup_dir.glob('kavacrm_*'):
                if backup_file.is_file():
                    file_date = datetime.fromtimestamp(backup_file.stat().st_mtime).date()
                    if file_date == today:  # Копіюємо тільки сьогоднішні
                        usb_file = usb_backup_path / backup_file.name

                        # Перевіряємо чи файл вже існує
                        if usb_file.exists():
                            # Порівнюємо розміри
                            if usb_file.stat().st_size == backup_file.stat().st_size:
                                logger.info(f"File already exists on USB: {backup_file.name}")
                                continue

                        shutil.copy2(backup_file, usb_file)
                        copied_count += 1
                        copied_size += backup_file.stat().st_size
                        logger.info(f"Copied to USB: {backup_file.name}")

            logger.info(f"Copied {copied_count} backup files to USB ({copied_size} bytes)")

            return {
                'success': True,
                'drive': usb_drive,
                'copied_count': copied_count,
                'copied_size': copied_size,
                'drive_free_gb': drive_free / (1024**3) if drive_free else 0
            }

        except Exception as e:
            logger.error(f"Failed to copy backups to USB: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'drive': usb_drive if 'usb_drive' in locals() else None
            }

    def create_backup_report(self):
        """Створення детального звіту про бекапи"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = self.backup_dir / f"backup_report_{timestamp}.txt"

            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("    ЗВІТ ПРО БЕКАП KAVACRM\n")
                f.write("="*60 + "\n")
                f.write(f"Дата створення: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Користувач: {os.environ.get('USERNAME', 'Unknown')}\n")
                f.write(f"Комп'ютер: {platform.node()}\n")
                f.write("\n")

                # Локальні бекапи
                f.write("ЛОКАЛЬНІ БЕКАПИ:\n")
                local_backups = list(self.backup_dir.glob('kavacrm_*'))
                if local_backups:
                    total_size = 0
                    for backup in sorted(local_backups, key=lambda x: x.stat().st_mtime, reverse=True):
                        size = backup.stat().st_size
                        total_size += size
                        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
                        f.write(f"  {backup.name} ({size} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})\n")
                    f.write(f"  Всього: {len(local_backups)} файлів, {total_size} bytes\n")
                else:
                    f.write("  Немає локальних бекапів\n")
                f.write("\n")

                # USB бекапи
                f.write("USB БЕКАПИ:\n")
                if self.usb_backup_enabled:
                    usb_result = self.copy_to_usb()
                else:
                    usb_result = {'success': False, 'error': 'USB backup disabled'}
                if usb_result['success']:
                    usb_drive = usb_result['drive']
                    usb_path = Path(usb_drive) / self.usb_backup_dir
                    if usb_path.exists():
                        usb_backups = list(usb_path.glob('kavacrm_*'))
                        if usb_backups:
                            total_usb_size = 0
                            for backup in sorted(usb_backups, key=lambda x: x.stat().st_mtime, reverse=True):
                                size = backup.stat().st_size
                                total_usb_size += size
                                mtime = datetime.fromtimestamp(backup.stat().st_mtime)
                                f.write(f"  {backup.name} ({size} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})\n")
                            f.write(f"  Всього: {len(usb_backups)} файлів, {total_usb_size} bytes\n")
                            f.write(f"  Диск: {usb_drive}\n")
                        else:
                            f.write("  Немає бекапів на USB\n")
                    else:
                        f.write("  USB директорія не існує\n")
                else:
                    f.write(f"  Помилка: {usb_result.get('error', 'Невідома помилка')}\n")
                f.write("\n")

                # Системна інформація
                f.write("СИСТЕМНА ІНФОРМАЦІЯ:\n")
                f.write(f"  ОС: {platform.system()} {platform.release()}\n")
                f.write(f"  Архітектура: {platform.machine()}\n")

                # Розмір директорії бекапів
                try:
                    total_size = sum(f.stat().st_size for f in self.backup_dir.rglob('*') if f.is_file())
                    f.write(f"  Розмір директорії бекапів: {total_size} bytes\n")
                except:
                    f.write("  Розмір директорії: не вдалося визначити\n")

                f.write("\n")
                f.write("="*60 + "\n")

            logger.info(f"Backup report created: {report_file}")
            return report_file

        except Exception as e:
            logger.error(f"Failed to create backup report: {str(e)}")
            return None

    def create_full_backup(self):
        """Створення повного бекапу з покращеним моніторингом"""
        try:
            logger.info("Starting full backup process...")

            start_time = datetime.now()

            # Створюємо бекапи
            db_backup = self.create_database_backup()
            media_backup = self.create_media_backup()
            static_backup = self.create_static_backup()

            # Копіюємо на USB (якщо увімкнено)
            if self.usb_backup_enabled:
                usb_result = self.copy_to_usb()
            else:
                usb_result = {'success': False, 'error': 'USB backup disabled'}

            # Очищаємо старі бекапи
            cleanup_result = self.cleanup_old_backups()

            # Створюємо звіт
            report_file = self.create_backup_report()

            # Час виконання
            duration = datetime.now() - start_time

            # Результати
            backup_files = [f for f in [db_backup, media_backup, static_backup] if f]

            result = {
                'success': True,
                'files': backup_files,
                'usb_success': usb_result['success'] if usb_result else False,
                'usb_info': usb_result,
                'cleanup_info': cleanup_result,
                'report_file': report_file,
                'duration': duration.total_seconds(),
                'timestamp': datetime.now().isoformat()
            }

            logger.info(f"Full backup completed successfully. Files: {backup_files}")
            logger.info(f"USB copy success: {usb_result['success'] if usb_result else False}")
            logger.info(f"Duration: {duration.total_seconds():.2f} seconds")

            return result

        except Exception as e:
            logger.error(f"Full backup failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
