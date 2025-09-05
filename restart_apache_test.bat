@echo off
echo === Перезапуск Apache та тестування конфігурації ===

cd /d C:\srv\kava\app\kavapro

echo 1. Зупинка Apache...
net stop apache2.4

echo 2. Старт Apache...
net start apache2.4

echo 3. Перевірка статусу...
sc query apache2.4

echo 4. Тест локального доступу...
timeout /t 2 /nobreak > nul
curl -s http://localhost/crm/ | findstr "KavaCRM" > nul
if %errorlevel% equ 0 (
    echo ✅ Локальний доступ працює!
) else (
    echo ❌ Локальний доступ не працює
)

echo.
echo === Для тестування зовнішнього доступу ===
echo Відкрийте в браузері: http://kava-crm.asuscomm.com/crm/
echo.
pause
