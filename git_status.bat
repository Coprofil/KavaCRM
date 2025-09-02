@echo off
chcp 65001 >nul
echo ========================================
echo        СТАТУС GIT РЕПОЗИТОРІЮ
echo ========================================
echo.
echo Кодування: UTF-8 (підтримує українську мову)
echo.

REM Перевірка Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git не встановлений!
    echo.
    echo Встановіть Git: https://git-scm.com/download/win
    goto end
)

echo ✅ Git встановлений

REM Перевірка чи це Git репозиторій
if not exist .git (
    echo ❌ Це не Git репозиторій!
    echo.
    echo Запустіть git_init_fixed.bat для ініціалізації
    goto end
)

echo ✅ Git репозиторій знайдено

echo.
echo 📊 ІНФОРМАЦІЯ ПРО РЕПОЗИТОРІЙ:
echo ===============================
echo.

REM Інформація про користувача
echo 👤 Git користувач:
git config user.name
git config user.email
echo.

REM Статус файлів
echo 📁 Статус файлів:
git status --porcelain
if %errorlevel% neq 0 (
    echo   (Немає змін)
)
echo.

REM Поточна гілка
echo 🌿 Поточна гілка:
git branch --show-current
echo.

REM Всі гілки
echo 🌳 Всі гілки:
git branch -a
echo.

REM Останні коміти
echo 📝 Останні коміти:
git log --oneline -5
if %errorlevel% neq 0 (
    echo   (Немає комітів)
)
echo.

REM Remote репозиторії
echo 🔗 Remote репозиторії:
git remote -v
if %errorlevel% neq 0 (
    echo   (Немає remote репозиторіїв)
)

echo.
echo 🎯 ШВИДКІ КОМАНДИ:
echo =================
echo.
echo git add .           - додати всі зміни
echo git commit -m "msg" - створити коміт
echo git push            - відправити на GitHub
echo git pull            - отримати з GitHub
echo git status          - статус файлів
echo.

:end
echo.
pause
