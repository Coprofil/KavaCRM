#!/usr/bin/env python
import os
import sys
import django

# Додаємо шлях до проекту
sys.path.append('/mnt/c/srv/kava/app/kavapro')
os.chdir('/mnt/c/srv/kava/app/kavapro')

# Налаштовуємо Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kavapro.settings')
django.setup()

from kavacrm.models import Client, Route, RoutePlanHistory, Unloading

print("Перевірка залишків агентів ТА4:")
print("Клієнти:", list(Client.objects.filter(agent='ТА4').values_list('name', flat=True)))
print("Маршрути:", Route.objects.filter(agent='ТА4').count())
print("Історії маршрутів:", RoutePlanHistory.objects.filter(agent='ТА4').count())
print("Відвантаження:", Unloading.objects.filter(agent='ТА4').count())

print("\n=== ПЕРЕВІРКА СТАНУ АГЕНТІВ ===")
print("та1 (робочий):", Client.objects.filter(agent='та1').count(), "клієнтів")
print("та3 (робочий):", Client.objects.filter(agent='та3').count(), "клієнтів")
print("та4 (робочий):", Client.objects.filter(agent='та4').count(), "клієнтів")
print("ТА1 (робочий):", Client.objects.filter(agent='ТА1').count(), "клієнтів")
print("ТА3 (не робочий):", Client.objects.filter(agent='ТА3').count(), "клієнтів")
print("ТА4 (не робочий):", Client.objects.filter(agent='ТА4').count(), "клієнтів")

print("\n=== ПОТРІБНО ВИПРАВИТИ ===")
print("та3 має бути відновлено з та1")
print("та4 має бути відновлено з та1")

print("\n=== ЗАГАЛЬНА СТАТИСТИКА АГЕНТІВ ===")

# Всі агенти
all_clients = Client.objects.exclude(agent__isnull=True).exclude(agent='').values_list('agent', flat=True)
all_routes = Route.objects.exclude(agent__isnull=True).exclude(agent='').values_list('agent', flat=True)
all_histories = RoutePlanHistory.objects.exclude(agent__isnull=True).exclude(agent='').values_list('agent', flat=True)
all_unloadings = Unloading.objects.exclude(agent__isnull=True).exclude(agent='').values_list('agent', flat=True)

all_agents = set(list(all_clients) + list(all_routes) + list(all_histories) + list(all_unloadings))
print("Усі агенти в системі:", sorted(all_agents))

print("\nСтатистика по кожному агенту:")
for agent in sorted(all_agents):
    client_count = Client.objects.filter(agent=agent).count()
    route_count = Route.objects.filter(agent=agent).count()
    history_count = RoutePlanHistory.objects.filter(agent=agent).count()
    unloading_count = Unloading.objects.filter(agent=agent).count()

    print(f"  {agent}: {client_count} клієнтів, {route_count} маршрутів, {history_count} історій, {unloading_count} відвантажень")
