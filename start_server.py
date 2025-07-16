#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
    try:
        django.setup()
        print("✅ Django setup successful")
        print("🚀 Starting Django development server...")
        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000'])
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
