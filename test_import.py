#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kavapro.settings')
django.setup()

try:
    from kavacrm.views import add_phone
    print("add_phone imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Other error: {e}")
