@echo off
echo ========================================
echo       GIT STATUS CHECK
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul

echo Current codepage: UTF-8
echo.

REM Check Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Git: NOT INSTALLED
    echo.
    echo Install Git from: https://git-scm.com/download/win
    goto end
)

echo √ Git: INSTALLED
echo.

REM Check user configuration
echo Checking user configuration:
echo ===========================

for /f %%i in ('git config user.name') do set GIT_USER=%%i
if "%GIT_USER%"=="" (
    echo X User name: NOT CONFIGURED
) else (
    echo √ User name: %GIT_USER%
)

for /f %%i in ('git config user.email') do set GIT_EMAIL=%%i
if "%GIT_EMAIL%"=="" (
    echo X User email: NOT CONFIGURED
) else (
    echo √ User email: %GIT_EMAIL%
)

echo.

REM Check repository
echo Checking repository:
echo ===================

if exist .git (
    echo √ Repository: INITIALIZED
) else (
    echo X Repository: NOT INITIALIZED
    goto end
)

REM Check commits
echo.
echo Checking commits:
echo ================
git log --oneline -1 >nul 2>&1
if %errorlevel% equ 0 (
    echo √ Commits: EXIST
    echo Last commit:
    git log --oneline -1
) else (
    echo X Commits: NONE
)

REM Check remote
echo.
echo Checking remote:
echo ===============
git remote get-url origin >nul 2>&1
if %errorlevel% equ 0 (
    echo √ Remote: CONFIGURED
    for /f %%i in ('git remote get-url origin') do echo URL: %%i
) else (
    echo X Remote: NOT CONFIGURED
)

REM Show quick commands
echo.
echo QUICK COMMANDS:
echo ===============
echo git status     - Check file status
echo git add .      - Add all changes
echo git commit -m "msg" - Create commit
echo git push       - Push to GitHub
echo git pull       - Pull from GitHub

:end
echo.
echo ========================================
echo         STATUS SUMMARY
echo ========================================
echo.
echo If you see X marks above, run:
echo - git_user_config.bat (for user setup)
echo - git_quick_init.bat (for repository)
echo - github_publish_simple.bat (for GitHub)
echo.
pause
