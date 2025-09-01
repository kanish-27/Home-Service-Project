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

def test_booking_system():
    print("🧪 Testing Booking System...")
    
    # Check if we have any bookings
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    
    print(f"📊 Total bookings: {total_bookings}")
    print(f"⏳ Pending bookings: {pending_bookings}")
    
    # Check if we have users
    customers = User.objects.filter(user_type='customer').count()
    admins = User.objects.filter(user_type='admin').count()
    
    print(f"👥 Customers: {customers}")
    print(f"👨‍💼 Admins: {admins}")
    
    # Check if we have services
    services = Service.objects.count()
    categories = ServiceCategory.objects.count()
    
    print(f"🛠️ Services: {services}")
    print(f"📂 Categories: {categories}")
    
    if pending_bookings == 0:
        print("\n🔧 Creating test booking for testing...")
        create_test_booking()
    
    print("\n✅ Booking system test completed!")

def create_test_booking():
    try:
        # Get or create a customer
        customer, created = User.objects.get_or_create(
            email='test.customer@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'Customer',
                'user_type': 'customer'
            }
        )
        if created:
            customer.set_password('customer123')
            customer.save()
            print(f"✅ Created test customer: {customer.email}")
        
        # Get or create a provider
        provider, created = User.objects.get_or_create(
            email='test.provider@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'Provider',
                'user_type': 'provider'
            }
        )
        if created:
            provider.set_password('provider123')
            provider.save()
            print(f"✅ Created test provider: {provider.email}")
        
        # Get or create a category
        category, created = ServiceCategory.objects.get_or_create(
            name='Test Category',
            defaults={'description': 'Test category for testing'}
        )
        if created:
            print(f"✅ Created test category: {category.name}")
        
        # Get or create a service
        service, created = Service.objects.get_or_create(
            name='Test Service',
            defaults={
                'category': category,
                'provider': provider,
                'description': 'Test service for testing booking system',
                'price': Decimal('1500.00'),
                'duration': 2,
                'is_active': True
            }
        )
        if created:
            print(f"✅ Created test service: {service.name}")
        
        # Create a test booking
        booking = Booking.objects.create(
            customer=customer,
            service=service,
            provider=provider,
            booking_date=datetime.now() + timedelta(days=1),
            total_amount=Decimal('1500.00'),
            address='123 Test Street, Test City',
            phone_number='1234567890',
            notes='Test booking for admin approval testing',
            status='pending'
        )
        
        print(f"✅ Created test booking: ID {booking.id}")
        print(f"   Customer: {booking.customer.email}")
        print(f"   Service: {booking.service.name}")
        print(f"   Amount: ₹{booking.total_amount}")
        print(f"   Status: {booking.status}")
        
    except Exception as e:
        print(f"❌ Error creating test booking: {e}")

if __name__ == '__main__':
    test_booking_system()
