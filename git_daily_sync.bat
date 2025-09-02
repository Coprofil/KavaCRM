@echo off
echo ========================================
echo       DAILY GIT SYNC
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
    echo Install from: https://git-scm.com/download/win
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

REM Show current status
echo CURRENT STATUS:
echo ===============
git status --porcelain
echo.

REM Count changes
for /f %%i in ('git status --porcelain ^| find /c "M"') do set MODIFIED=%%i
for /f %%i in ('git status --porcelain ^| find /c "A"') do set ADDED=%%i
for /f %%i in ('git status --porcelain ^| find /c "??"') do set UNTRACKED=%%i

echo Modified files: %MODIFIED%
echo Added files: %ADDED%
echo Untracked files: %UNTRACKED%
echo.

REM Check if there are changes
set /a TOTAL_CHANGES=%MODIFIED%+%ADDED%+%UNTRACKED%

if %TOTAL_CHANGES% equ 0 (
    echo No changes to commit.
    echo.
    echo Checking if we need to push...
    git status -b
    echo.
    echo If you want to push anyway, run: git push
    goto end
)

echo CHANGES FOUND: %TOTAL_CHANGES% files
echo ================================
echo.

REM Show what will be committed
echo Files to be committed:
git status --porcelain
echo.

REM Ask for commit message
echo Enter commit message (or press Enter for default):
set /p commit_msg=

if "%commit_msg%"=="" (
    set commit_msg=Daily update - %date%
    echo Using default message: %commit_msg%
) else (
    echo Using message: %commit_msg%
)

echo.

REM Add all changes
echo Adding changes...
git add .

REM Create commit
echo Creating commit...
git commit -m "%commit_msg%"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo      COMMIT CREATED SUCCESSFULLY!
    echo ========================================
    echo.
    git log --oneline -1
    echo.

    REM Check if remote exists
    git remote get-url origin >nul 2>&1
    if %errorlevel% equ 0 (
        echo Pushing to GitHub...
        git push origin master
        if %errorlevel% equ 0 (
            echo.
            echo ========================================
            echo    SUCCESS: PUSHED TO GITHUB!
            echo ========================================
            echo.
            echo Your changes are now on GitHub!
            echo.
        ) else (
            echo.
            echo WARNING: Push failed
            echo You can try manually: git push origin master
            echo.
        )
    ) else (
        echo.
        echo WARNING: No remote repository configured
        echo To set up GitHub, run: github_publish_simple.bat
        echo.
    )

    REM Show final status
    echo FINAL STATUS:
    echo =============
    git status -b
    echo.

) else (
    echo.
    echo ========================================
    echo        COMMIT FAILED
    echo ========================================
    echo.
    echo Check the error messages above.
    echo You can try to commit manually:
    echo git add .
    echo git commit -m "Your message"
    echo.
    git status
)

:end
echo.
echo ========================================
echo         DAILY SYNC COMPLETE
echo ========================================
echo.
echo Next time you work on the project:
echo 1. Make your changes
echo 2. Run: git_daily_sync.bat
echo 3. Your work is safely stored on GitHub!
echo.
pause
