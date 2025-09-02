@echo off
echo ========================================
echo      START WORK SESSION
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul

echo Current codepage: UTF-8
echo Time: %date% %time%
echo.

REM Check Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git not installed!
    pause
    exit /b 1
)

echo Git is ready.
echo.

REM Check repository
if not exist .git (
    echo ERROR: Not a Git repository!
    echo Run git_quick_init.bat first
    pause
    exit /b 1
)

echo Repository found.
echo.

REM Check remote
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: No remote repository configured
    echo You won't be able to sync with GitHub
    echo.
) else (
    echo Remote repository configured.
    echo.

    REM Pull latest changes
    echo Pulling latest changes from GitHub...
    git pull origin master
    if %errorlevel% equ 0 (
        echo Successfully pulled latest changes!
    ) else (
        echo WARNING: Could not pull changes
        echo You might have local changes that conflict
    )
    echo.
)

REM Show current status
echo CURRENT STATUS:
echo ===============
git status
echo.

REM Show recent commits
echo RECENT WORK:
echo ============
git log --oneline -3
echo.

echo ========================================
echo     READY TO WORK!
echo ========================================
echo.
echo You can now start working on your project.
echo.
echo When you're done for the day, run:
echo git_daily_sync.bat
echo.
echo This will save all your changes to GitHub.
echo.
pause
