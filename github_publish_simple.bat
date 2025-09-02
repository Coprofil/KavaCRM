@echo off
echo ========================================
echo    PUBLISH TO GITHUB
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
    pause
    exit /b 1
)

echo Git is ready.
echo.

REM Check if repository is initialized
if not exist .git (
    echo ERROR: Git repository not initialized!
    echo.
    echo Run git_init_simple.bat first
    pause
    exit /b 1
)

echo Git repository found.
echo.

REM Check if there are commits
git log --oneline -1 >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: No commits in repository!
    echo.
    echo Run git_init_simple.bat first
    pause
    exit /b 1
)

echo Commits found.
echo.

echo GITHUB REPOSITORY CREATION INSTRUCTIONS:
echo ========================================
echo.
echo 1. Go to https://github.com/new
echo 2. Enter repository name: KavaCRM
echo 3. Add description: CRM system with AI
echo 4. IMPORTANT: DO NOT check "Add README file"
echo 5. DO NOT check "Add .gitignore"
echo 6. Click "Create repository"
echo.
echo 7. Copy repository URL (example: https://github.com/username/KavaCRM.git)
echo.

set /p repo_url=Enter your GitHub repository URL:

if "%repo_url%"=="" (
    echo ERROR: URL not entered!
    pause
    exit /b 1
)

echo.
echo Setting up remote origin...
git remote add origin "%repo_url%"

if %errorlevel% neq 0 (
    echo WARNING: Remote origin already exists, updating...
    git remote set-url origin "%repo_url%"
)

echo Remote origin configured.
echo.

echo Pushing code to GitHub...
echo This may take some time depending on project size...

REM Push to GitHub
git push -u origin master

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo      PROJECT PUBLISHED!
    echo ========================================
    echo.
    echo Repository successfully created on GitHub
    echo URL: %repo_url%
    echo.
    echo Next steps:
    echo 1. Check repository on GitHub
    echo 2. Add project description in README
    echo 3. Invite contributors
    echo.
    echo Useful commands:
    echo - git status (check status)
    echo - git add . (add changes)
    echo - git commit -m "message" (commit)
    echo - git push (push to GitHub)
    echo - git pull (pull from GitHub)
    echo.
) else (
    echo.
    echo ERROR: Failed to push to GitHub
    echo.
    echo Possible reasons:
    echo - Incorrect repository URL
    echo - No access to repository
    echo - Internet connection problems
    echo.
    echo Try:
    echo 1. Check repository URL
    echo 2. Check access rights
    echo 3. Try: git push --force-with-lease origin master
    echo.
    pause
    exit /b 1
)

echo.
echo Pushing develop branch...
git push -u origin develop

if %errorlevel% equ 0 (
    echo Develop branch pushed successfully.
) else (
    echo WARNING: Failed to push develop branch.
)

echo.
echo CONGRATULATIONS! PROJECT IS READY FOR COLLABORATION
echo.
echo Now you can:
echo - Share project with team
echo - Accept contributions
echo - Track changes
echo - Create releases
echo.
pause
