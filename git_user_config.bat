@echo off
echo ========================================
echo     GIT USER CONFIGURATION
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul

echo Current codepage: UTF-8
echo.

REM Check Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git not found!
    echo Install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git is installed.
echo.

echo Current Git configuration:
echo =========================
echo User name: 
git config user.name
echo User email:
git config user.email
echo.

echo Setting up default user...
echo ========================
echo.

REM Set default values if empty
for /f %%i in ('git config user.name') do set CURRENT_NAME=%%i
if "%CURRENT_NAME%"=="" (
    echo Setting default user name...
    git config user.name "KavaCRM Developer"
    echo Default name set: KavaCRM Developer
) else (
    echo User name already set: %CURRENT_NAME%
)

for /f %%i in ('git config user.email') do set CURRENT_EMAIL=%%i
if "%CURRENT_EMAIL%"=="" (
    echo Setting default user email...
    git config user.email "dev@kavacrm.local"
    echo Default email set: dev@kavacrm.local
) else (
    echo User email already set: %CURRENT_EMAIL%
)

echo.
echo Final configuration:
echo ===================
echo Name: 
git config user.name
echo Email:
git config user.email

echo.
echo ========================================
echo     CONFIGURATION COMPLETE
echo ========================================
echo.
echo Git user is now configured.
echo You can now create commits.
echo.
pause
