@echo off
echo ========================================
echo      QUICK GIT INITIALIZATION
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul

echo Current codepage: UTF-8
echo.

REM Check Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git not installed!
    echo Install from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git found.
echo.

REM Configure user if not configured
for /f %%i in ('git config user.name') do set GIT_USER=%%i
if "%GIT_USER%"=="" (
    echo Configuring Git user...
    git config user.name "KavaCRM User"
    git config user.email "user@kavacrm.local"
    echo User configured.
)

REM Initialize repository if not initialized
if not exist .git (
    echo Initializing Git repository...
    git init
    echo Repository initialized.
) else (
    echo Repository already exists.
)

REM Check if there are commits
git log --oneline -1 >nul 2>&1
if %errorlevel% neq 0 (
    echo No commits found, creating initial commit...

    REM Add files
    echo Adding files...
    git add .

    REM Create commit
    echo Creating commit...
    git commit -m "Initial KavaCRM commit"
    if %errorlevel% equ 0 (
        echo.
        echo ========================================
        echo     INITIAL COMMIT CREATED!
        echo ========================================
        echo.
        git log --oneline -1
        echo.
        echo Now you can run: github_publish_simple.bat
        echo to publish to GitHub.
        echo.
    ) else (
        echo ERROR: Failed to create commit
        git status
    )
) else (
    echo Commits already exist.
    echo Last commit:
    git log --oneline -1
)

echo.
echo Repository status:
git status --porcelain | find /c "."

echo.
pause
