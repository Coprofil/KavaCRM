@echo off
echo ========================================
echo      СТВОРЕННЯ БЕКАПУ KAVACRM
echo ========================================

REM Створюємо директорію для бекапів
if not exist backups mkdir backups

echo ℹ️  Підготовка до бекапу...

REM Зупиняємо Django сервер (якщо запущений)
taskkill /f /im python.exe /fi "WINDOWTITLE eq Django*" >nul 2>&1

echo ℹ️  Створення бекапу бази даних...

REM Копіюємо базу даних
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

if exist db.sqlite3 (
    copy db.sqlite3 "backups\kavacrm_backup_%TIMESTAMP%.sqlite3"
    echo ✅ База даних скопійована
) else (
    echo ⚠️  База даних не знайдена: db.sqlite3
)

echo ℹ️  Створення бекапу медіа файлів...

REM Архівуємо медіа файли
if exist media (
    powershell "Compress-Archive -Path 'media' -DestinationPath 'backups\kavacrm_media_%TIMESTAMP%.zip' -Force"
    echo ✅ Медіа файли заархівовані
) else (
    echo ⚠️  Директорія media не існує
)

echo ℹ️  Створення бекапу статичних файлів...

REM Архівуємо статичні файли
if exist staticfiles (
    powershell "Compress-Archive -Path 'staticfiles' -DestinationPath 'backups\kavacrm_static_%TIMESTAMP%.zip' -Force"
    echo ✅ Статичні файли заархівовані
) else (
    echo ⚠️  Директорія staticfiles не існує
)

echo ℹ️  Створення бекапу коду проекту...

REM Архівуємо код (крім великих директорій)
powershell "Get-ChildItem -Exclude 'backups','staticfiles','media','__pycache__','*.pyc','*.log','logs','venv','.venv','node_modules' | Compress-Archive -DestinationPath 'backups\kavacrm_code_%TIMESTAMP%.zip' -Force"
echo ✅ Код проекту заархівований

echo ℹ️  Створення бекапу конфігураційних файлів...

REM Копіюємо важливі конфігураційні файли
copy kavapro\settings.py "backups\kavacrm_settings_%TIMESTAMP%.py" >nul 2>&1
copy requirements_production.txt "backups\kavacrm_requirements_%TIMESTAMP%.txt" >nul 2>&1
echo ✅ Конфігураційні файли скопійовані

echo ℹ️  Перевірка USB дисків...

REM Шукаємо USB диски
for %%d in (D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist %%d:\ (
        echo ℹ️  Знайдено диск %%d:
        if not exist %%d:\KavaCRM_Backups mkdir %%d:\KavaCRM_Backups

        echo ℹ️  Копіювання на USB диск %%d:...
        xcopy "backups\*" %%d:\KavaCRM_Backups\ /Y /I >nul 2>&1

        if %errorlevel% equ 0 (
            echo ✅ Бекапи скопійовані на USB диск %%d:\KavaCRM_Backups
            goto usb_done
        ) else (
            echo ⚠️  Помилка копіювання на USB диск %%d:
        )
    )
)

:usb_done
echo ℹ️  Пошук USB дисків завершено

echo ℹ️  Створення звіту про бекап...

REM Створюємо звіт
echo ======================================== > "backups\backup_report_%TIMESTAMP%.txt"
echo      ЗВІТ ПРО БЕКАП KAVACRM         >> "backups\backup_report_%TIMESTAMP%.txt"
echo ======================================== >> "backups\backup_report_%TIMESTAMP%.txt"
echo. >> "backups\backup_report_%TIMESTAMP%.txt"
echo Дата та час: %date% %time% >> "backups\backup_report_%TIMESTAMP%.txt"
echo Директорія бекапів: %cd%\backups >> "backups\backup_report_%TIMESTAMP%.txt"
echo. >> "backups\backup_report_%TIMESTAMP%.txt"
echo СТВОРЕНІ ФАЙЛИ: >> "backups\backup_report_%TIMESTAMP%.txt"
dir /b backups\kavacrm_*%TIMESTAMP%* >> "backups\backup_report_%TIMESTAMP%.txt" 2>nul
echo. >> "backups\backup_report_%TIMESTAMP%.txt"
echo ЗАГАЛЬНИЙ РОЗМІР: >> "backups\backup_report_%TIMESTAMP%.txt"
powershell "Get-ChildItem 'backups\kavacrm_*%TIMESTAMP%*' | Measure-Object -Property Length -Sum | Select-Object -ExpandProperty Sum | ForEach-Object { '{0:N2} MB' -f ($_ / 1MB) }" >> "backups\backup_report_%TIMESTAMP%.txt"

echo ✅ Звіт створено: backups\backup_report_%TIMESTAMP%.txt

echo.
echo ========================================
echo         БЕКАП ЗАВЕРШЕНО!
echo ========================================
echo.
echo 📁 Директорія бекапів: %cd%\backups
echo 📊 Створені файли:
dir /b backups\kavacrm_*%TIMESTAMP%* 2>nul
echo.
echo 📄 Звіт: backups\backup_report_%TIMESTAMP%.txt
echo.
echo 🎉 РЕКОМЕНДАЦІЇ:
echo • Зберігайте бекапи в безпечному місці
echo • Регулярно перевіряйте цілісність бекапів
echo • Налаштуйте автоматичні бекапи для щоденного створення
echo.
pause
