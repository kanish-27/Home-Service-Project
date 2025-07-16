#!/usr/bin/env python3
"""
Quick setup script to create admin user and sample services
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from services.models import Service, ServiceCategory
from users.models import User

def quick_setup():
    print("🚀 Quick Setup for Admin Services Interface...")
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        email='admin@homeservice.com',
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'user_type': 'admin',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )
    
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Created admin user: {admin_user.email}")
    else:
        # Update existing user to ensure it has admin privileges
        admin_user.user_type = 'admin'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Updated admin user: {admin_user.email}")
    
    # Clean up any existing data to avoid conflicts
    try:
        Service.objects.all().delete()
        ServiceCategory.objects.all().delete()
        print("✅ Cleaned up existing data")
    except:
        print("⚠️ Could not clean up existing data (this is okay)")
    
    # Create categories
    categories = []
    category_names = ['Plumbing', 'Electrical', 'Cleaning', 'Painting', 'AC Service']
    
    for name in category_names:
        category = ServiceCategory.objects.create(
            name=name,
            slug=name.lower().replace(' ', '-'),
            description=f'{name} services for your home'
        )
        categories.append(category)
        print(f"✅ Created category: {category.name}")
    
    # Create sample services
    services_data = [
        ('Basic Plumbing Repair', categories[0], 500, 'Fix leaks and basic plumbing issues'),
        ('Electrical Installation', categories[1], 800, 'Install switches, outlets, and basic electrical work'),
        ('Deep House Cleaning', categories[2], 1200, 'Complete deep cleaning of your home'),
        ('Interior Wall Painting', categories[3], 2000, 'Professional interior wall painting service'),
        ('AC Repair & Service', categories[4], 600, 'Air conditioning repair and maintenance'),
    ]
    
    for name, category, price, description in services_data:
        service = Service.objects.create(
            name=name,
            description=description,
            price=price,
            category=category,
            provider=admin_user,
            duration=2,
            is_available=True,
            is_active=True
        )
        print(f"✅ Created service: {service.name} - ₹{service.price}")
    
    print(f"\n🎉 Quick setup complete!")
    print(f"📊 Total Services: {Service.objects.count()}")
    print(f"📊 Total Categories: {ServiceCategory.objects.count()}")
    print(f"\n🔗 Admin Login Credentials:")
    print(f"📧 Email: admin@homeservice.com")
    print(f"🔑 Password: admin123")
    print(f"\n🔗 URLs:")
    print(f"🔗 Login: http://127.0.0.1:8001/accounts/login/")
    print(f"🔗 Admin Services: http://127.0.0.1:8001/services/admin-services/")
    print(f"\n📝 Instructions:")
    print(f"1. Login with the credentials above")
    print(f"2. Navigate to the admin services URL")
    print(f"3. You should see 5 sample services")
    print(f"4. Try editing, deleting, or adding new services")

if __name__ == '__main__':
    quick_setup()
