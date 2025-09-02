@echo off
echo ========================================
echo    БЕКАП + GIT COMMIT + PUSH
echo ========================================

REM Перевірка Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git не встановлений!
    pause
    exit /b 1
)

echo ✅ Git готовий

REM Створення бекапу
echo ℹ️  Створення бекапу...
if exist backup_simple.py (
    python backup_simple.py
    echo ✅ Бекап створено
) else (
    echo ⚠️  Скрипт бекапу не знайдено, пропускаємо бекап
)

REM Перевірка статусу Git
echo ℹ️  Перевірка змін у Git...
git status --porcelain > temp_status.txt
set /p has_changes=<temp_status.txt
del temp_status.txt

if "%has_changes%"=="" (
    echo ✅ Немає нових змін для коміту
    echo.
    echo Інформація про останній коміт:
    git log --oneline -1
    echo.
    goto :push_section
)

echo ✅ Знайдено зміни, додаємо до Git...
git add .

REM Створення коміту з повідомленням
echo Поточна дата/час: %date% %time%
echo.
echo Введіть повідомлення для коміту (або натисніть Enter для автоматичного):
set /p commit_message=

if "%commit_message%"=="" (
    set commit_message=Backup and update - %date% %time%
)

echo ℹ️  Створення коміту: "%commit_message%"
git commit -m "%commit_message%"

if %errorlevel% neq 0 (
    echo ❌ Помилка створення коміту
    git status
    pause
    exit /b 1
)

echo ✅ Коміт створено

:push_section
REM Відправка на GitHub
echo ℹ️  Відправка на GitHub...

REM Перевірка чи є remote
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Remote origin не налаштований
    echo.
    echo Запустіть publish_to_github.bat для налаштування GitHub
    pause
    exit /b 1
)

git push origin main

if %errorlevel% equ 0 (
    echo ✅ Код відправлено на GitHub
) else (
    echo ❌ Помилка відправки на GitHub
    echo.
    echo Можливі рішення:
    echo • Перевірте інтернет з'єднання
    echo • Перевірте права доступу до репозиторію
    echo • Спробуйте: git push --force-with-lease origin main
    pause
    exit /b 1
)

REM Відправка develop гілки якщо вона існує
git branch --list develop >nul 2>&1
if %errorlevel% equ 0 (
    echo ℹ️  Відправка develop гілки...
    git push origin develop
    if %errorlevel% equ 0 (
        echo ✅ Develop гілка відправлена
    ) else (
        echo ⚠️  Помилка відправки develop гілки
    )
)

echo.
echo ========================================
echo     ОПЕРАЦІЯ ЗАВЕРШЕНА УСПІШНО!
echo ========================================
echo.
echo ✅ Бекап створено
echo ✅ Зміни збережено в Git
echo ✅ Код відправлено на GitHub
echo.
echo 📊 СТАТИСТИКА:
echo.
git log --oneline -3
echo.
echo 🎯 РЕКОМЕНДАЦІЇ:
echo • Регулярно робіть такі бекапи
echo • Пишіть змістовні повідомлення комітів
echo • Синхронізуйте роботу з командою через Git
echo.
pause
