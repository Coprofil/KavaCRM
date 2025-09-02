@echo off
echo ========================================
echo    ПУБЛІКАЦІЯ ПРОЕКТУ НА GITHUB
echo ========================================

REM Перевірка Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git не встановлений!
    echo.
    echo Встановіть Git з https://git-scm.com/download/win
    echo та запустіть скрипт знову.
    pause
    exit /b 1
)

echo ✅ Git встановлений

REM Перевірка чи ініціалізований репозиторій
if not exist .git (
    echo ❌ Git репозиторій не ініціалізований!
    echo.
    echo Запустіть спочатку init_git_repo.bat
    pause
    exit /b 1
)

echo ✅ Git репозиторій ініціалізований

REM Перевірка наявності комітів
git log --oneline -1 >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Немає комітів у репозиторії!
    echo.
    echo Запустіть спочатку init_git_repo.bat
    pause
    exit /b 1
)

echo ✅ Знайдено коміти

echo.
echo 🔗 ІНСТРУКЦІЇ ПО СТВОРЕННЮ GITHUB РЕПОЗИТОРІЮ:
echo ================================================
echo.
echo 1. Перейдіть на https://github.com/new
echo 2. Введіть назву репозиторію: KavaCRM
echo 3. Додайте опис: "CRM система управління клієнтами з AI"
echo 4. ОБОВ'ЯЗКОВО: НЕ ставте галочку "Add a README file"
echo 5. НЕ ставте галочку "Add .gitignore"
echo 6. НЕ додавайте ліцензію поки що
echo 7. Натисніть "Create repository"
echo.
echo 8. Скопіюйте URL репозиторію (наприклад: https://github.com/username/KavaCRM.git)
echo.

set /p repo_url="Введіть URL вашого GitHub репозиторію: "

if "%repo_url%"=="" (
    echo ❌ URL не введено!
    pause
    exit /b 1
)

echo.
echo ℹ️  Налаштування remote origin...
git remote add origin "%repo_url%"

if %errorlevel% neq 0 (
    echo ⚠️  Remote origin вже існує, оновлюємо...
    git remote set-url origin "%repo_url%"
)

echo ✅ Remote origin налаштований

echo.
echo ℹ️  Відправка коду на GitHub...
echo Це може зайняти деякий час залежно від розміру проекту...

REM Відправка на GitHub
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo        ПРОЕКТ ОПУБЛІКОВАНО!
    echo ========================================
    echo.
    echo ✅ Репозиторій успішно створено на GitHub
    echo 🌐 URL: %repo_url%
    echo.
    echo 🔧 НАСТУПНІ КРОКИ:
    echo.
    echo 1. Перевірте репозиторій на GitHub
    echo 2. Додайте опис проекту в README
    echo 3. Налаштуйте GitHub Actions для CI/CD (опціонально)
    echo 4. Запросіть контрибʼюторів
    echo.
    echo 📚 КОРИСНІ КОМАНДИ:
    echo.
    echo • git status                    - статус змін
    echo • git add .                     - додати всі зміни
    echo • git commit -m "повідомлення"  - створити коміт
    echo • git push                      - відправити на GitHub
    echo • git pull                      - отримати зміни з GitHub
    echo.
    echo 🔒 ВАЖЛИВО:
    echo • НІКОЛИ не комітьте .env файли
    echo • НІКОЛИ не комітьте секретні ключі
    echo • Використовуйте .gitignore для виключення чутливих файлів
    echo.
) else (
    echo.
    echo ❌ ПОМИЛКА ВІДПРАВКИ НА GITHUB
    echo.
    echo Можливі причини:
    echo • Неправильний URL репозиторію
    echo • Немає доступу до репозиторію
    echo • Проблеми з інтернетом
    echo.
    echo Спробуйте:
    echo 1. Перевірити URL репозиторію
    echo 2. Перевірити права доступу
    echo 3. Спробувати: git push --force-with-lease origin main
    echo.
    pause
    exit /b 1
)

REM Створення develop гілки на GitHub
echo.
echo ℹ️  Створення develop гілки на GitHub...
git push -u origin develop

if %errorlevel% equ 0 (
    echo ✅ Develop гілка відправлена на GitHub
) else (
    echo ⚠️  Не вдалося відправити develop гілку
)

echo.
echo 🎉 ВІТАЄМО! ПРОЕКТ ПОВНІСТЮ ГОТОВИЙ ДО СПІВПРАЦІ
echo.
echo Тепер ви можете:
echo • Ділитися проектом з командою
echo • Приймати контрибʼюції
echo • Відстежувати зміни
echo • Створювати релізи
echo.
pause
