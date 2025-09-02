@echo off
chcp 65001 >nul
echo ========================================
echo    ІНІЦІАЛІЗАЦІЯ GIT РЕПОЗИТОРІЮ
echo ========================================
echo.
echo Кодування встановлено на UTF-8
echo Тепер українська мова буде відображатися правильно!
echo.

REM Перевірка чи встановлений Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git не встановлений!
    echo.
    echo Для встановлення Git:
    echo 1. Завантажте з https://git-scm.com/download/win
    echo 2. Встановіть з налаштуваннями за замовчуванням
    echo 3. Перезапустіть командний рядок
    echo 4. Запустіть цей скрипт знову
    echo.
    pause
    exit /b 1
)

echo ✅ Git встановлений

REM Ініціалізація Git репозиторію
if not exist .git (
    echo ℹ️  Ініціалізація Git репозиторію...
    git init
    echo ✅ Git репозиторій ініціалізований
) else (
    echo ✅ Git репозиторій вже існує
)

REM Налаштування Git користувача (якщо не налаштований)
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Git користувач не налаштований
    echo Введіть ваше ім'я для Git:
    set /p git_name=
    git config user.name "%git_name%"
    echo Введіть ваш email для Git:
    set /p git_email=
    git config user.email "%git_email%"
    echo ✅ Git користувач налаштований
)

REM Перевірка .gitignore
if exist .gitignore (
    echo ✅ Файл .gitignore існує
) else (
    echo ❌ Файл .gitignore не знайдений
    echo Створіть .gitignore файл з необхідними правилами
    pause
    exit /b 1
)

REM Додавання файлів до Git
echo ℹ️  Додавання файлів до Git...
git add .

REM Створення першого коміту
echo ℹ️  Створення першого коміту...
git commit -m "Initial commit - KavaCRM project

- Django CRM система
- Повний функціонал управління клієнтами
- Система маршрутів та відвантажень
- Модуль технічного обслуговування
- Аналітика та звіти
- 2FA аутентифікація
- Моніторинг системи
- RAG інтеграція з LLM
- Автоматичні бекапи

Features:
✅ Керування клієнтами та агентами
✅ Планувальник маршрутів
✅ Система відвантажень
✅ Модуль технічного обслуговування
✅ Аналітика продажів
✅ 2FA безпека
✅ Telegram сповіщення
✅ Health monitoring
✅ RAG AI інтеграція
✅ Автоматичні бекапи"

if %errorlevel% equ 0 (
    echo ✅ Перший коміт створено успішно
) else (
    echo ❌ Помилка створення коміту
    git status
    pause
    exit /b 1
)

REM Створення develop гілки
echo ℹ️  Створення develop гілки...
git branch develop
echo ✅ Гілка develop створена

REM Показ статусу
echo.
echo ========================================
echo        GIT РЕПОЗИТОРІЙ ГОТОВИЙ!
echo ========================================
echo.
git status
echo.
git log --oneline -5
echo.
echo 🎉 РЕКОМЕНДАЦІЇ:
echo • Зберігайте код в develop гілці
echo • Регулярно робіть коміти
echo • Синхронізуйте з GitHub
echo.
echo 🔧 КОРИСНІ КОМАНДИ:
echo • git status - перевірка статусу
echo • git add . - додати всі зміни
echo • git commit -m "повідомлення" - створити коміт
echo • git log --oneline - історія комітів
echo • git branch - список гілок
echo.
echo 📝 ПРАВИЛА РОБОТИ З GIT:
echo • Завжди працюйте в develop гілці
echo • Використовуйте змістовні повідомлення комітів
echo • Регулярно синхронізуйте з віддаленим репозиторієм
echo.
pause
