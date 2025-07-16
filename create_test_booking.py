#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from services.models import Booking, Service, ServiceCategory
from users.models import User
from decimal import Decimal
from datetime import datetime, timedelta

def create_test_data():
    print("🔧 Creating test data for booking approval testing...")
    
    try:
        # Create or get admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@homeservice.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'user_type': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            print(f"✅ Created admin user: {admin_user.email}")
        else:
            print(f"✅ Admin user exists: {admin_user.email}")

        # Create test customer
        customer, created = User.objects.get_or_create(
            email='customer@test.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'Customer',
                'user_type': 'customer'
            }
        )
        if created:
            customer.set_password('customer123')
            customer.save()
            print(f"✅ Created customer: {customer.email}")

        # Create test provider
        provider, created = User.objects.get_or_create(
            email='provider@test.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'Provider',
                'user_type': 'provider'
            }
        )
        if created:
            provider.set_password('provider123')
            provider.save()
            print(f"✅ Created provider: {provider.email}")

        # Create test category
        category, created = ServiceCategory.objects.get_or_create(
            name='Home Cleaning',
            defaults={'description': 'Professional home cleaning services'}
        )
        if created:
            print(f"✅ Created category: {category.name}")

        # Create test service
        service, created = Service.objects.get_or_create(
            name='Deep House Cleaning',
            defaults={
                'category': category,
                'provider': provider,
                'description': 'Complete deep cleaning service for your home',
                'price': Decimal('2500.00'),
                'duration': 3,
                'is_active': True
            }
        )
        if created:
            print(f"✅ Created service: {service.name}")

        # Create test bookings
        booking1 = Booking.objects.create(
            customer=customer,
            service=service,
            provider=provider,
            booking_date=datetime.now() + timedelta(days=1),
            total_amount=Decimal('2500.00'),
            address='123 Test Street, Mumbai, Maharashtra',
            phone_number='9876543210',
            notes='Regular cleaning service needed',
            status='pending'
        )
        print(f"✅ Created booking 1: ID {booking1.id}")

        booking2 = Booking.objects.create(
            customer=customer,
            service=service,
            provider=provider,
            booking_date=datetime.now() + timedelta(days=2),
            total_amount=Decimal('3000.00'),
            address='456 Another Street, Delhi, India',
            phone_number='9876543210',
            notes='Deep cleaning required',
            status='pending'
        )
        print(f"✅ Created booking 2: ID {booking2.id}")

        # Summary
        total_bookings = Booking.objects.count()
        pending_bookings = Booking.objects.filter(status='pending').count()
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total bookings: {total_bookings}")
        print(f"   Pending bookings: {pending_bookings}")
        print(f"   Admin email: admin@homeservice.com")
        print(f"   Admin password: admin123")
        print(f"\n🎯 Ready for testing! Go to: http://127.0.0.1:8000/services/admin-bookings/")

    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_test_data()
