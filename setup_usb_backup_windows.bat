@echo off
chcp 65001 >nul
echo ========================================
echo    НАЛАШТУВАННЯ USB БЕКАПУ WINDOWS
echo ========================================
echo.

REM Перевірка прав адміністратора
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Запущено з правами адміністратора
) else (
    echo ❌ Потрібні права адміністратора!
    echo Запустіть цей файл як адміністратор
    pause
    exit /b 1
)

echo.
echo Крок 1: Перевірка Python середовища...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не знайдено!
    echo Встановіть Python з https://python.org
    pause
    exit /b 1
)
echo ✅ Python знайдено

echo.
echo Крок 2: Перевірка Django...
python -c "import django; print('Django version:', django.VERSION)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Django не знайдено!
    echo Встановіть залежності: pip install -r requirements_production.txt
    pause
    exit /b 1
)
echo ✅ Django знайдено

echo.
echo Крок 3: Створення директорії для бекапів...
if not exist "backups" mkdir backups
if not exist "backups\logs" mkdir backups\logs
if not exist "backups\temp" mkdir backups\temp
echo ✅ Директорії створені

echo.
echo Крок 4: Створення конфігурації бекапу...
echo # Конфігурація USB бекапу для KavaCRM > backups\backup_config.ini
echo [BACKUP] >> backups\backup_config.ini
echo backup_dir=backups >> backups\backup_config.ini
echo usb_drive_label=KAVA_BACKUP >> backups\backup_config.ini
echo usb_backup_dir=kavacrm_backups >> backups\backup_config.ini
echo retention_days=30 >> backups\backup_config.ini
echo max_usb_space_mb=5000 >> backups\backup_config.ini
echo compression_level=6 >> backups\backup_config.ini
echo. >> backups\backup_config.ini
echo [SCHEDULE] >> backups\backup_config.ini
echo daily_time=04:00 >> backups\backup_config.ini
echo weekly_day=Sunday >> backups\backup_config.ini
echo monthly_day=1 >> backups\backup_config.ini
echo. >> backups\backup_config.ini
echo [NOTIFICATIONS] >> backups\backup_config.ini
echo telegram_enabled=false >> backups\backup_config.ini
echo telegram_bot_token= >> backups\backup_config.ini
echo telegram_chat_id= >> backups\backup_config.ini
echo email_enabled=false >> backups\backup_config.ini
echo email_recipient= >> backups\backup_config.ini
echo ✅ Конфігурація створена

echo.
echo Крок 5: Створення скриптів управління USB...
call :create_usb_scripts
echo ✅ Скрипти управління створені

echo.
echo Крок 6: Налаштування планувальника завдань...
call :setup_task_scheduler
echo ✅ Планувальник налаштовано

echo.
echo Крок 7: Створення скриптів моніторингу...
call :create_monitoring_scripts
echo ✅ Моніторинг налаштовано

echo.
echo Крок 8: Тестування системи...
call :test_backup_system
if %errorlevel% neq 0 (
    echo ❌ Помилка тестування системи
    goto :error
)

echo.
echo ========================================
echo    USB БЕКАП НАЛАШТОВАНО УСПІШНО!
echo ========================================
echo.
echo Що налаштовано:
echo ✅ Директорії для бекапів
echo ✅ Конфігурація системи
echo ✅ Скрипти управління USB
echo ✅ Планувальник завдань (04:00 щодня)
echo ✅ Система моніторингу
echo ✅ Тестування системи
echo.
echo Для використання:
echo • Вставте USB диск з лейблом "KAVA_BACKUP"
echo • Система автоматично створить бекап о 04:00
echo • Ротація: видалення бекапів старше 30 днів
echo • Моніторинг: логи в backups\logs\
echo.
echo Корисні команди:
echo • backup_now.bat - створити бекап негайно
echo • check_usb.bat - перевірити USB диск
echo • backup_status.bat - статус бекапів
echo • cleanup_backups.bat - очистити старі бекапи
echo.
goto :end

:create_usb_scripts
echo Створення скриптів управління USB...

REM Скрипт пошуку USB диска
echo @echo off > backups\find_usb_drive.bat
echo chcp 65001 ^>nul >> backups\find_usb_drive.bat
echo echo Пошук USB диска з лейблом KAVA_BACKUP... >> backups\find_usb_drive.bat
echo. >> backups\find_usb_drive.bat
echo for /f "tokens=3" %%a in ('powershell "Get-WmiObject Win32_Volume ^| Where-Object { $_.Label -eq 'KAVA_BACKUP' } ^| Select-Object DriveLetter"') do ( >> backups\find_usb_drive.bat
echo     echo Знайдено USB диск: %%a >> backups\find_usb_drive.bat
echo     echo %%a^> usb_drive_letter.txt >> backups\find_usb_drive.bat
echo     exit /b 0 >> backups\find_usb_drive.bat
echo ) >> backups\find_usb_drive.bat
echo echo USB диск не знайдено >> backups\find_usb_drive.bat
echo exit /b 1 >> backups\find_usb_drive.bat

REM Скрипт копіювання на USB
echo @echo off > backups\copy_to_usb.bat
echo chcp 65001 ^>nul >> backups\copy_to_usb.bat
echo echo Копіювання бекапів на USB... >> backups\copy_to_usb.bat
echo. >> backups\copy_to_usb.bat
echo call find_usb_drive.bat >> backups\copy_to_usb.bat
echo if %errorlevel% neq 0 ( >> backups\copy_to_usb.bat
echo     echo ❌ USB диск не знайдено >> backups\copy_to_usb.bat
echo     exit /b 1 >> backups\copy_to_usb.bat
echo ) >> backups\copy_to_usb.bat
echo. >> backups\copy_to_usb.bat
echo set /p usb_drive=^< usb_drive_letter.txt >> backups\copy_to_usb.bat
echo set usb_backup_dir=%usb_drive%\kavacrm_backups >> backups\copy_to_usb.bat
echo. >> backups\copy_to_usb.bat
echo if not exist "%usb_backup_dir%" mkdir "%usb_backup_dir%" >> backups\copy_to_usb.bat
echo. >> backups\copy_to_usb.bat
echo echo Копіювання файлів... >> backups\copy_to_usb.bat
echo xcopy "kavacrm_db_*.gz" "%usb_backup_dir%\" /Y /Q >> backups\copy_to_usb.bat
echo xcopy "kavacrm_media_*.gz" "%usb_backup_dir%\" /Y /Q >> backups\copy_to_usb.bat
echo xcopy "kavacrm_static_*.gz" "%usb_backup_dir%\" /Y /Q >> backups\copy_to_usb.bat
echo xcopy "backup_report_*.txt" "%usb_backup_dir%\" /Y /Q >> backups\copy_to_usb.bat
echo. >> backups\copy_to_usb.bat
echo echo ✅ Копіювання завершено >> backups\copy_to_usb.bat
echo exit /b 0 >> backups\copy_to_usb.bat

REM Скрипт перевірки USB
echo @echo off > backups\check_usb.bat
echo chcp 65001 ^>nul >> backups\check_usb.bat
echo echo Перевірка USB диска... >> backups\check_usb.bat
echo. >> backups\check_usb.bat
echo call find_usb_drive.bat >> backups\check_usb.bat
echo if %errorlevel% neq 0 ( >> backups\check_usb.bat
echo     echo ❌ USB диск не знайдено або не підключений >> backups\check_usb.bat
echo     echo Переконайтеся що: >> backups\check_usb.bat
echo     echo 1. USB диск вставлений >> backups\check_usb.bat
echo     echo 2. Лейбл диска: KAVA_BACKUP >> backups\check_usb.bat
echo     echo 3. Диск відформатований в NTFS або FAT32 >> backups\check_usb.bat
echo     exit /b 1 >> backups\check_usb.bat
echo ) >> backups\check_usb.bat
echo. >> backups\check_usb.bat
echo set /p usb_drive=^< usb_drive_letter.txt >> backups\check_usb.bat
echo echo ✅ USB диск знайдено: %usb_drive% >> backups\check_usb.bat
echo. >> backups\check_usb.bat
echo echo Інформація про диск: >> backups\check_usb.bat
echo wmic logicaldisk where "DeviceID='%usb_drive%'" get Size,FreeSpace /format:list >> backups\check_usb.bat
echo. >> backups\check_usb.bat
echo set usb_backup_dir=%usb_drive%\kavacrm_backups >> backups\check_usb.bat
echo if not exist "%usb_backup_dir%" ( >> backups\check_usb.bat
echo     echo Створення директорії: %usb_backup_dir% >> backups\check_usb.bat
echo     mkdir "%usb_backup_dir%" >> backups\check_usb.bat
echo ) else ( >> backups\check_usb.bat
echo     echo ✅ Директорія існує: %usb_backup_dir% >> backups\check_usb.bat
echo     dir "%usb_backup_dir%" /b >> backups\check_usb.bat
echo ) >> backups\check_usb.bat
echo exit /b 0 >> backups\check_usb.bat
goto :eof

:setup_task_scheduler
echo Налаштування планувальника завдань...

REM Створення основного скрипта бекапу
echo @echo off > backup_now.bat
echo chcp 65001 ^>nul >> backup_now.bat
echo echo ======================================== >> backup_now.bat
echo echo    СТВОРЕННЯ БЕКАПУ KAVACRM >> backup_now.bat
echo echo ======================================== >> backup_now.bat
echo echo Час початку: %%date%% %%time%% >> backup_now.bat
echo echo. >> backup_now.bat
echo. >> backup_now.bat
echo REM Перехід до директорії проекту >> backup_now.bat
echo cd /d "%~dp0" >> backup_now.bat
echo. >> backup_now.bat
echo REM Створення бекапу через Django >> backup_now.bat
echo echo Створення бекапу бази даних... >> backup_now.bat
echo python manage.py backup --verbose >> backup_now.bat
echo if %%errorlevel%% neq 0 ( >> backup_now.bat
echo     echo ❌ Помилка створення бекапу >> backup_now.bat
echo     goto :backup_error >> backup_now.bat
echo ) >> backup_now.bat
echo. >> backup_now.bat
echo REM Копіювання на USB >> backup_now.bat
echo echo Копіювання на USB диск... >> backup_now.bat
echo call backups\copy_to_usb.bat >> backup_now.bat
echo. >> backup_now.bat
echo REM Очистка старих бекапів >> backup_now.bat
echo echo Очистка старих бекапів... >> backup_now.bat
echo call backups\cleanup_backups.bat >> backup_now.bat
echo. >> backup_now.bat
echo REM Створення звіту >> backup_now.bat
echo echo Створення звіту... >> backup_now.bat
echo call backups\create_backup_report.bat >> backup_now.bat
echo. >> backup_now.bat
echo echo ✅ Бекап завершено успішно >> backup_now.bat
echo echo Час завершення: %%date%% %%time%% >> backup_now.bat
echo goto :end >> backup_now.bat
echo. >> backup_now.bat
echo :backup_error >> backup_now.bat
echo echo ❌ Сталася помилка під час бекапу >> backup_now.bat
echo echo Перевірте логи в backups\logs\ >> backup_now.bat
echo. >> backup_now.bat
echo :end >> backup_now.bat
echo pause >> backup_now.bat

REM Скрипт створення завдання в планувальнику
echo @echo off > backups\setup_task_scheduler.bat
echo chcp 65001 ^>nul >> backups\setup_task_scheduler.bat
echo echo Налаштування планувальника завдань для щоденного бекапу... >> backups\setup_task_scheduler.bat
echo. >> backups\setup_task_scheduler.bat
echo REM Видалення старого завдання >> backups\setup_task_scheduler.bat
echo schtasks /delete /tn "KavaCRM Daily Backup" /f ^>nul 2^>^&1 >> backups\setup_task_scheduler.bat
echo. >> backups\setup_task_scheduler.bat
echo REM Створення нового завдання >> backups\setup_task_scheduler.bat
echo schtasks /create /tn "KavaCRM Daily Backup" /tr "%~dp0backup_now.bat" /sc daily /st 04:00 /rl highest /f >> backups\setup_task_scheduler.bat
echo if %%errorlevel%% neq 0 ( >> backups\setup_task_scheduler.bat
echo     echo ❌ Помилка створення завдання >> backups\setup_task_scheduler.bat
echo     exit /b 1 >> backups\setup_task_scheduler.bat
echo ) >> backups\setup_task_scheduler.bat
echo. >> backups\setup_task_scheduler.bat
echo echo ✅ Завдання створено успішно >> backups\setup_task_scheduler.bat
echo echo Бекап буде виконуватися щодня о 04:00 >> backups\setup_task_scheduler.bat
echo. >> backups\setup_task_scheduler.bat
echo REM Перевірка завдання >> backups\setup_task_scheduler.bat
echo schtasks /query /tn "KavaCRM Daily Backup" >> backups\setup_task_scheduler.bat
echo exit /b 0 >> backups\setup_task_scheduler.bat

REM Запуск налаштування планувальника
call backups\setup_task_scheduler.bat
goto :eof

:create_monitoring_scripts
echo Створення скриптів моніторингу...

REM Скрипт перевірки статусу бекапів
echo @echo off > backup_status.bat
echo chcp 65001 ^>nul >> backup_status.bat
echo echo ======================================== >> backup_status.bat
echo echo    СТАТУС БЕКАПІВ KAVACRM >> backup_status.bat
echo echo ======================================== >> backup_status.bat
echo echo. >> backup_status.bat
echo echo Локальні бекапи: >> backup_status.bat
echo dir backups\kavacrm_*.gz /b /o-d 2^>nul ^| findstr . ^>nul >> backup_status.bat
echo if %%errorlevel%% neq 0 ( >> backup_status.bat
echo     echo ❌ Локальні бекапи не знайдені >> backup_status.bat
echo ) else ( >> backup_status.bat
echo     dir backups\kavacrm_*.gz /b /o-d >> backup_status.bat
echo ) >> backup_status.bat
echo. >> backup_status.bat
echo echo USB бекапи: >> backup_status.bat
echo call backups\check_usb.bat ^>nul 2^>^&1 >> backup_status.bat
echo if %%errorlevel%% neq 0 ( >> backup_status.bat
echo     echo ❌ USB диск не доступний >> backup_status.bat
echo ) else ( >> backup_status.bat
echo     set /p usb_drive=^< usb_drive_letter.txt >> backup_status.bat
echo     dir "%%usb_drive%%\kavacrm_backups" /b /o-d 2^>nul >> backup_status.bat
echo ) >> backup_status.bat
echo. >> backup_status.bat
echo echo Останні логи: >> backup_status.bat
echo dir backups\logs\*.log /b /o-d 2^>nul ^| findstr . ^>nul >> backup_status.bat
echo if %%errorlevel%% neq 0 ( >> backup_status.bat
echo     echo ❌ Логи не знайдені >> backup_status.bat
echo ) else ( >> backup_status.bat
echo     for /f %%i in ('dir backups\logs\*.log /b /o-d') do ( >> backup_status.bat
echo         echo %%i: >> backup_status.bat
echo         type backups\logs\%%i ^| findstr /i "error\|success\|failed" ^| tail -5 >> backup_status.bat
echo         goto :next_log >> backup_status.bat
echo     ) >> backup_status.bat
echo     :next_log >> backup_status.bat
echo ) >> backup_status.bat
echo. >> backup_status.bat
echo echo Планувальник завдань: >> backup_status.bat
echo schtasks /query /tn "KavaCRM Daily Backup" /fo list ^| findstr "Status\|Last Run\|Next Run" >> backup_status.bat
echo. >> backup_status.bat
echo pause >> backup_status.bat

REM Скрипт очистки старих бекапів
echo @echo off > backups\cleanup_backups.bat
echo chcp 65001 ^>nul >> backups\cleanup_backups.bat
echo echo Очистка старих бекапів... >> backups\cleanup_backups.bat
echo. >> backups\cleanup_backups.bat
echo REM Видалення файлів старше 30 днів >> backups\cleanup_backups.bat
echo forfiles /p "backups" /s /m kavacrm_*.gz /d -30 /c "cmd /c del @path" 2^>nul >> backups\cleanup_backups.bat
echo forfiles /p "backups" /s /m backup_report_*.txt /d -30 /c "cmd /c del @path" 2^>nul >> backups\cleanup_backups.bat
echo forfiles /p "backups\logs" /m *.log /d -90 /c "cmd /c del @path" 2^>nul >> backups\cleanup_backups.bat
echo. >> backups\cleanup_backups.bat
echo echo ✅ Очистка завершена >> backups\cleanup_backups.bat
echo exit /b 0 >> backups\cleanup_backups.bat

REM Скрипт створення звіту
echo @echo off > backups\create_backup_report.bat
echo chcp 65001 ^>nul >> backups\create_backup_report.bat
echo setlocal enabledelayedexpansion >> backups\create_backup_report.bat
echo. >> backups\create_backup_report.bat
echo set "timestamp=%%date:~-4%%-%%date:~3,2%%-%%date:~0,2%%_%%time:~0,2%%-%%time:~3,2%%-%%time:~6,2%%" >> backups\create_backup_report.bat
echo set "timestamp=%%timestamp: =0%%" >> backups\create_backup_report.bat
echo set "report_file=backups\backup_report_%%timestamp%%.txt" >> backups\create_backup_report.bat
echo. >> backups\create_backup_report.bat
echo echo ======================================== ^> "%%report_file%%" >> backups\create_backup_report.bat
echo echo    ЗВІТ ПРО БЕКАП KAVACRM ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo echo ======================================== ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo echo Дата створення: %%date%% %%time%% ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo echo. ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo. >> backups\create_backup_report.bat
echo echo ЛОКАЛЬНІ БЕКАПИ: ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo dir backups\kavacrm_*.gz /b /o-d 2^>nul ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo if %%errorlevel%% neq 0 echo Немає локальних бекапів ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo. ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo echo USB БЕКАПИ: ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo call find_usb_drive.bat ^>nul 2^>^&1 >> backups\create_backup_report.bat
echo if %%errorlevel%% neq 0 ( >> backups\create_backup_report.bat
echo     echo USB диск не знайдено ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo ) else ( >> backups\create_backup_report.bat
echo     set /p usb_drive=^< usb_drive_letter.txt >> backups\create_backup_report.bat
echo     dir "%%usb_drive%%\kavacrm_backups" /b /o-d 2^>nul ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo ) >> backups\create_backup_report.bat
echo. ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo echo СТАТИСТИКА: ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo for /f %%i in ('dir backups\kavacrm_*.gz /b 2^>nul ^| find /c "kavacrm_"') do echo Кількість бекапів: %%i ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo for /f %%i in ('dir backups\kavacrm_*.gz /b 2^>nul ^| for /f "tokens=4" %%j in ("findstr /r /c:".*bytes free" dir /-c backups 2^>nul"') do @echo %%j') do echo Розмір бекапів: %%i bytes ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo. ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo echo СИСТЕМНА ІНФОРМАЦІЯ: ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo echo Користувач: %%USERNAME%% ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo echo Комп'ютер: %%COMPUTERNAME%% ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo systeminfo ^| findstr /c:"Total Physical Memory" ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo. ^>^> "%%report_file%%" >> backups\create_backup_report.bat
echo echo ✅ Звіт створено: %%report_file%% >> backups\create_backup_report.bat
echo type "%%report_file%%" >> backups\create_backup_report.bat
echo exit /b 0 >> backups\create_backup_report.bat
goto :eof

:test_backup_system
echo Тестування системи бекапу...

REM Тест 1: Перевірка конфігурації
if not exist "backups\backup_config.ini" (
    echo ❌ Конфігурація не знайдена
    goto :error
)
echo ✅ Конфігурація існує

REM Тест 2: Перевірка скриптів
if not exist "backup_now.bat" (
    echo ❌ Основний скрипт бекапу не знайдено
    goto :error
)
echo ✅ Основний скрипт існує

REM Тест 3: Перевірка планувальника
schtasks /query /tn "KavaCRM Daily Backup" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Завдання планувальника не знайдено
    goto :error
)
echo ✅ Завдання планувальника існує

REM Тест 4: Перевірка USB (опціонально)
call backups\check_usb.bat >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ USB диск доступний
) else (
    echo ⚠️  USB диск не доступний (це нормально, якщо не вставлений)
)

echo ✅ Тестування завершено успішно
goto :eof

:error
echo ❌ Сталася помилка під час налаштування
echo Перевірте логи вище
pause
exit /b 1

:end
echo.
echo Для ручного тестування:
echo • backup_now.bat - створити бекап негайно
echo • backup_status.bat - перевірити статус
echo • backups\check_usb.bat - перевірити USB
echo.
pause
