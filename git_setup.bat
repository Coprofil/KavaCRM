@echo off
echo ========================================
echo        НАЛАШТУВАННЯ GIT
echo ========================================
echo.

REM Встановлюємо кодування UTF-8
chcp 65001 >nul

echo Поточна кодова сторінка: UTF-8
echo.

REM Перевірка Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git не встановлений!
    echo.
    echo Встановіть Git з: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git встановлений успішно!
echo.

REM Налаштування користувача
echo Налаштування імені користувача...
echo Введіть ваше ім'я (наприклад: Ivan Petrov):
set /p user_name=

echo Налаштування email...
echo Введіть ваш email (наприклад: ivan@example.com):
set /p user_email=

REM Налаштування Git
echo.
echo Налаштування Git...
git config --global user.name "%user_name%"
git config --global user.email "%user_email%"

echo.
echo Перевірка налаштувань:
git config --global user.name
git config --global user.email

echo.
echo ========================================
echo   GIT НАЛАШТОВАНИЙ УСПІШНО!
echo ========================================
echo.
echo Тепер можна використовувати Git команди.
echo Рекомендується запустити git_init_fixed.bat
echo.
pause
