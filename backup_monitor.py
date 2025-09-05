#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Моніторинг системи бекапу KavaCRM
Перевірка статусу, сповіщення, автоматична ротація
"""

import os
import sys
import json
import smtplib
import logging
import argparse
import configparser
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

# Додаємо директорію проекту до шляху
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from backup_utils_windows import WindowsBackupManager
except ImportError:
    print("❌ Помилка імпорту WindowsBackupManager")
    sys.exit(1)

logger = logging.getLogger(__name__)

class BackupMonitor:
    """Монітор системи бекапу"""

    def __init__(self, config_file="backups/backup_config.ini"):
        self.config_file = Path(config_file)
        self.backup_manager = WindowsBackupManager(config_file)
        self.config = self.backup_manager.config

        # Налаштування логування
        self._setup_logging()

    def _setup_logging(self):
        """Налаштування логування"""
        logs_dir = self.backup_manager.backup_dir / "logs"
        logs_dir.mkdir(exist_ok=True)

        log_file = logs_dir / f"backup_monitor_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

    def check_backup_status(self):
        """Перевірка статусу бекапів"""
        logger.info("Перевірка статусу бекапів...")

        status = {
            'timestamp': datetime.now().isoformat(),
            'local_backups': {},
            'usb_backups': {},
            'issues': [],
            'recommendations': []
        }

        try:
            # Збираємо всі бекапи з різних місць
            all_backups = []

            # Перевірка локальних бекапів
            local_backups = list(self.backup_manager.backup_dir.glob('kavacrm_*'))
            all_backups.extend(local_backups)
            status['local_backups']['count'] = len(local_backups)
            status['local_backups']['total_size'] = sum(f.stat().st_size for f in local_backups)

            # Перевірка бекапів в custom_backup_path
            if self.backup_manager.custom_backup_path:
                custom_dir = Path(self.backup_manager.custom_backup_path)
                if custom_dir.exists():
                    custom_backups = list(custom_dir.glob('kavacrm_*'))
                    all_backups.extend(custom_backups)
                    status['custom_backups'] = {
                        'count': len(custom_backups),
                        'total_size': sum(f.stat().st_size for f in custom_backups)
                    }

            # Перевірка найновішого бекапу з усіх місць
            if all_backups:
                latest_backup = max(all_backups, key=lambda x: x.stat().st_mtime)
                latest_time = datetime.fromtimestamp(latest_backup.stat().st_mtime)
                status['local_backups']['latest_backup'] = {
                    'name': latest_backup.name,
                    'timestamp': latest_time.isoformat(),
                    'age_hours': (datetime.now() - latest_time).total_seconds() / 3600,
                    'location': 'custom' if self.backup_manager.custom_backup_path and str(latest_backup.parent) == self.backup_manager.custom_backup_path else 'local'
                }

                # Перевірка чи бекап свіжий (менше 24 годин)
                if status['local_backups']['latest_backup']['age_hours'] > 24:
                    status['issues'].append({
                        'type': 'stale_backup',
                        'message': f'Останній бекап старший за {status["local_backups"]["latest_backup"]["age_hours"]:.1f} годин',
                        'severity': 'warning'
                    })
            else:
                status['issues'].append({
                    'type': 'no_backups',
                    'message': 'Немає бекапів',
                    'severity': 'critical'
                })

            # Перевірка USB (тільки якщо увімкнено)
            usb_result = {'success': False, 'error': 'USB backup disabled'}
            if getattr(self.backup_manager, 'usb_backup_enabled', True):
                usb_result = self.backup_manager.copy_to_usb()
            if usb_result['success']:
                usb_drive = usb_result['drive']
                usb_path = Path(usb_drive) / self.backup_manager.usb_backup_dir

                usb_backups = list(usb_path.glob('kavacrm_*'))
                status['usb_backups']['count'] = len(usb_backups)
                status['usb_backups']['total_size'] = sum(f.stat().st_size for f in usb_backups)
                status['usb_backups']['drive'] = usb_drive

                if usb_backups:
                    latest_usb = max(usb_backups, key=lambda x: x.stat().st_mtime)
                    latest_usb_time = datetime.fromtimestamp(latest_usb.stat().st_mtime)
                    status['usb_backups']['latest_backup'] = {
                        'name': latest_usb.name,
                        'timestamp': latest_usb_time.isoformat(),
                        'age_hours': (datetime.now() - latest_usb_time).total_seconds() / 3600
                    }
                else:
                    status['issues'].append({
                        'type': 'no_usb_backups',
                        'message': 'Немає бекапів на USB диску',
                        'severity': 'warning'
                    })
            else:
                status['issues'].append({
                    'type': 'usb_error',
                    'message': f'Помилка доступу до USB: {usb_result.get("error", "Невідома помилка")}',
                    'severity': 'error'
                })

            # Перевірка місця на диску
            disk_usage = self._check_disk_space()
            status['disk_usage'] = disk_usage

            if disk_usage['backup_dir']['free_percent'] < 10:
                status['issues'].append({
                    'type': 'low_disk_space',
                    'message': f'Мало місця в директорії бекапів: {disk_usage["backup_dir"]["free_percent"]:.1f}%',
                    'severity': 'warning'
                })

            # Генерація рекомендацій
            status['recommendations'] = self._generate_recommendations(status)

        except Exception as e:
            logger.error(f"Помилка перевірки статусу: {e}")
            status['issues'].append({
                'type': 'check_error',
                'message': f'Помилка перевірки статусу: {str(e)}',
                'severity': 'error'
            })

        return status

    def _check_disk_space(self):
        """Перевірка місця на диску"""
        try:
            import shutil

            backup_dir = self.backup_manager.backup_dir

            # Місце в директорії бекапів
            usage = shutil.disk_usage(backup_dir)
            backup_disk = {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'free_percent': (usage.free / usage.total) * 100
            }

            # Місце на системному диску
            system_usage = shutil.disk_usage(Path.home().anchor)
            system_disk = {
                'total': system_usage.total,
                'used': system_usage.used,
                'free': system_usage.free,
                'free_percent': (system_usage.free / system_usage.total) * 100
            }

            return {
                'backup_dir': backup_disk,
                'system_disk': system_disk
            }

        except Exception as e:
            logger.error(f"Помилка перевірки місця на диску: {e}")
            return {}

    def _generate_recommendations(self, status):
        """Генерація рекомендацій на основі статусу"""
        recommendations = []

        # Рекомендації по кількості бекапів
        if status['local_backups']['count'] < 7:
            recommendations.append("Рекомендується мати принаймні 7 днів бекапів")

        # Рекомендації по USB
        if not status.get('usb_backups', {}).get('count', 0):
            recommendations.append("Налаштуйте бекап на USB диск для додаткової безпеки")

        # Рекомендації по місцю
        disk_usage = status.get('disk_usage', {})
        if disk_usage.get('backup_dir', {}).get('free_percent', 100) < 20:
            recommendations.append("Звільніть місце в директорії бекапів або збільште період ротації")

        # Рекомендації по свіжості
        latest_backup = status.get('local_backups', {}).get('latest_backup', {})
        if latest_backup.get('age_hours', 0) > 48:
            recommendations.append("Останній бекап занадто старий, перевірте планувальник завдань")

        return recommendations

    def send_notifications(self, status):
        """Надсилання сповіщень"""
        logger.info("Надсилання сповіщень...")

        # Telegram повідомлення
        if self.config.getboolean('NOTIFICATIONS', 'telegram_enabled', fallback=False):
            self._send_telegram_notification(status)

        # Email повідомлення
        if self.config.getboolean('NOTIFICATIONS', 'email_enabled', fallback=False):
            self._send_email_notification(status)

    def _send_telegram_notification(self, status):
        """Надсилання повідомлення в Telegram"""
        try:
            bot_token = self.config.get('NOTIFICATIONS', 'telegram_bot_token', fallback='')
            chat_id = self.config.get('NOTIFICATIONS', 'telegram_chat_id', fallback='')

            if not bot_token or not chat_id:
                logger.warning("Telegram не налаштований (відсутній токен або chat_id)")
                return

            message = self._format_telegram_message(status)

            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }

            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                logger.info("Telegram повідомлення надіслано успішно")
            else:
                logger.error(f"Помилка надсилання Telegram: {response.text}")

        except Exception as e:
            logger.error(f"Помилка надсилання Telegram повідомлення: {e}")

    def _send_email_notification(self, status):
        """Надсилання email повідомлення"""
        try:
            recipient = self.config.get('NOTIFICATIONS', 'email_recipient', fallback='')

            if not recipient:
                logger.warning("Email не налаштований (відсутній одержувач)")
                return

            # Використовуємо Django email налаштування
            from django.core.mail import send_mail
            from django.conf import settings

            subject = f"KavaCRM Backup Status - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            # Створюємо HTML повідомлення
            html_message = self._format_html_email(status)
            plain_message = self._format_plain_email(status)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                html_message=html_message
            )

            logger.info("Email повідомлення надіслано успішно")

        except Exception as e:
            logger.error(f"Помилка надсилання email: {e}")

    def _format_telegram_message(self, status):
        """Форматування повідомлення для Telegram"""
        message = "🔄 <b>KavaCRM Backup Status</b>\n"
        message += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

        # Локальні бекапи
        local = status['local_backups']
        message += f"💾 <b>Локальні бекапи:</b> {local['count']} файлів\n"
        if 'latest_backup' in local:
            age = local['latest_backup']['age_hours']
            message += f"🕐 Останній: {age:.1f} годин тому\n"

        # USB бекапи
        usb = status.get('usb_backups', {})
        if usb:
            message += f"\n💿 <b>USB бекапи:</b> {usb['count']} файлів\n"
            if 'drive' in usb:
                message += f"📀 Диск: {usb['drive']}\n"

        # Проблеми
        if status['issues']:
            message += "\n⚠️ <b>Проблеми:</b>\n"
            for issue in status['issues']:
                emoji = "🔴" if issue['severity'] == 'critical' else "🟡" if issue['severity'] == 'warning' else "🔵"
                message += f"{emoji} {issue['message']}\n"

        # Рекомендації
        if status['recommendations']:
            message += "\n💡 <b>Рекомендації:</b>\n"
            for rec in status['recommendations']:
                message += f"• {rec}\n"

        return message

    def _format_html_email(self, status):
        """Форматування HTML email"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background: #007bff; color: white; padding: 10px; }}
                .section {{ margin: 20px 0; }}
                .issue-critical {{ color: #dc3545; }}
                .issue-warning {{ color: #ffc107; }}
                .issue-info {{ color: #17a2b8; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>KavaCRM Backup Status Report</h2>
                <p>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>

            <div class="section">
                <h3>Локальні бекапи</h3>
                <p>Кількість: {status['local_backups']['count']}</p>
                <p>Розмір: {status['local_backups'].get('total_size', 0)} bytes</p>
        """

        if 'latest_backup' in status['local_backups']:
            html += f"<p>Останній бекап: {status['local_backups']['latest_backup']['age_hours']:.1f} годин тому</p>"

        html += "</div>"

        if status.get('usb_backups'):
            html += f"""
            <div class="section">
                <h3>USB бекапи</h3>
                <p>Кількість: {status['usb_backups']['count']}</p>
                <p>Диск: {status['usb_backups'].get('drive', 'N/A')}</p>
            </div>
            """

        if status['issues']:
            html += '<div class="section"><h3>Проблеми</h3><ul>'
            for issue in status['issues']:
                css_class = f"issue-{issue['severity']}"
                html += f'<li class="{css_class}">[{issue["severity"].upper()}] {issue["message"]}</li>'
            html += '</ul></div>'

        if status['recommendations']:
            html += '<div class="section"><h3>Рекомендації</h3><ul>'
            for rec in status['recommendations']:
                html += f'<li>{rec}</li>'
            html += '</ul></div>'

        html += "</body></html>"
        return html

    def _format_plain_email(self, status):
        """Форматування звичайного text email"""
        message = f"KavaCRM Backup Status Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

        message += f"Локальні бекапи: {status['local_backups']['count']} файлів\n"

        if status.get('usb_backups'):
            message += f"USB бекапи: {status['usb_backups']['count']} файлів\n"

        if status['issues']:
            message += "\nПроблеми:\n"
            for issue in status['issues']:
                message += f"[{issue['severity'].upper()}] {issue['message']}\n"

        return message

    def generate_daily_report(self):
        """Генерація денного звіту"""
        logger.info("Генерація денного звіту...")

        status = self.check_backup_status()

        # Створюємо детальний звіт
        report_file = self.backup_manager.backup_dir / f"daily_report_{datetime.now().strftime('%Y%m%d')}.txt"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("                    ДЕННИЙ ЗВІТ ПРО СИСТЕМУ БЕКАПУ KAVACRM\n")
            f.write("="*80 + "\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Користувач: {os.environ.get('USERNAME', 'Unknown')}\n")
            f.write(f"Комп'ютер: {os.environ.get('COMPUTERNAME', 'Unknown')}\n\n")

            # Детальна інформація про бекапи
            f.write("ЛОКАЛЬНІ БЕКАПИ:\n")
            f.write("-" * 40 + "\n")

            local_backups = list(self.backup_manager.backup_dir.glob('kavacrm_*'))
            if local_backups:
                # Групуємо по датам
                backups_by_date = {}
                for backup in local_backups:
                    date = datetime.fromtimestamp(backup.stat().st_mtime).date()
                    if date not in backups_by_date:
                        backups_by_date[date] = []
                    backups_by_date[date].append(backup)

                for date in sorted(backups_by_date.keys(), reverse=True):
                    f.write(f"\n{date.strftime('%Y-%m-%d')}:\n")
                    day_backups = backups_by_date[date]
                    total_size = sum(b.stat().st_size for b in day_backups)

                    for backup in sorted(day_backups, key=lambda x: x.stat().st_mtime):
                        time_str = datetime.fromtimestamp(backup.stat().st_mtime).strftime('%H:%M')
                        size_mb = backup.stat().st_size / (1024 * 1024)
                        f.write(f"  {time_str} - {backup.name} ({size_mb:.2f} MB)\n")

                    f.write(f"  Всього за день: {len(day_backups)} файлів, {total_size / (1024*1024):.2f} MB\n")
            else:
                f.write("Немає локальних бекапів\n")

            # USB інформація
            f.write("\n\nUSB БЕКАПИ:\n")
            f.write("-" * 40 + "\n")

            if getattr(self.backup_manager, 'usb_backup_enabled', True):
                usb_result = self.backup_manager.copy_to_usb()
            else:
                usb_result = {'success': False, 'error': 'USB backup disabled'}
            if usb_result['success']:
                usb_drive = usb_result['drive']
                usb_path = Path(usb_drive) / self.backup_manager.usb_backup_dir

                f.write(f"USB диск: {usb_drive}\n")
                f.write(f"Директорія: {self.backup_manager.usb_backup_dir}\n")

                if usb_path.exists():
                    usb_backups = list(usb_path.glob('kavacrm_*'))
                    if usb_backups:
                        total_usb_size = sum(f.stat().st_size for f in usb_backups)
                        f.write(f"Кількість бекапів: {len(usb_backups)}\n")
                        f.write(f"Загальний розмір: {total_usb_size / (1024*1024):.2f} MB\n")

                        # Останні 5 бекапів
                        f.write("\nОстанні бекапи на USB:\n")
                        for backup in sorted(usb_backups, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                            time_str = datetime.fromtimestamp(backup.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                            size_mb = backup.stat().st_size / (1024 * 1024)
                            f.write(f"  {time_str} - {backup.name} ({size_mb:.2f} MB)\n")
                    else:
                        f.write("Немає бекапів на USB диску\n")
                else:
                    f.write("USB директорія не існує\n")
            else:
                f.write(f"Помилка доступу до USB: {usb_result.get('error', 'Невідома помилка')}\n")

            # Статистика використання місця
            f.write("\n\nСТАТИСТИКА ВИКОРИСТАННЯ МІСЦЯ:\n")
            f.write("-" * 40 + "\n")

            disk_usage = self._check_disk_space()
            if disk_usage:
                for disk_name, usage in disk_usage.items():
                    f.write(f"{disk_name.upper()}:\n")
                    f.write(f"  Загалом: {usage['total'] / (1024**3):.2f} GB\n")
                    f.write(f"  Використано: {usage['used'] / (1024**3):.2f} GB\n")
                    f.write(f"  Вільно: {usage['free'] / (1024**3):.2f} GB ({usage['free_percent']:.1f}%)\n")
                    f.write("\n")

            # Проблеми та рекомендації
            if status['issues']:
                f.write("ПОПЕРЕДЖЕННЯ ТА ПРОБЛЕМИ:\n")
                f.write("-" * 40 + "\n")
                for issue in status['issues']:
                    severity_icon = "🔴" if issue['severity'] == 'critical' else "🟡" if issue['severity'] == 'warning' else "🔵"
                    f.write(f"{severity_icon} [{issue['severity'].upper()}] {issue['message']}\n")
                f.write("\n")

            if status['recommendations']:
                f.write("РЕКОМЕНДАЦІЇ:\n")
                f.write("-" * 40 + "\n")
                for rec in status['recommendations']:
                    f.write(f"• {rec}\n")
                f.write("\n")

            f.write("="*80 + "\n")
            f.write("Кінець звіту\n")

        logger.info(f"Денний звіт створено: {report_file}")

        # Надсилаємо сповіщення
        self.send_notifications(status)

        return report_file

def main():
    """Основна функція"""
    parser = argparse.ArgumentParser(description='Моніторинг системи бекапу KavaCRM')
    parser.add_argument('action', choices=['status', 'report', 'check', 'notify'],
                       help='Дія для виконання')
    parser.add_argument('--config', default='backups/backup_config.ini',
                       help='Шлях до конфігураційного файлу')
    parser.add_argument('--verbose', action='store_true',
                       help='Детальний вивід')

    args = parser.parse_args()

    # Налаштування Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kavapro.settings')
    import django
    django.setup()

    # Створюємо монітор
    monitor = BackupMonitor(args.config)

    if args.action == 'status':
        status = monitor.check_backup_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif args.action == 'report':
        report_file = monitor.generate_daily_report()
        print(f"Звіт створено: {report_file}")

    elif args.action == 'check':
        status = monitor.check_backup_status()

        print("\n" + "="*60)
        print(" СТАТУС СИСТЕМИ БЕКАПУ KAVACRM")
        print("="*60)

        # Локальні бекапи
        local = status['local_backups']
        print("\n💾 ЛОКАЛЬНІ БЕКАПИ:")
        print(f"   Кількість: {local['count']}")
        print(f"   Розмір: {local.get('total_size', 0) / (1024*1024):.2f} MB")

        if 'latest_backup' in local:
            print(f"   Останній: {local['latest_backup']['age_hours']:.1f} годин тому")

        # USB бекапи
        usb = status.get('usb_backups', {})
        if usb:
            print("\n💿 USB БЕКАПИ:")
            print(f"   Кількість: {usb['count']}")
            print(f"   Розмір: {usb.get('total_size', 0) / (1024*1024):.2f} MB")
            print(f"   Диск: {usb.get('drive', 'N/A')}")
            if 'latest_backup' in usb:
                print(f"   Останній: {usb['latest_backup']['age_hours']:.1f} годин тому")

        # Проблеми
        if status['issues']:
            print("\n⚠️ ПРОБЛЕМИ:")
            for issue in status['issues']:
                icon = "🔴" if issue['severity'] == 'critical' else "🟡" if issue['severity'] == 'warning' else "🔵"
                print(f"   {icon} {issue['message']}")

        # Рекомендації
        if status['recommendations']:
            print("\n💡 РЕКОМЕНДАЦІЇ:")
            for rec in status['recommendations']:
                print(f"   • {rec}")

        print("\n" + "="*60)

    elif args.action == 'notify':
        status = monitor.check_backup_status()
        monitor.send_notifications(status)
        print("Сповіщення надіслано")

if __name__ == '__main__':
    main()
