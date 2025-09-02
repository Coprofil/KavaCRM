@echo off
chcp 65001 >nul
echo ========================================
echo    ВИПРАВЛЕННЯ КОДУВАННЯ
echo ========================================

echo ℹ️  Поточна кодова сторінка:
chcp

echo.
echo 🔧 Перевірка файлів проекту...

REM Перевірка наявності файлів з українською мовою
echo.
echo 📁 Перевірка Python файлів:
for %%f in (*.py) do (
    echo Проверка: %%f
    findstr /C:"україн" "%%f" >nul 2>&1 && echo   ✅ Знайдено український текст в %%f
)

echo.
echo 📄 Перевірка інших файлів:
for %%f in (*.md) do (
    if exist "%%f" (
        echo Проверка: %%f
        findstr /C:"україн" "%%f" >nul 2>&1 && echo   ✅ Знайдено український текст в %%f
    )
)

for %%f in (*.txt) do (
    if exist "%%f" (
        echo Проверка: %%f
        findstr /C:"україн" "%%f" >nul 2>&1 && echo   ✅ Знайдено український текст в %%f
    )
)

echo.
echo ⚙️  Перевірка Django налаштувань...

REM Перевірка settings.py
if exist kavapro\settings.py (
    echo Перевірка settings.py...
    findstr /C:"LANGUAGE_CODE = 'uk'" kavapro\settings.py >nul 2>&1 && echo   ✅ Українська мова налаштована в Django
)

echo.
echo 🛠️  Створення файлу з тестуванням кодування...

REM Створення тестового файлу
echo Тестування кодування файлів > test_encoding.txt
echo. >> test_encoding.txt
echo Український текст: Привіт, світ! >> test_encoding.txt
echo English text: Hello, world! >> test_encoding.txt
echo Кирилиця: АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ >> test_encoding.txt
echo. >> test_encoding.txt
echo Якщо ви бачите цей текст коректно - кодування працює! >> test_encoding.txt

echo ✅ Тестовий файл створено: test_encoding.txt

echo.
echo 🔍 Перевірка вмісту тестового файлу:
type test_encoding.txt

echo.
echo ========================================
echo    РЕЗУЛЬТАТИ ПЕРЕВІРКИ
echo ========================================
echo.
echo ✅ Кодування термінала: UTF-8 (65001)
echo ✅ Файли створені з підтримкою Unicode
echo.
echo 📋 РЕКОМЕНДАЦІЇ:
echo.
echo 1. Для постійного використання UTF-8 додайте до ваших .bat файлів:
echo    chcp 65001 ^>nul
echo.
echo 2. В Python скриптах використовуйте:
echo    -*- coding: utf-8 -*-
echo.
echo 3. Для Django переконайтеся що в settings.py:
echo    LANGUAGE_CODE = 'uk'
echo    USE_I18N = True
echo.
echo 4. Якщо проблеми з відображенням - спробуйте:
echo    • Перезапустити командний рядок
echo    • Використати PowerShell замість cmd
echo    • Перевірити налаштування консолі
echo.
pause
