@echo off
echo ========================================
echo      GIT INITIALIZATION
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul

echo Current codepage: UTF-8
echo.

REM Check Git installation
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed!
    echo.
    echo Install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git is installed successfully!
echo.

REM Check if user is configured
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git user is not configured!
    echo.
    echo Run git_setup.bat first to configure Git user
    pause
    exit /b 1
)

echo Git user is configured.
echo.

REM Initialize Git repository
if not exist .git (
    echo Initializing Git repository...
    git init
    echo Git repository initialized.
) else (
    echo Git repository already exists.
)

echo.

REM Check .gitignore
if exist .gitignore (
    echo .gitignore file exists.
) else (
    echo WARNING: .gitignore file not found.
    echo Create .gitignore file with necessary rules.
    pause
    exit /b 1
)

echo.

REM Add files to Git
echo Adding files to Git...
git add .

REM Create first commit with simple message
echo Creating first commit...
git commit -m "Initial commit - KavaCRM project

Django CRM system with:
- Client management
- Route planning
- Unloading system
- Technical service module
- Analytics and reports
- 2FA authentication
- Monitoring system
- AI integration
- Automatic backups"

if %errorlevel% equ 0 (
    echo First commit created successfully!
) else (
    echo ERROR: Failed to create commit
    git status
    pause
    exit /b 1
)

REM Create develop branch
echo Creating develop branch...
git branch develop
echo Develop branch created.

echo.

REM Show status
echo ========================================
echo     GIT REPOSITORY READY!
echo ========================================
echo.
echo Current status:
git status
echo.
echo Last commits:
git log --oneline -3
echo.
echo Next steps:
echo 1. Create repository on GitHub
echo 2. Run github_publish_fixed.bat
echo 3. Push code to GitHub
echo.
echo Useful commands:
echo - git status (check status)
echo - git add . (add all changes)
echo - git commit -m "message" (create commit)
echo - git push (push to GitHub)
echo.
pause
