@echo off
echo ========================================
echo      GIT REPOSITORY STATUS
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul

echo Current codepage: UTF-8
echo.

REM Check Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed!
    echo.
    echo Install Git from: https://git-scm.com/download/win
    goto end
)

echo Git is installed.
echo.

REM Check if this is a Git repository
if not exist .git (
    echo ERROR: This is not a Git repository!
    echo.
    echo Run git_init_simple.bat to initialize
    goto end
)

echo Git repository found.
echo.

echo REPOSITORY INFORMATION:
echo ======================
echo.

REM User information
echo Git user:
git config user.name
git config user.email
echo.

REM Current branch
echo Current branch:
git branch --show-current
echo.

REM File status
echo File status:
git status --porcelain
if %errorlevel% neq 0 (
    echo (No changes)
)
echo.

REM All branches
echo All branches:
git branch -a
echo.

REM Recent commits
echo Recent commits:
git log --oneline -5
if %errorlevel% neq 0 (
    echo (No commits)
)
echo.

REM Remote repositories
echo Remote repositories:
git remote -v
if %errorlevel% neq 0 (
    echo (No remote repositories)
)

echo.
echo QUICK COMMANDS:
echo ===============
echo.
echo git add .           - add all changes
echo git commit -m "msg" - create commit
echo git push            - push to GitHub
echo git pull            - pull from GitHub
echo git status          - check file status
echo.

:end
echo.
pause
