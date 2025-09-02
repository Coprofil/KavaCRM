# Скрипт для запуску Django CRM безпосередньо в Windows
# Це альтернатива WSL для NSSM служби

# Встановлюємо змінні середовища
$env:DJANGO_SETTINGS_MODULE = "kavapro.settings"
$env:PYTHONPATH = "C:\srv\kava\app\kavapro"

# Переходимо в папку проекту
Set-Location "C:\srv\kava\app\kavapro"

# Активуємо віртуальне середовище (якщо є)
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
}

# Запускаємо Django сервер
Write-Host "Запускаємо Django CRM на порту 8080..." -ForegroundColor Green
python manage.py runserver 0.0.0.0:8080 --noreload
