# Скрипт для налаштування NSSM служби KavaCRM
# Запускати від імені адміністратора!

Write-Host "=== Налаштування служби KavaCRM ===" -ForegroundColor Green

# Зупиняємо службу
Write-Host "Зупиняємо службу KavaCRM..." -ForegroundColor Yellow
& "C:\srv\kava\app\kavapro\nssm-2.24\win64\nssm.exe" stop KavaCRM

# Налаштовуємо користувача (поточний користувач)
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
Write-Host "Встановлюємо користувача: $currentUser" -ForegroundColor Yellow
& "C:\srv\kava\app\kavapro\nssm-2.24\win64\nssm.exe" set KavaCRM ObjectName $currentUser

# Перевіряємо налаштування
Write-Host "Перевіряємо налаштування служби..." -ForegroundColor Yellow
& "C:\srv\kava\app\kavapro\nssm-2.24\win64\nssm.exe" dump KavaCRM

# Запускаємо службу
Write-Host "Запускаємо службу KavaCRM..." -ForegroundColor Yellow
& "C:\srv\kava\app\kavapro\nssm-2.24\win64\nssm.exe" start KavaCRM

# Перевіряємо статус
Write-Host "Перевіряємо статус служби..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
sc.exe query KavaCRM

Write-Host "=== Налаштування завершено ===" -ForegroundColor Green
