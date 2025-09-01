#!/usr/bin/env python
"""
Direct test of payment page by manually inserting booking data
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from decimal import Decimal
import pymongo
from django.conf import settings

def test_payment_page_direct():
    """Test payment page by directly inserting booking data"""
    User = get_user_model()
    
    # Get or create test user
    try:
        user = User.objects.get(email='test@example.com')
        print(f"Using existing user: {user.email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        print(f"Created new user: {user.email}")
    
    # Connect to MongoDB directly
    try:
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        bookings_collection = db['services_booking']
        
        # Create a test booking directly in MongoDB
        tomorrow = datetime.now() + timedelta(days=1)
        
        booking_data = {
            'customer_id': user.id,
            'provider_id': user.id,  # Use same user as provider for testing
            'service_id': None,  # We'll leave this null for testing
            'status': 'pending',
            'booking_date': tomorrow,
            'address': '123 Test Street, Test City',
            'phone_number': '9876543210',
            'total_amount': Decimal('2500.00'),
            'payment_status': 'pending',
            'is_paid': False,
            'special_instructions': 'Test booking for payment page',
            'notes': 'Sample booking for Electrical Installation',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Insert the booking
        result = bookings_collection.insert_one(booking_data)
        booking_id = result.inserted_id
        
        print(f"✅ Booking created directly in MongoDB with ID: {booking_id}")
        
        # Test payment URL
        from django.urls import reverse
        payment_url = reverse('services:payment', kwargs={'booking_id': str(booking_id)})
        print(f"Payment URL: http://127.0.0.1:8000{payment_url}")
        
        return str(booking_id)
        
    except Exception as e:
        print(f"❌ Error creating booking directly: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None

def test_with_django_orm():
    """Alternative test using Django ORM with minimal data"""
    User = get_user_model()
    
    try:
        user = User.objects.get(email='test@example.com')
        print(f"Using existing user: {user.email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        print(f"Created new user: {user.email}")
    
    # Try to create a booking using raw SQL/MongoDB commands
    from django.db import connection
    
    try:
        # Use Django's raw database connection
        tomorrow = datetime.now() + timedelta(days=1)
        
        # Create booking using Django ORM but with minimal validation
        from services.models import Booking
        
        # Create a booking instance without saving first
        booking = Booking(
            customer=user,
            provider=user,
            status='pending',
            booking_date=tomorrow,
            address='123 Test Street, Test City',
            phone_number='9876543210',
            total_amount=Decimal('2500.00'),
            special_instructions='Test booking for payment page',
            notes='Sample booking for Electrical Installation'
        )
        
        # Try to save with minimal validation
        booking.save()
        
        print(f"✅ Booking created with Django ORM: {booking.id}")
        
        # Test payment URL
        from django.urls import reverse
        booking_id_str = str(booking.id)
        payment_url = reverse('services:payment', kwargs={'booking_id': booking_id_str})
        print(f"Payment URL: http://127.0.0.1:8000{payment_url}")

        return booking_id_str
        
    except Exception as e:
        print(f"❌ Error with Django ORM: {e}")
        return None

if __name__ == '__main__':
    print("Testing payment page access...")
    print("\n1. Trying direct MongoDB insertion:")
    booking_id = test_payment_page_direct()
    
    if not booking_id:
        print("\n2. Trying Django ORM approach:")
        booking_id = test_with_django_orm()
    
    if booking_id:
        print(f"\n✅ Test completed successfully!")
        print(f"You can now test the payment page at: http://127.0.0.1:8000/services/payment/{booking_id}/")
        print(f"Login with: test@example.com / testpass123")
    else:
        print(f"\n❌ All tests failed!")
