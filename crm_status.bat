@echo off
chcp 65001 >nul
echo === СТАТУС CRM СИСТЕМИ ===

REM Перевірка служб
echo [1/3] Служби:
nssm-2.24\win64\nssm.exe status KavaCRM 2>nul | findstr SERVICE_RUNNING >nul
if %errorlevel% equ 0 (echo   ✓ KavaCRM: RUNNING) else (echo   ✗ KavaCRM: STOPPED)

sc query Apache2.4 2>nul | findstr RUNNING >nul
if %errorlevel% equ 0 (echo   ✓ Apache: RUNNING) else (echo   ✗ Apache: STOPPED)

REM Перевірка портів
echo [2/3] Порти:
netstat -ano 2>nul | findstr :8000 >nul
if %errorlevel% equ 0 (echo   ✓ Django: LISTENING :8000) else (echo   ✗ Django: NOT FOUND)

netstat -ano 2>nul | findstr :80 >nul
if %errorlevel% equ 0 (echo   ✓ Apache: LISTENING :80) else (echo   ✗ Apache: NOT FOUND)

REM Перевірка доступу (швидка)
echo [3/3] Доступ:
call safe_cmd.bat "curl -s http://localhost/crm/ >nul 2>&1 && echo   ✓ Локальний доступ працює || echo   ✗ Локальний доступ не працює"

echo.
echo === ПЕРЕВІРКА ЗАВЕРШЕНА ===
echo Для детальної діагностики використовуйте: safe_cmd.bat "команда"
