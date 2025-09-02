"""
URL configuration for kavapro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

# Зміна шляху адмінки для безпеки
admin.site.site_header = "KavaCRM Адміністрація"
admin.site.site_title = "KavaCRM"
admin.site.index_title = "Панель управління"

urlpatterns = [
    # 2FA URLs (опційно, якщо встановлено two_factor)
    # Якщо пакету немає — пропускаємо
]

try:
    urlpatterns += [path('', include('two_factor.urls', 'two_factor'))]
except Exception:
    pass

# Безпечний шлях адмінки (змініть на унікальний)
urlpatterns += [
    path('secure-admin-panel-2024/', admin.site.urls),
    path('', include('kavacrm.urls')),
]

# Додаткові URL для продакшн
if not settings.DEBUG:
    try:
        urlpatterns += [path('health/', include('health_check.urls'))]
    except Exception:
        pass
