@echo off
echo ========================================
echo        TEST GIT SETUP
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul

echo Current codepage: UTF-8
echo.

REM Check Git installation
echo 1. Checking Git installation...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo    Git: INSTALLED
    for /f %%i in ('git --version') do echo    Version: %%i
) else (
    echo    Git: NOT INSTALLED
    echo    Install from: https://git-scm.com/download/win
    goto error
)

echo.

REM Check Git user configuration
echo 2. Checking Git user configuration...
git config user.name >nul 2>&1
if %errorlevel% equ 0 (
    echo    User name: CONFIGURED
    for /f %%i in ('git config user.name') do echo    Name: %%i
) else (
    echo    User name: NOT CONFIGURED
    echo    Run: git_setup.bat
    goto error
)

git config user.email >nul 2>&1
if %errorlevel% equ 0 (
    echo    User email: CONFIGURED
    for /f %%i in ('git config user.email') do echo    Email: %%i
) else (
    echo    User email: NOT CONFIGURED
    echo    Run: git_setup.bat
    goto error
)

echo.

REM Check if repository is initialized
echo 3. Checking Git repository...
if exist .git (
    echo    Repository: INITIALIZED
) else (
    echo    Repository: NOT INITIALIZED
    echo    Run: git_init_simple.bat
    goto error
)

echo.

REM Check commits
echo 4. Checking commits...
git log --oneline -1 >nul 2>&1
if %errorlevel% equ 0 (
    echo    Commits: FOUND
    echo    Last commit:
    git log --oneline -1
) else (
    echo    Commits: NOT FOUND
    echo    Run: git_init_simple.bat
    goto error
)

echo.

REM Check .gitignore
echo 5. Checking .gitignore...
if exist .gitignore (
    echo    .gitignore: EXISTS
) else (
    echo    .gitignore: MISSING
    echo    Create .gitignore file
)

echo.

REM Check remote
echo 6. Checking remote repository...
git remote get-url origin >nul 2>&1
if %errorlevel% equ 0 (
    echo    Remote: CONFIGURED
    for /f %%i in ('git remote get-url origin') do echo    URL: %%i
) else (
    echo    Remote: NOT CONFIGURED
    echo    Run: github_publish_simple.bat
)

echo.

REM Check current branch
echo 7. Checking current branch...
for /f %%i in ('git branch --show-current') do echo    Current branch: %%i

echo.

REM Final status
echo ========================================
echo           TEST RESULTS
echo ========================================
echo.

set /a score=0

git --version >nul 2>&1 && set /a score+=1
git config user.name >nul 2>&1 && set /a score+=1
git config user.email >nul 2>&1 && set /a score+=1
if exist .git set /a score+=1
git log --oneline -1 >nul 2>&1 && set /a score+=1

echo Score: !score!/5

if !score! equ 5 (
    echo.
    echo ========================================
    echo     SUCCESS: GIT IS READY!
    echo ========================================
    echo.
    echo All Git components are configured correctly.
    echo You can now work with Git and GitHub.
    echo.
    echo Next steps:
    echo 1. Make changes to files
    echo 2. Run: git add .
    echo 3. Run: git commit -m "your message"
    echo 4. Run: git push
    echo.
) else (
    echo.
    echo ========================================
    echo       WARNING: ISSUES FOUND
    echo ========================================
    echo.
    echo Some Git components need configuration.
    echo Follow the instructions above to fix issues.
    echo.
)

goto end

:error
echo.
echo ========================================
echo         CONFIGURATION NEEDED
echo ========================================
echo.
echo Follow the error messages above to fix issues.
echo.

:end
echo.
echo Available tools:
echo - git_setup.bat (configure Git user)
echo - git_init_simple.bat (initialize repository)
echo - github_publish_simple.bat (publish to GitHub)
echo - git_status_simple.bat (check status)
echo - GIT_QUICK_START.txt (instructions)
echo.
pause
