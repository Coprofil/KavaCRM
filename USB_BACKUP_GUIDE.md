# 💾 USB БЕКАП KAVACRM - ПОВНИЙ ПОСІБНИК

## 🚀 ШВИДКИЙ СТАРТ

### 1. Повне налаштування системи
```cmd
setup_usb_backup_windows.bat
```
**Що робить:**
- Створює директорії та конфігурацію
- Налаштовує планувальник завдань (04:00 щодня)
- Створює всі необхідні скрипти
- Налаштовує моніторинг

### 2. Тестування системи
```cmd
test_backup_system.bat
```
**Що тестує:**
- Створення бекапів
- Копіювання на USB
- Систему моніторингу
- Ротацію файлів

### 3. Ручне створення бекапу
```cmd
backup_now.bat
```
**Що створює:**
- Бекап бази даних
- Бекап медіа файлів
- Бекап статичних файлів
- Копіювання на USB
- Очистку старих бекапів

## 📁 СТРУКТУРА ФАЙЛІВ

```
backups/
├── backup_config.ini          # Конфігурація системи
├── backup_now.bat             # Ручний бекап
├── logs/                      # Логи системи
│   ├── backup_monitor_20241201.log
│   └── ...
├── temp/                      # Тимчасові файли
├── kavacrm_db_20241201_0400.sql.gz     # Бекап БД
├── kavacrm_media_20241201_0400.zip     # Бекап медіа
├── kavacrm_static_20241201_0400.zip    # Бекап статичних файлів
├── backup_report_20241201.txt          # Звіти
└── daily_report_20241201.txt           # Денні звіти
```

## ⚙️ КОНФІГУРАЦІЯ

### Основні налаштування (backup_config.ini)
```ini
[BACKUP]
backup_dir=backups                    # Директорія для бекапів
usb_drive_label=KAVA_BACKUP          # Лейбл USB диска
usb_backup_dir=kavacrm_backups       # Директорія на USB
retention_days=30                    # Днів зберігання
compression_level=6                  # Рівень стиснення

[SCHEDULE]
daily_time=04:00                     # Час щоденного бекапу
weekly_day=Sunday                    # День тижневого бекапу
monthly_day=1                        # День місячного бекапу

[NOTIFICATIONS]
telegram_enabled=false               # Telegram сповіщення
telegram_bot_token=                  # Токен бота
telegram_chat_id=                    # ID чату
email_enabled=false                  # Email сповіщення
email_recipient=                     # Одержувач email
```

### Налаштування USB диска

#### Підготовка USB диска:
1. **Вставте USB диск**
2. **Відформатуйте в NTFS** (або FAT32 для сумісності)
3. **Змініть лейбл на "KAVA_BACKUP"**
   ```cmd
   # В командному рядку
   label E: KAVA_BACKUP
   ```
4. **Створіть директорію kavacrm_backups**

#### Перевірка USB диска:
```cmd
backups\check_usb.bat
```

## 📋 КОМАНДИ УПРАВЛІННЯ

### Основні команди
```cmd
# Повний бекап зараз
backup_now.bat

# Перевірка статусу
backup_status.bat

# Очистка старих бекапів
backups\cleanup_backups.bat

# Створення звіту
backups\create_backup_report.bat
```

### Моніторинг та діагностика
```cmd
# Перевірка статусу системи
python backup_monitor.py check

# Створення денного звіту
python backup_monitor.py report

# Детальна інформація про статус
python backup_monitor.py status

# Надсилання сповіщень
python backup_monitor.py notify
```

### USB управління
```cmd
# Пошук USB диска
backups\find_usb_drive.bat

# Копіювання на USB
backups\copy_to_usb.bat

# Перевірка USB
backups\check_usb.bat
```

## ⏰ ПЛАНУВАЛЬНИК ЗАВДАНЬ

### Автоматичний запуск о 04:00
Система автоматично налаштовує планувальник завдань Windows для щоденного бекапу о 04:00.

#### Перевірка планувальника:
```cmd
schtasks /query /tn "KavaCRM Daily Backup"
```

#### Ручне налаштування планувальника:
```cmd
backups\setup_task_scheduler.bat
```

#### Зміна часу бекапу:
1. Відредагуйте `backups\backup_config.ini`
2. Змініть `daily_time=04:00` на бажаний час
3. Перезавантажте планувальник:
   ```cmd
   backups\setup_task_scheduler.bat
   ```

## 📊 МОНІТОРИНГ ТА СПОВІЩЕННЯ

### Telegram сповіщення
1. **Створіть бота** в [@BotFather](https://t.me/botfather)
2. **Отримайте токен** бота
3. **Додайте бота до каналу** та зробіть адміністратором
4. **Отримайте Chat ID** каналу
5. **Налаштуйте конфігурацію:**
   ```ini
   [NOTIFICATIONS]
   telegram_enabled=true
   telegram_bot_token=YOUR_BOT_TOKEN
   telegram_chat_id=YOUR_CHAT_ID
   ```

### Email сповіщення
1. **Налаштуйте SMTP** в Django settings
2. **Вкажіть одержувача:**
   ```ini
   [NOTIFICATIONS]
   email_enabled=true
   email_recipient=admin@yourdomain.com
   ```

### Логи системи
```
backups/logs/
├── backup_monitor_20241201.log    # Логи моніторингу
├── django_backup_20241201.log     # Логи Django бекапу
└── usb_backup_20241201.log        # Логи USB операцій
```

## 🔄 РОТАЦІЯ БЕКАПІВ

### Автоматична ротація
- **Локальні бекапи:** видаляються після 30 днів
- **USB бекапи:** видаляються після 30 днів
- **Логи:** видаляються після 90 днів

### Ручна очистка
```cmd
backups\cleanup_backups.bat
```

### Зміна періоду зберігання
1. Відредагуйте `backups\backup_config.ini`
2. Змініть `retention_days=30` на бажане значення
3. Система застосує зміни автоматично

## 📈 СТАТИСТИКА ТА ЗВІТИ

### Денні звіти
Створюються автоматично та містять:
- Статистику бекапів
- Інформацію про USB
- Використання місця на диску
- Рекомендації та попередження

### Перегляд звітів
```cmd
# Останній денний звіт
type backups\daily_report_*.txt | more

# Останній звіт бекапу
type backups\backup_report_*.txt | more
```

### Статистика використання місця
```cmd
# Розмір директорії бекапів
du -sh backups/

# Найбільші файли
find backups/ -type f -exec ls -lh {} \; | sort -k5 -hr | head -10
```

## 🔧 ДІАГНОСТИКА ПРОБЛЕМ

### Бекап не створюється
```cmd
# Перевірка Python та Django
python --version
python -c "import django; print(django.VERSION)"

# Перевірка бази даних
python manage.py dbshell --help

# Перевірка місця на диску
dir C: | find "bytes free"
```

### USB диск не знаходиться
```cmd
# Перевірка підключених дисків
wmic logicaldisk get name,volumename

# Зміна лейблу диска
label E: KAVA_BACKUP

# Перевірка доступу
backups\check_usb.bat
```

### Планувальник не працює
```cmd
# Перевірка статусу
schtasks /query /tn "KavaCRM Daily Backup"

# Перестворення завдання
backups\setup_task_scheduler.bat

# Перевірка логів Windows
eventvwr.msc
```

### Помилки стиснення
```cmd
# Перевірка місця в temp
dir %TEMP%

# Зміна рівня стиснення
# Відредагуйте backup_config.ini
compression_level=1  # Мінімальне стиснення
```

## 🚀 ПРОДАКШН РОЗГОРТАННЯ

### На сервері Linux
```bash
# Копіювання конфігурації
scp backups/backup_config.ini user@server:/path/to/config/

# Налаштування cron
echo "0 4 * * * /path/to/backup_script.sh" | crontab -

# Налаштування моніторингу
# Додайте до cron:
# */30 * * * * /path/to/backup_monitor.py check
```

### Інтеграція з Django
```python
# В settings.py додайте:
BACKUP_CONFIG = {
    'BACKUP_DIR': '/var/backups/kavacrm',
    'USB_MOUNT': '/mnt/usb',
    'RETENTION_DAYS': 30,
    'NOTIFICATIONS': {
        'TELEGRAM': True,
        'EMAIL': True,
    }
}
```

## 📋 ЧЕК-ЛИСТ ПЕРЕВІРКИ

### Щоденна перевірка
- [ ] Бекап створений о 04:00
- [ ] Файли скопійовано на USB
- [ ] Немає помилок в логах
- [ ] Місце на диску достатнє

### Тижнева перевірка
- [ ] Ротація працює коректно
- [ ] USB диск доступний
- [ ] Сповіщення надсилаються
- [ ] Звіти створюються

### Місячна перевірка
- [ ] Перевірити відновлення з бекапу
- [ ] Очистити старі логи
- [ ] Оновити конфігурацію якщо потрібно

## 🆘 ШВИДКА ДОПОМОГА

### Найпоширеніші проблеми

#### 1. "USB диск не знайдено"
```
Рішення:
1. Перевірте чи вставлений USB диск
2. Змініть лейбл: label E: KAVA_BACKUP
3. Перевірте форматування (NTFS/FAT32)
```

#### 2. "Недостатньо місця"
```
Рішення:
1. Очистити старі бекапи: cleanup_backups.bat
2. Зменшити retention_days в конфігурації
3. Звільнити місце на диску
```

#### 3. "Бекап не створюється"
```
Рішення:
1. Перевірити Python: python --version
2. Перевірити Django: python manage.py check
3. Перевірити базу даних: python manage.py dbshell
```

#### 4. "Планувальник не працює"
```
Рішення:
1. Перевірити права адміністратора
2. Перезавантажити планувальник
3. Перестворити завдання
```

## 🎯 РЕЗЮМЕ

**USB бекап система KavaCRM включає:**

✅ **Автоматичне створення бекапів** о 04:00 щодня
✅ **Ротація файлів** з налаштовуваним періодом
✅ **USB підтримка** з автоматичним копіюванням
✅ **Моніторинг та сповіщення** через Telegram та email
✅ **Детальні звіти** про стан системи
✅ **Windows інтеграція** через планувальник завдань
✅ **Стиснення файлів** для економії місця
✅ **Висока надійність** з перевірками та логуванням

**Для початку роботи:**
```cmd
setup_usb_backup_windows.bat
test_backup_system.bat
backup_now.bat
```

Система готова до використання! 💾✨
