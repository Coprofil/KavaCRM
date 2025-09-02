@echo off
echo ========================================
echo        CREATE GIT COMMIT NOW
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul

echo Setting up Git user...
git config user.name "KavaCRM User"
git config user.email "user@kavacrm.local"

echo Creating simple commit...
git commit -m "Initial KavaCRM commit"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo      SUCCESS: COMMIT CREATED!
    echo ========================================
    echo.
    git log --oneline -1
    echo.
    echo Now you can run: github_publish_simple.bat
    echo.
) else (
    echo.
    echo ========================================
    echo         COMMIT FAILED
    echo ========================================
    echo.
    echo Try these manual commands:
    echo.
    echo git config user.name "Your Name"
    echo git config user.email "your@email.com"
    echo git commit -m "Initial commit"
    echo.
    git status
)

echo.
pause
