# Скрипт для прямого запуску Django CRM в Windows
# Без віртуального середовища

# Встановлюємо змінні середовища
$env:DJANGO_SETTINGS_MODULE = "kavapro.settings"
$env:PYTHONPATH = "C:\srv\kava\app\kavapro"

# Переходимо в папку проекту
Set-Location "C:\srv\kava\app\kavapro"

# Запускаємо Django сервер
Write-Host "Запускаємо Django CRM на порту 8080..." -ForegroundColor Green
Write-Host "Натисніть Ctrl+C для зупинки" -ForegroundColor Yellow

try {
    python manage.py runserver 0.0.0.0:8080 --noreload
} catch {
    Write-Host "Помилка запуску Django: $_" -ForegroundColor Red
    Write-Host "Перевірте, чи встановлений Django: pip install django" -ForegroundColor Yellow
}
