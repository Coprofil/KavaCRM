#!/usr/bin/env python
import sqlite3

# Підключаємося до резервної копії
conn = sqlite3.connect('db_backup_before_utf8_fix.sqlite3')
cursor = conn.cursor()

print("=== ДАНІ З РЕЗЕРВНОЇ КОПІЇ ===")

# Перевіряємо агентів у клієнтах
cursor.execute("""
    SELECT agent, COUNT(*)
    FROM kavacrm_client
    WHERE agent IN ('та1', 'та3', 'та4', 'ТА1', 'ТА3', 'ТА4')
    GROUP BY agent
    ORDER BY agent
""")

print("\nКлієнти:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} записів")

# Перевіряємо агентів у маршрутах
cursor.execute("""
    SELECT agent, COUNT(*)
    FROM kavacrm_route
    WHERE agent IN ('та1', 'та3', 'та4', 'ТА1', 'ТА3', 'ТА4')
    GROUP BY agent
    ORDER BY agent
""")

print("\nМаршрути:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} записів")

conn.close()

print("\n=== ПОТОЧНА БАЗА ДАНИХ ===")

import os
import sys
import django

sys.path.append('/mnt/c/srv/kava/app/kavapro')
os.chdir('/mnt/c/srv/kava/app/kavapro')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kavapro.settings')
django.setup()

from kavacrm.models import Client, Route

print("\nКлієнти зараз:")
for agent in ['та1', 'та3', 'та4', 'ТА1', 'ТА3', 'ТА4']:
    count = Client.objects.filter(agent=agent).count()
    if count > 0:
        print(f"  {agent}: {count} записів")

print("\nМаршрути зараз:")
for agent in ['та1', 'та3', 'та4', 'ТА1', 'ТА3', 'ТА4']:
    count = Route.objects.filter(agent=agent).count()
    if count > 0:
        print(f"  {agent}: {count} записів")
