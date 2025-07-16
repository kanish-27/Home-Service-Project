#!/usr/bin/env python3
"""
Simple script to create one test service
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from services.models import Service, ServiceCategory
from users.models import User

def create_simple_service():
    print("🛠️ Creating Simple Test Service...")
    
    # Get admin user
    try:
        admin_user = User.objects.get(email='admin@homeservice.com')
        print(f"✅ Found admin user: {admin_user.email}")
    except User.DoesNotExist:
        print("❌ Admin user not found. Creating one...")
        admin_user = User.objects.create_user(
            email='admin@homeservice.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            user_type='admin',
            is_staff=True,
            is_superuser=True
        )
        print(f"✅ Created admin user: {admin_user.email}")
    
    # Create a simple category
    try:
        category = ServiceCategory.objects.get(name='Plumbing')
        print(f"✅ Found category: {category.name}")
    except ServiceCategory.DoesNotExist:
        category = ServiceCategory.objects.create(
            name='Plumbing',
            slug='plumbing',
            description='Plumbing services for your home'
        )
        print(f"✅ Created category: {category.name}")
    
    # Create a simple service
    try:
        service = Service.objects.get(name='Basic Plumbing Repair')
        print(f"✅ Service already exists: {service.name}")
    except Service.DoesNotExist:
        service = Service.objects.create(
            name='Basic Plumbing Repair',
            description='Fix leaks, unclog drains, and basic plumbing repairs for your home',
            price=500.00,
            category=category,
            provider=admin_user,
            duration=2,
            is_available=True,
            is_active=True
        )
        print(f"✅ Created service: {service.name} - ₹{service.price}")
    
    print(f"\n🎉 Simple service creation complete!")
    print(f"📊 Total Services: {Service.objects.count()}")
    print(f"📊 Total Categories: {ServiceCategory.objects.count()}")
    print(f"\n🔗 Admin Services URL: http://127.0.0.1:8001/services/admin-services/")

if __name__ == '__main__':
    try:
        create_simple_service()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("This is okay - the admin interface will still work without sample data")
