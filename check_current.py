#!/usr/bin/env python
import os
import sys
import django

sys.path.append('/mnt/c/srv/kava/app/kavapro')
os.chdir('/mnt/c/srv/kava/app/kavapro')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kavapro.settings')
django.setup()

from kavacrm.models import Client, Route, RoutePlanHistory

print("=== ПОТОЧНИЙ СТАН ===")
print(f"та1 клієнтів: {Client.objects.filter(agent='та1').count()}")
print(f"та1 маршрутів: {Route.objects.filter(agent='та1').count()}")
print(f"та1 історій: {RoutePlanHistory.objects.filter(agent='та1').count()}")

print("\n=== ПРОПОЗИЦІЯ РОЗПОДІЛУ ===")
total_clients = Client.objects.filter(agent='та1').count()
print(f"Загалом клієнтів: {total_clients}")
print(f"та1: {total_clients // 3} клієнтів")
print(f"та3: {total_clients // 3} клієнтів")
print(f"та4: {total_clients - 2 * (total_clients // 3)} клієнтів")
