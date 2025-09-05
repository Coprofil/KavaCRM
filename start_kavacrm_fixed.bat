@echo off
cd /d C:\srv\kava\app\kavapro
wsl -e bash -lc "cd /mnt/c/srv/kava/app/kavapro && source .venv/bin/activate && PYTHONUNBUFFERED=1 python manage.py runserver 0.0.0.0:8000 --noreload --insecure --skip-checks --verbosity=0"
