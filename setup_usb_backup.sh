#!/bin/bash

# Скрипт для налаштування USB бекапів

set -e

USB_MOUNT_POINT="/mnt/usb"
BACKUP_DIR="/var/backups/kavacrm"

echo "💾 Налаштування USB бекапів для KavaCRM"

# Створення точки монтування
echo "📁 Створення точки монтування..."
sudo mkdir -p $USB_MOUNT_POINT

# Створення директорії для бекапів
echo "📂 Створення директорії для бекапів..."
sudo mkdir -p $BACKUP_DIR
sudo chown -R $USER:$USER $BACKUP_DIR

# Створення udev правило для автоматичного монтування USB
echo "🔌 Налаштування автоматичного монтування USB..."
sudo tee /etc/udev/rules.d/99-usb-backup.rules > /dev/null <<EOF
# Автоматичне монтування USB для бекапів
SUBSYSTEM=="block", KERNEL=="sd[b-z][0-9]", ATTRS{idVendor}=="*", ATTRS{idProduct}=="*", RUN+="/usr/local/bin/mount-usb-backup.sh"
EOF

# Створення скрипта монтування
echo "📝 Створення скрипта монтування..."
sudo tee /usr/local/bin/mount-usb-backup.sh > /dev/null <<'EOF'
#!/bin/bash

USB_MOUNT_POINT="/mnt/usb"
BACKUP_DIR="/var/backups/kavacrm"

# Перевіряємо, чи USB вже змонтований
if mountpoint -q $USB_MOUNT_POINT; then
    echo "USB already mounted at $USB_MOUNT_POINT"
    exit 0
fi

# Знаходимо USB пристрій
USB_DEVICE=$(lsblk -o NAME,LABEL | grep -E "(BACKUP|KAVA|USB)" | head -1 | awk '{print "/dev/"$1}')

if [ -z "$USB_DEVICE" ]; then
    # Якщо не знайшли за лейблом, беремо перший USB
    USB_DEVICE=$(lsblk -o NAME,TYPE | grep disk | grep -v sda | head -1 | awk '{print "/dev/"$1}')
fi

if [ -n "$USB_DEVICE" ]; then
    echo "Mounting USB device: $USB_DEVICE"
    
    # Монтуємо USB
    mount $USB_DEVICE $USB_MOUNT_POINT
    
    # Створюємо директорію для бекапів на USB
    mkdir -p $USB_MOUNT_POINT/kavacrm_backups
    
    # Копіюємо останні бекапи
    if [ -d "$BACKUP_DIR" ]; then
        find $BACKUP_DIR -name "kavacrm_*" -mtime -1 -exec cp {} $USB_MOUNT_POINT/kavacrm_backups/ \;
    fi
    
    echo "USB mounted and backups copied"
else
    echo "No USB device found"
fi
EOF

sudo chmod +x /usr/local/bin/mount-usb-backup.sh

# Створення скрипта розмонтування
echo "📝 Створення скрипта розмонтування..."
sudo tee /usr/local/bin/unmount-usb-backup.sh > /dev/null <<'EOF'
#!/bin/bash

USB_MOUNT_POINT="/mnt/usb"

if mountpoint -q $USB_MOUNT_POINT; then
    echo "Unmounting USB from $USB_MOUNT_POINT"
    umount $USB_MOUNT_POINT
    echo "USB unmounted"
else
    echo "USB not mounted at $USB_MOUNT_POINT"
fi
EOF

sudo chmod +x /usr/local/bin/unmount-usb-backup.sh

# Створення systemd сервісу для моніторингу USB
echo "⚙️ Створення systemd сервісу..."
sudo tee /etc/systemd/system/usb-backup-monitor.service > /dev/null <<EOF
[Unit]
Description=USB Backup Monitor
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/local/bin/mount-usb-backup.sh
Restart=always
RestartSec=30
User=root

[Install]
WantedBy=multi-user.target
EOF

# Створення cron завдання для щоденного бекапу
echo "⏰ Налаштування cron завдання..."
(crontab -l 2>/dev/null; echo "0 4 * * * /usr/local/bin/mount-usb-backup.sh") | crontab -

# Перезавантаження udev
echo "🔄 Перезавантаження udev..."
sudo udevadm control --reload-rules
sudo udevadm trigger

# Встановлення необхідних пакетів
echo "📦 Встановлення необхідних пакетів..."
sudo apt update
sudo apt install -y usbutils

echo "✅ USB бекап налаштування завершено!"
echo "💾 USB буде автоматично монтуватися в $USB_MOUNT_POINT"
echo "📁 Бекапи будуть зберігатися в $BACKUP_DIR"
echo "⏰ Щоденний бекап о 04:00"
echo ""
echo "Команди для ручного управління:"
echo "  Монтування: sudo /usr/local/bin/mount-usb-backup.sh"
echo "  Розмонтування: sudo /usr/local/bin/unmount-usb-backup.sh"
