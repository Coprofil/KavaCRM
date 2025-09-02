@echo off
echo ========================================
echo      FIX GIT COMMIT ISSUE
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
    pause
    exit /b 1
)

echo Git is installed.
echo.

REM Check current Git user configuration
echo Checking current Git configuration...
echo Current user name:
git config user.name
echo Current user email:
git config user.email
echo.

REM If user name is empty, configure it
for /f %%i in ('git config user.name') do set GIT_USER=%%i
if "%GIT_USER%"=="" (
    echo User name is empty, configuring...
    echo Enter your name:
    set /p user_name=
    git config user.name "%user_name%"
    echo User name configured: %user_name%
) else (
    echo User name is configured: %GIT_USER%
)

REM If user email is empty, configure it
for /f %%i in ('git config user.email') do set GIT_EMAIL=%%i
if "%GIT_EMAIL%"=="" (
    echo User email is empty, configuring...
    echo Enter your email:
    set /p user_email=
    git config user.email "%user_email%"
    echo User email configured: %user_email%
) else (
    echo User email is configured: %GIT_EMAIL%
)

echo.

REM Verify configuration
echo Verifying Git configuration...
git config user.name
git config user.email
echo.

REM Check repository status
echo Checking repository status...
git status --porcelain
echo.

REM Create commit with simple message
echo Creating commit with simple message...
git commit -m "Initial KavaCRM commit"
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo      COMMIT CREATED SUCCESSFULLY!
    echo ========================================
    echo.
    echo Git commit created successfully!
    echo.
    echo Repository status:
    git status
    echo.
    echo Last commit:
    git log --oneline -1
    echo.
    echo You can now push to GitHub using:
    echo github_publish_simple.bat
    echo.
) else (
    echo.
    echo ========================================
    echo        COMMIT FAILED
    echo ========================================
    echo.
    echo Trying alternative approach...
    echo.

    REM Try with different message format
    git commit -m "Initial commit"
    if %errorlevel% equ 0 (
        echo Commit created with alternative message!
    ) else (
        echo Still failed. Trying to reset and commit again...
        echo.

        REM Reset staging area and try again
        git reset
        git add .
        git commit -m "Initial commit"
        if %errorlevel% equ 0 (
            echo Commit created after reset!
        ) else (
            echo ERROR: Cannot create commit
            echo.
            echo Possible solutions:
            echo 1. Check your user name and email again
            echo 2. Try: git config --global user.name "Your Name"
            echo 3. Try: git config --global user.email "your@email.com"
            echo 4. Make sure Git is properly installed
            echo.
            git status
        )
    )
)

echo.
pause
