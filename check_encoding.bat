@echo off
chcp 65001 >nul
echo ========================================
echo    ПЕРЕВІРКА КОДУВАННЯ ПРОЕКТУ
echo ========================================

echo ℹ️  Кодування термінала встановлено на UTF-8
echo.

echo 🔍 Перевірка файлів з українським текстом...
echo.

REM Перевірка основних файлів
set files_to_check=README.md kavapro\settings.py kavacrm\models.py kavacrm\views.py

for %%f in (%files_to_check%) do (
    if exist "%%f" (
        echo Перевірка: %%f
        findstr /C:"україн" "%%f" >nul 2>&1 && (
            echo   ✅ Знайдено український текст
            REM Показуємо перші кілька рядків з українським текстом
            for /f "tokens=*" %%l in ('findstr /N /C:"україн" "%%f" ^| findstr /C:":україн"') do (
                echo     Рядок %%l
            )
        ) || echo   ⚠️  Український текст не знайдено
        echo.
    ) else (
        echo ⚠️  Файл %%f не існує
        echo.
    )
)

echo 📊 Створення тестового файлу з українським текстом...

REM Створюємо тестовий файл
echo Тестування кодування файлів > ukrainian_test.txt
echo. >> ukrainian_test.txt
echo Український алфавіт: АБВГДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ >> ukrainian_test.txt
echo Український текст: Привіт, це тестовий файл! >> ukrainian_test.txt
echo База даних: клієнти, маршрути, відвантаження >> ukrainian_test.txt
echo Команди: створити, редагувати, видалити, зберегти >> ukrainian_test.txt
echo. >> ukrainian_test.txt
echo Якщо ви бачите цей текст правильно - кодування працює! >> ukrainian_test.txt

echo ✅ Тестовий файл створено: ukrainian_test.txt
echo.

echo 📖 Вміст тестового файлу:
type ukrainian_test.txt
echo.

echo 🔧 Перевірка Django налаштувань...

REM Перевірка settings.py
if exist kavapro\settings.py (
    echo Перевірка LANGUAGE_CODE в settings.py...
    findstr /C:"LANGUAGE_CODE = 'uk'" kavapro\settings.py >nul 2>&1 && (
        echo   ✅ Українська мова налаштована в Django
    ) || (
        echo   ⚠️  Українська мова НЕ налаштована в Django
        echo   Додайте: LANGUAGE_CODE = 'uk'
    )
) else (
    echo ⚠️  Файл settings.py не знайдено
)

echo.
echo 🎯 РЕЗУЛЬТАТИ ДІАГНОСТИКИ:
echo ===============================
echo.

REM Підрахунок файлів з українським текстом
set /a ukr_files=0
for %%f in (*.py) do (
    findstr /C:"україн" "%%f" >nul 2>&1 && set /a ukr_files+=1
)
for %%f in (*.md) do (
    findstr /C:"україн" "%%f" >nul 2>&1 && set /a ukr_files+=1
)
for %%f in (*.txt) do (
    findstr /C:"україн" "%%f" >nul 2>&1 && set /a ukr_files+=1
)

echo 📊 Файлів з українським текстом: !ukr_files!
echo ✅ Кодування термінала: UTF-8
echo ✅ Створено тестовий файл: ukrainian_test.txt

echo.
echo 💡 РЕКОМЕНДАЦІЇ:
echo ================
echo.
echo 1. Якщо ви бачите ієрогліфи замість українського тексту:
echo    • Перезапустіть командний рядок
echo    • Використовуйте PowerShell замість cmd.exe
echo    • Перевірте налаштування шрифту консолі
echo.
echo 2. Для Python файлів додайте на початок:
echo    # -*- coding: utf-8 -*-
echo.
echo 3. Зберігайте файли в UTF-8 в вашому редакторі
echo.
echo 4. В Django settings.py має бути:
echo    LANGUAGE_CODE = 'uk'
echo    USE_I18N = True
echo.
echo 5. Для постійного UTF-8 в bat файлах:
echo    chcp 65001 ^>nul
echo.

pause
