@echo off
cd /d C:\srv\kava\app\kavapro
set DJANGO_SETTINGS_MODULE=kavapro.settings
set PYTHONPATH=C:\srv\kava\app\kavapro
python manage.py runserver 0.0.0.0:8080
