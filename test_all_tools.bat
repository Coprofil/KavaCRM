@echo off
chcp 65001 >nul
echo ========================================
echo    ТЕСТУВАННЯ ВСІХ ІНСТРУМЕНТІВ
echo ========================================
echo.
echo Кодування: UTF-8
echo Українська мова: працює!
echo.

echo 🔧 ПЕРЕВІРКА ДОСТУПНИХ ІНСТРУМЕНТІВ:
echo ====================================
echo.

REM Перевірка основних інструментів
set tools[0]="git_init_fixed.bat - Ініціалізація Git"
set tools[1]="github_publish_fixed.bat - Публікація на GitHub"
set tools[2]="git_status.bat - Статус Git"
set tools[3]="backup_and_git.bat - Бекап + Git"
set tools[4]="create_backup.bat - Створення бекапу"
set tools[5]="check_encoding.bat - Перевірка кодування"
set tools[6]="fix_encoding.bat - Виправлення кодування"

set /a count=0
for %%t in ("%tools[0]%" "%tools[1]%" "%tools[2]%" "%tools[3]%" "%tools[4]%" "%tools[5]%" "%tools[6]%") do (
    for /f "tokens=1,* delims= " %%a in (%%t) do (
        if exist %%a (
            echo ✅ Знайдено: %%t
        ) else (
            echo ❌ Відсутній: %%t
        )
    )
    set /a count+=1
)

echo.
echo 📁 ПЕРЕВІРКА ПРОЕКТНИХ ФАЙЛІВ:
echo =============================
echo.

REM Перевірка важливих файлів проекту
set project_files[0]="README.md - Документація"
set project_files[1]="requirements_production.txt - Залежності"
set project_files[2]="kavapro\settings.py - Налаштування Django"
set project_files[3]="kavacrm\models.py - Моделі даних"
set project_files[4]=".gitignore - Git налаштування"
set project_files[5]="manage.py - Django менеджер"

for %%f in ("%project_files[0]%" "%project_files[1]%" "%project_files[2]%" "%project_files[3]%" "%project_files[4]%" "%project_files[5]%") do (
    for /f "tokens=1,* delims= " %%a in (%%f) do (
        if exist %%a (
            echo ✅ Знайдено: %%t
        ) else (
            echo ⚠️  Відсутній: %%t
        )
    )
)

echo.
echo 🛠️  ПЕРЕВІРКА ЗОВНІШНІХ ІНСТРУМЕНТІВ:
echo ===================================
echo.

REM Перевірка Git
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Git: встановлений
    for /f %%i in ('git --version') do echo    Версія: %%i
) else (
    echo ❌ Git: не встановлений
)

REM Перевірка Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python: встановлений
    for /f %%i in ('python --version 2^>^&1') do echo    Версія: %%i
) else (
    echo ❌ Python: не встановлений
)

echo.
echo 📊 СТАТИСТИКА ПРОЕКТУ:
echo =====================
echo.

REM Підрахунок файлів
if exist kavacrm\templates (
    for /f %%i in ('dir /b /s kavacrm\templates\*.html 2^>nul ^| find /c ".html"') do set html_count=%%i
) else (
    set html_count=0
)

if exist kavacrm (
    for /f %%i in ('dir /b /s kavacrm\*.py 2^>nul ^| find /c ".py"') do set py_count=%%i
) else (
    set py_count=0
)

echo 📄 HTML шаблонів: !html_count!
echo 🐍 Python файлів: !py_count!
echo 📦 Всього інструментів: 7

echo.
echo 🎯 РЕЗУЛЬТАТИ ТЕСТУВАННЯ:
echo =========================
echo.

REM Загальна оцінка
set /a score=0
if exist git_init_fixed.bat set /a score+=1
if exist github_publish_fixed.bat set /a score+=1
if exist README.md set /a score+=1
git --version >nul 2>&1 && set /a score+=1
python --version >nul 2>&1 && set /a score+=1

echo 📈 Оцінка готовності: !score!/5

if !score! equ 5 (
    echo ✅ ПРОЕКТ ПОВНІСТЮ ГОТОВИЙ!
    echo 🎉 Всі інструменти на місці
    echo 🚀 Можна починати роботу з Git
) else (
    echo ⚠️  Деякі компоненти відсутні
    echo 🔧 Потрібно встановити відсутні інструменти
)

echo.
echo 💡 РЕКОМЕНДОВАНИЙ ПОРЯДОК ДІЙ:
echo ===============================
echo.
echo 1. Встановіть Git (якщо не встановлений)
echo 2. Запустіть: git_init_fixed.bat
echo 3. Створіть репозиторій на GitHub
echo 4. Запустіть: github_publish_fixed.bat
echo 5. Перевіряйте статус: git_status.bat
echo 6. Робіть бекапи: backup_and_git.bat
echo.
echo 📚 ДОКУМЕНТАЦІЯ: GIT_INSTRUCTIONS.md
echo.

pause
