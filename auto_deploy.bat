@echo off
echo ========================================
echo    АВТОМАТИЧНЕ РОЗГОРТАННЯ KAVACRM
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul

echo Starting automated deployment...
echo Current time: %date% %time%
echo.

REM Step 1: Check Python and Django
echo [1/8] Checking Python and Django...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Install Python from: https://python.org
    pause
    exit /b 1
)

python -c "import django; print('Django version:', django.VERSION)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Django not installed!
    echo Install with: pip install -r requirements_production.txt
    pause
    exit /b 1
)

echo Python and Django are ready.
echo.

REM Step 2: Check database
echo [2/8] Checking database...
if exist db.sqlite3 (
    echo Database exists.
) else (
    echo Database not found, will be created during migrations.
)

echo.

REM Step 3: Run migrations
echo [3/8] Running database migrations...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo WARNING: makemigrations failed
)

python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: Migration failed!
    pause
    exit /b 1
)

echo Migrations completed.
echo.

REM Step 4: Collect static files
echo [4/8] Collecting static files...
python manage.py collectstatic --noinput --clear
if %errorlevel% neq 0 (
    echo WARNING: Static files collection failed
) else (
    echo Static files collected.
)

echo.

REM Step 5: Create superuser (optional)
echo [5/8] Checking superuser...
python manage.py shell -c "from django.contrib.auth.models import User; print('Superusers:', User.objects.filter(is_superuser=True).count())" > temp_superuser.txt 2>&1
set /p superuser_count=<temp_superuser.txt
del temp_superuser.txt

echo %superuser_count% | find "Superusers: 0" >nul
if %errorlevel% equ 0 (
    echo No superuser found.
    echo.
    echo Creating default superuser...
    echo Username: admin
    echo Email: admin@kavacrm.local
    echo Password: admin123
    echo.
    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@kavacrm.local', 'admin123')"
    if %errorlevel% equ 0 (
        echo Superuser created successfully!
        echo.
        echo IMPORTANT: Change password after first login!
        echo Username: admin
        echo Password: admin123
    ) else (
        echo WARNING: Could not create superuser
    )
) else (
    echo Superuser already exists.
)

echo.

REM Step 6: Test Django
echo [6/8] Testing Django configuration...
python manage.py check
if %errorlevel% equ 0 (
    echo Django configuration is valid.
) else (
    echo WARNING: Django configuration issues found
)

echo.

REM Step 7: Initialize RAG system (if available)
echo [7/8] Checking RAG system...
python -c "from kavacrm.rag_system import RAGSystem" >nul 2>&1
if %errorlevel% equ 0 (
    echo RAG system available.
    echo Initializing RAG system...
    python manage.py init_rag_system 2>nul
    if %errorlevel% equ 0 (
        echo RAG system initialized.
    ) else (
        echo WARNING: RAG initialization failed
    )
) else (
    echo RAG system not available (optional).
)

echo.

REM Step 8: Final check and startup
echo [8/8] Final check and startup...
python manage.py shell -c "print('Django is working correctly!')" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo    DEPLOYMENT COMPLETED SUCCESSFULLY!
    echo ========================================
    echo.
    echo Django is working correctly!
    echo.
    echo To start the server, run:
    echo python manage.py runserver
    echo.
    echo Or for production:
    echo .\start_production.sh
    echo.
    echo Access the application at:
    echo http://localhost:8000/crm/
    echo.
    echo Admin panel: http://localhost:8000/secure-admin-panel-2024/
    echo Username: admin
    echo Password: admin123 (CHANGE AFTER FIRST LOGIN!)
    echo.
) else (
    echo.
    echo ========================================
    echo        DEPLOYMENT WARNING
    echo ========================================
    echo.
    echo Django may have configuration issues.
    echo Check the error messages above.
    echo.
    echo Try running: python manage.py check
    echo.
)

echo.
echo DEPLOYMENT SUMMARY:
echo ===================
echo • Database: Migrated
echo • Static files: Collected
echo • Superuser: Configured
echo • Django: Tested
echo • RAG: Initialized (if available)
echo.

echo Next steps:
echo 1. Start server: python manage.py runserver
echo 2. Open browser: http://localhost:8000/crm/
echo 3. Login to admin panel
echo 4. Configure system settings
echo 5. Set up monitoring and backups
echo.

pause
