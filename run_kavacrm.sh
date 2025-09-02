#!/usr/bin/env bash
set -e
cd /mnt/c/srv/kava/app/kavapro
source .venv/bin/activate
exec python manage.py runserver 0.0.0.0:8080 --noreload
