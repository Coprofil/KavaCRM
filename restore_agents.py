#!/usr/bin/env python
import os
import sys
import django
from random import choice

# Налаштування Django
sys.path.append('/mnt/c/srv/kava/app/kavapro')
os.chdir('/mnt/c/srv/kava/app/kavapro')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kavapro.settings')
django.setup()

from kavacrm.models import Client, Route, RoutePlanHistory, Unloading

def restore_agents():
    print("=== ВІДНОВЛЕННЯ АГЕНТІВ ===")
    print("Робочі агенти: та1, та3, та4")
    print("Не робочі агенти: ТА3, ТА4 (вже видалені)")
    print()

    # Отримуємо всіх клієнтів поточного агента та1
    clients = list(Client.objects.filter(agent='та1'))
    routes = list(Route.objects.filter(agent='та1'))
    histories = list(RoutePlanHistory.objects.filter(agent='та1'))

    print(f"Знайдено: {len(clients)} клієнтів, {len(routes)} маршрутів, {len(histories)} історій")

    if not clients:
        print("Немає даних для відновлення")
        return

    # Розподіляємо клієнтів між трьома агентами
    agents = ['та1', 'та3', 'та4']
    client_count = len(clients)
    routes_count = len(routes)
    histories_count = len(histories)

    print(f"\nРозподіл клієнтів між агентами {agents}:")
    print(f"  та1: {client_count // 3} клієнтів")
    print(f"  та3: {client_count // 3} клієнтів")
    print(f"  та4: {client_count - 2 * (client_count // 3)} клієнтів")

    # Розподіляємо клієнтів
    for i, client in enumerate(clients):
        new_agent = agents[i % 3]
        if new_agent != 'та1':  # та1 залишається
            client.agent = new_agent
            print(f"  {client.name}: та1 → {new_agent}")

    # Розподіляємо маршрути
    for i, route in enumerate(routes):
        new_agent = agents[i % 3]
        if new_agent != 'та1':
            route.agent = new_agent

    # Розподіляємо історії
    for i, history in enumerate(histories):
        new_agent = agents[i % 3]
        if new_agent != 'та1':
            history.agent = new_agent

    # Зберігаємо зміни
    print("\nЗбереження змін...")
    for client in clients:
        if client.agent != 'та1':
            client.save()

    for route in routes:
        if route.agent != 'та1':
            route.save()

    for history in histories:
        if history.agent != 'та1':
            history.save()

    print("✅ Відновлення завершено!")

if __name__ == '__main__':
    restore_agents()
