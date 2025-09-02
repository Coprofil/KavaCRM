@echo off
echo ========================================
echo     BACKUP + GIT SYNC
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul

echo Current codepage: UTF-8
echo Backup time: %date% %time%
echo.

REM Create backup directory if it doesn't exist
if not exist backups mkdir backups

echo Creating project backup...
echo ========================

REM Backup database if exists
if exist db.sqlite3 (
    echo Backing up database...
    copy db.sqlite3 "backups\db_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.sqlite3" >nul
    echo Database backup created.
) else (
    echo No database file found.
)

REM Backup media files if exist
if exist media (
    echo Backing up media files...
    if exist "backups\media_backup.zip" del "backups\media_backup.zip"
    powershell "Compress-Archive -Path 'media' -DestinationPath 'backups\media_backup.zip' -Force" 2>nul
    if %errorlevel% equ 0 (
        echo Media files backup created.
    ) else (
        echo WARNING: Could not create media backup
    )
) else (
    echo No media directory found.
)

echo Backup created in backups\ folder.
echo.

REM Now do Git sync
echo STARTING GIT SYNC...
echo ===================

REM Check Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git not installed!
    goto end
)

echo Git is ready.
echo.

REM Check repository
if not exist .git (
    echo ERROR: Not a Git repository!
    goto end
)

echo Repository found.
echo.

REM Show current status
echo Checking for changes...
git status --porcelain > temp_changes.txt
set /p CHANGES=<temp_changes.txt
del temp_changes.txt

if "%CHANGES%"=="" (
    echo No changes to commit.
    echo.
    echo Checking if we need to push...
    goto push_check
)

echo Changes found, adding to Git...
git add .

REM Create commit with backup message
set BACKUP_MSG=Backup and sync - %date% %time%
echo Creating commit: %BACKUP_MSG%
git commit -m "%BACKUP_MSG%"

if %errorlevel% equ 0 (
    echo Commit created successfully!
) else (
    echo ERROR: Failed to create commit
    goto end
)

:push_check
REM Check if remote exists and push
git remote get-url origin >nul 2>&1
if %errorlevel% equ 0 (
    echo Pushing to GitHub...
    git push origin master
    if %errorlevel% equ 0 (
        echo Successfully pushed to GitHub!
    ) else (
        echo WARNING: Push failed
    )
) else (
    echo WARNING: No remote repository configured
    echo To set up GitHub, run: github_publish_simple.bat
)

echo.
echo FINAL STATUS:
echo =============
git status -b
echo.

echo ========================================
echo    BACKUP + SYNC COMPLETE!
echo ========================================
echo.
echo - Project backed up locally
echo - Changes committed to Git
echo - Code pushed to GitHub
echo.
echo Your work is safe! ✅

:end
echo.
pause
