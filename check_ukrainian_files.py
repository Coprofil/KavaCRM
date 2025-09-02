#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Перевірка українських символів у файлах проекту
"""

import os
import codecs
from pathlib import Path

def check_file_encoding(file_path):
    """Перевірка кодування файлу"""
    try:
        # Спробуємо прочитати файл з різними кодуваннями
        encodings_to_try = ['utf-8', 'cp1251', 'cp866', 'iso-8859-1']

        for encoding in encodings_to_try:
            try:
                with codecs.open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    # Перевіряємо наявність українських символів
                    ukrainian_chars = ['і', 'ї', 'є', 'ґ', 'а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ь', 'ю', 'я']
                    has_ukrainian = any(char in content.lower() for char in ukrainian_chars)
                    return encoding, has_ukrainian, len(content)
            except UnicodeDecodeError:
                continue

        return None, False, 0
    except Exception as e:
        return f"Error: {e}", False, 0

def scan_project_files():
    """Сканування файлів проекту"""
    project_root = Path(".")
    files_to_check = [
        '*.py', '*.html', '*.txt', '*.md', '*.bat', '*.sh',
        'kavapro/*.py', 'kavacrm/*.py',
        'kavacrm/templates/**/*.html'
    ]

    print("🔍 ПЕРЕВІРКА УКРАЇНСЬКИХ СИМВОЛІВ У ФАЙЛАХ ПРОЕКТУ")
    print("=" * 60)

    files_with_ukrainian = []
    files_with_encoding_issues = []

    for pattern in files_to_check:
        if '**' in pattern:
            # Для рекурсивного пошуку
            base_path = Path(pattern.split('/')[0])
            if base_path.exists():
                for file_path in base_path.rglob(pattern.split('/')[-1]):
                    if file_path.is_file():
                        encoding, has_ukrainian, size = check_file_encoding(file_path)
                        if encoding:
                            if has_ukrainian:
                                files_with_ukrainian.append((file_path, encoding, size))
                            if encoding != 'utf-8':
                                files_with_encoding_issues.append((file_path, encoding))
                        else:
                            files_with_encoding_issues.append((file_path, "Не визначено"))
        else:
            # Для звичайного пошуку
            for file_path in project_root.glob(pattern):
                if file_path.is_file():
                    encoding, has_ukrainian, size = check_file_encoding(file_path)
                    if encoding:
                        if has_ukrainian:
                            files_with_ukrainian.append((file_path, encoding, size))
                        if encoding != 'utf-8':
                            files_with_encoding_issues.append((file_path, encoding))
                    else:
                        files_with_encoding_issues.append((file_path, "Не визначено"))

    print(f"\n📊 РЕЗУЛЬТАТИ СКАНУВАННЯ:")
    print(f"Файлів з українським текстом: {len(files_with_ukrainian)}")
    print(f"Файлів з проблемами кодування: {len(files_with_encoding_issues)}")

    if files_with_ukrainian:
        print(f"\n✅ ФАЙЛИ З УКРАЇНСЬКИМ ТЕКСТОМ ({len(files_with_ukrainian)}):")
        for file_path, encoding, size in files_with_ukrainian:
            print("15")

    if files_with_encoding_issues:
        print(f"\n⚠️  ФАЙЛИ З ПРОБЛЕМАМИ КОДУВАННЯ ({len(files_with_encoding_issues)}):")
        for file_path, encoding in files_with_encoding_issues:
            print(f"  • {file_path} - {encoding}")

        print("
🔧 РЕКОМЕНДАЦІЇ ПО ВИПРАВЛЕННЮ:"        print("  1. Перетворіть файли в UTF-8")
        print("  2. Додайте # -*- coding: utf-8 -*- в Python файли")
        print("  3. Використовуйте UTF-8 в редакторах")

    print(f"\n🎯 ВИСНОВОК:")
    if not files_with_encoding_issues and files_with_ukrainian:
        print("✅ Кодування файлів коректне! Українська мова підтримується.")
    elif files_with_encoding_issues:
        print("⚠️  Є проблеми з кодуванням. Потрібно виправити.")
    else:
        print("ℹ️  Не знайдено файлів з українським текстом.")

    return len(files_with_encoding_issues) == 0

def convert_to_utf8(file_path, source_encoding):
    """Конвертація файлу в UTF-8"""
    try:
        # Читаємо файл з поточним кодуванням
        with codecs.open(file_path, 'r', source_encoding) as f:
            content = f.read()

        # Записуємо в UTF-8
        with codecs.open(file_path, 'w', 'utf-8') as f:
            f.write(content)

        print(f"✅ Перетворено: {file_path} ({source_encoding} → UTF-8)")
        return True
    except Exception as e:
        print(f"❌ Помилка конвертації {file_path}: {e}")
        return False

def fix_encoding_issues():
    """Виправлення проблем з кодуванням"""
    print("
🔧 ВИПРАВЛЕННЯ ПРОБЛЕМ КОДУВАННЯ..."    print("=" * 60)

    project_root = Path(".")
    files_to_check = [
        '*.py', '*.html', '*.txt', '*.md', '*.bat', '*.sh',
        'kavapro/*.py', 'kavacrm/*.py'
    ]

    fixed_count = 0

    for pattern in files_to_check:
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                encoding, _, _ = check_file_encoding(file_path)
                if encoding and encoding != 'utf-8':
                    if convert_to_utf8(file_path, encoding):
                        fixed_count += 1

    print(f"\n✅ Виправлено файлів: {fixed_count}")

    # Додавання coding declarations до Python файлів
    python_files_fixed = 0
    for pattern in ['*.py', 'kavapro/*.py', 'kavacrm/*.py']:
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                try:
                    with codecs.open(file_path, 'r', 'utf-8') as f:
                        content = f.read()

                    # Перевіряємо, чи є вже coding declaration
                    if '# -*- coding:' not in content and content.strip():
                        # Додаємо coding declaration після shebang або на початок
                        lines = content.split('\n')
                        if lines and lines[0].startswith('#!'):
                            lines.insert(1, '# -*- coding: utf-8 -*-')
                        else:
                            lines.insert(0, '# -*- coding: utf-8 -*-')

                        new_content = '\n'.join(lines)

                        with codecs.open(file_path, 'w', 'utf-8') as f:
                            f.write(new_content)

                        python_files_fixed += 1
                        print(f"✅ Додано coding declaration: {file_path}")

                except Exception as e:
                    print(f"⚠️  Не вдалося обробити {file_path}: {e}")

    print(f"\n✅ Додано coding declarations: {python_files_fixed}")

if __name__ == '__main__':
    # Встановлюємо UTF-8 для консолі
    try:
        import sys
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

    print("Українська мова тест: Привіт, світ!")
    print("Кирилиця тест: АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
    print()

    # Скануємо файли
    if scan_project_files():
        print("
🎉 КОДУВАННЯ КОРЕКТНЕ!"    else:
        print("
🔧 ВИПРАВЛЯЄМО ПРОБЛЕМИ..."        fix_encoding_issues()

        print("
🔄 ПЕРЕПЕРЕВІРКА..."        scan_project_files()

    print("
💡 ПОРАДИ:"    print("• Зберігайте файли в UTF-8")
    print("• Використовуйте редактори з підтримкою Unicode")
    print("• В Python файлах додавайте # -*- coding: utf-8 -*-")
    print("• В терміналі використовуйте chcp 65001")
