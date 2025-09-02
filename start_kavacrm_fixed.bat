@echo off
cd /d C:\srv\kava\app\kavapro
wsl -e bash -lc "cd /mnt/c/srv/kava/app/kavapro && source .venv/bin/activate && python manage.py runserver 127.0.0.1:8080 --noreload --insecure"
