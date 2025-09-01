#!/usr/bin/env python3
"""
Simple script to create sample services for testing the admin interface
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from services.models import Service, ServiceCategory
from users.models import User

def create_sample_data():
    print("🏠 Creating Sample Home Services Data...")

    # Get admin user
    try:
        admin_user = User.objects.get(email='admin@homeservice.com')
        print(f"✅ Found admin user: {admin_user.email}")
    except User.DoesNotExist:
        print("❌ Admin user not found. Please run create_admin.py first.")
        return

    # Create categories
    categories_data = [
        {'name': 'Plumbing', 'slug': 'plumbing', 'description': 'Plumbing repair and installation services'},
        {'name': 'Electrical', 'slug': 'electrical', 'description': 'Electrical repair and installation services'},
        {'name': 'Cleaning', 'slug': 'cleaning', 'description': 'Home and office cleaning services'},
        {'name': 'Painting', 'slug': 'painting', 'description': 'Interior and exterior painting services'},
        {'name': 'AC Service', 'slug': 'ac-service', 'description': 'Air conditioning repair and maintenance'},
    ]

    created_categories = []
    for cat_data in categories_data:
        category, created = ServiceCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        created_categories.append(category)
        if created:
            print(f"✅ Created category: {category.name}")
        else:
            print(f"✅ Category exists: {category.name}")

    # Create sample services
    services_data = [
        {
            'name': 'Basic Plumbing Repair',
            'category': created_categories[0],  # Plumbing
            'price': 500.00,
            'duration': 2,
            'description': 'Fix leaks, unclog drains, and basic plumbing repairs for your home. Professional service with quality guarantee.'
        },
        {
            'name': 'Electrical Installation',
            'category': created_categories[1],  # Electrical
            'price': 800.00,
            'duration': 3,
            'description': 'Install switches, outlets, fans, and basic electrical work. Licensed electrician service.'
        },
        {
            'name': 'Deep House Cleaning',
            'category': created_categories[2],  # Cleaning
            'price': 1200.00,
            'duration': 4,
            'description': 'Complete deep cleaning of your home including all rooms, bathrooms, and kitchen. Eco-friendly products used.'
        },
        {
            'name': 'Interior Wall Painting',
            'category': created_categories[3],  # Painting
            'price': 2000.00,
            'duration': 6,
            'description': 'Professional interior wall painting service with premium quality paint. Color consultation included.'
        },
        {
            'name': 'AC Repair & Service',
            'category': created_categories[4],  # AC Service
            'price': 600.00,
            'duration': 2,
            'description': 'Air conditioning repair, cleaning, and maintenance service. Gas refilling and filter replacement included.'
        },
    ]

    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            name=service_data['name'],
            defaults={
                'description': service_data['description'],
                'price': service_data['price'],
                'category': service_data['category'],
                'provider': admin_user,
                'duration': service_data['duration'],
                'is_available': True,
                'is_active': True
            }
        )
        if created:
            print(f"✅ Created service: {service.name} - ₹{service.price}")
        else:
            print(f"✅ Service exists: {service.name} - ₹{service.price}")

    print(f"\n🎉 Sample data creation complete!")
    print(f"📊 Total Services: {Service.objects.count()}")
    print(f"📊 Total Categories: {ServiceCategory.objects.count()}")
    print(f"\n🔗 Now you can access the admin services interface:")
    print(f"🔗 URL: http://127.0.0.1:8000/services/admin-services/")

if __name__ == '__main__':
    create_sample_data()
