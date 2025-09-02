@echo off
echo ========================================
echo      WORK PROGRESS TRACKER
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul

echo Current session: %date% %time%
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
    pause
    exit /b 1
)

echo Repository found.
echo.

echo TODAY'S PROGRESS:
echo =================

REM Show today's commits
echo Your commits today:
git log --oneline --since="1 day ago" --author="$(git config user.name)"
echo.

REM Show today's changes
echo Files changed today:
git log --name-only --since="1 day ago" --author="$(git config user.name)" | grep -v "^$" | sort | uniq
echo.

REM Show current status
echo CURRENT WORK STATUS:
echo ===================
git status --porcelain
echo.

REM Count current changes
for /f %%i in ('git status --porcelain ^| find /c "M"') do set MODIFIED=%%i
for /f %%i in ('git status --porcelain ^| find /c "A"') do set ADDED=%%i
for /f %%i in ('git status --porcelain ^| find /c "??"') do set UNTRACKED=%%i

echo Modified files: %MODIFIED%
echo Added files: %ADDED%
echo Untracked files: %UNTRACKED%
echo.

REM Show recent activity
echo RECENT ACTIVITY:
echo ================
git log --oneline -5
echo.

REM Show branch status
echo BRANCH STATUS:
echo ==============
git status -b
echo.

echo ========================================
echo         PROGRESS SUMMARY
echo ========================================
echo.

REM Today's commit count
for /f %%i in ('git log --oneline --since="1 day ago" --author="$(git config user.name)" ^| find /c " "') do set TODAY_COMMITS=%%i
echo Today's commits: %TODAY_COMMITS%

REM This week's commit count
for /f %%i in ('git log --oneline --since="1 week ago" --author="$(git config user.name)" ^| find /c " "') do set WEEK_COMMITS=%%i
echo This week's commits: %WEEK_COMMITS%

REM Total project commits
for /f %%i in ('git log --oneline --all ^| find /c " "') do set TOTAL_COMMITS=%%i
echo Total project commits: %TOTAL_COMMITS%

echo.

if %MODIFIED% gtr 0 (
    echo ⚠️  You have unsaved changes!
    echo Run: git_daily_sync.bat
    echo.
)

echo TIPS FOR TODAY:
echo ===============
echo • Work on your planned tasks
echo • Commit regularly with clear messages
echo • Push to GitHub at end of day
echo • Review your progress weekly
echo.
echo Quick sync: git_daily_sync.bat
echo Full backup: backup_and_sync.bat
echo.

pause
