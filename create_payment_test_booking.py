#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def create_test_booking():
    """Create a test booking for payment testing"""
    print("📝 Creating test booking for payment testing...")
    
    try:
        from services.models import Service, ServiceCategory, Booking
        from users.models import User
        
        # Get or create test user
        test_user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'user_type': 'customer'
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            print("✅ Created test user")
        else:
            print("✅ Using existing test user")
        
        # Get or create admin user (service provider)
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
            print("✅ Created admin user")
        else:
            print("✅ Using existing admin user")
        
        # Get any existing category or create a new one
        category = ServiceCategory.objects.first()
        if not category:
            category = ServiceCategory.objects.create(
                name='Test Category',
                description='Test category for payment testing',
                slug='test-category'
            )
            print("✅ Created Test category")
        else:
            print(f"✅ Using existing category: {category.name}")
        
        # Get any existing service
        service = Service.objects.first()
        if not service:
            print("❌ No services found. Please create a service first through the admin interface.")
            return None
        else:
            print(f"✅ Using existing service: {service.name}")
        
        # Create test booking
        booking_date = datetime.now() + timedelta(days=1)  # Tomorrow
        
        # Check if booking already exists
        existing_booking = Booking.objects.filter(
            customer=test_user,
            service=service,
            status='pending'
        ).first()
        
        if existing_booking:
            print(f"✅ Using existing test booking: {existing_booking.id}")
            return existing_booking
        
        # Create new booking
        booking = Booking.objects.create(
            customer=test_user,
            service=service,
            provider=admin_user,
            booking_date=booking_date,
            total_amount=service.price,
            status='pending',
            payment_status='pending',
            is_paid=False,
            phone_number='9876543210',
            address='123 Test Street, Test City',
            special_instructions='Test booking for payment flow',
            notes=f'Service: {service.name}\nCategory: {category.name}\nProvider: {admin_user.get_full_name()}\nDuration: {service.duration} hours'
        )
        
        print(f"✅ Created test booking: {booking.id}")
        print(f"   Service: {service.name}")
        print(f"   Amount: ₹{service.price}")
        print(f"   Date: {booking_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Status: {booking.status}")
        
        return booking
        
    except Exception as e:
        print(f"❌ Error creating test booking: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    print("🚀 Creating Test Booking for Payment Testing\n")
    
    booking = create_test_booking()
    
    if booking:
        print(f"\n🎉 Test booking created successfully!")
        print(f"\n📝 Test Details:")
        print(f"   User: test@example.com / testpass123")
        print(f"   Booking ID: {booking.id}")
        print(f"   Payment URL: http://127.0.0.1:8000/services/payment/{booking.id}/")
        print(f"\n🔗 To test payment:")
        print(f"1. Go to: http://127.0.0.1:8000/services/payment/{booking.id}/")
        print(f"2. Select UPI payment method")
        print(f"3. Click 'I have paid ₹{booking.total_amount}' button")
        print(f"4. Should redirect to success page")
    else:
        print("\n❌ Failed to create test booking")
