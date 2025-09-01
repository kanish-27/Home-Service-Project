#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def create_simple_test_booking():
    """Create a simple test booking using MongoDB directly"""
    print("📝 Creating simple test booking...")
    
    try:
        import pymongo
        from django.conf import settings
        from bson import ObjectId
        from users.models import User
        
        # Get test user
        test_user = User.objects.filter(email='test@example.com').first()
        if not test_user:
            test_user = User.objects.create_user(
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User',
                user_type='customer'
            )
            print("✅ Created test user")
        else:
            print("✅ Using existing test user")
        
        # Get admin user
        admin_user = User.objects.filter(email='admin@homeservice.com').first()
        if not admin_user:
            admin_user = User.objects.create_user(
                email='admin@homeservice.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                user_type='admin',
                is_staff=True,
                is_superuser=True
            )
            print("✅ Created admin user")
        else:
            print("✅ Using existing admin user")
        
        # Connect to MongoDB
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Create test booking directly in MongoDB
        booking_data = {
            '_id': ObjectId(),
            'customer_id': test_user.id,
            'provider_id': admin_user.id,
            'booking_date': datetime.now() + timedelta(days=1),
            'total_amount': 500.0,
            'status': 'pending',
            'payment_status': 'pending',
            'is_paid': False,
            'phone_number': '9876543210',
            'address': '123 Test Street, Test City',
            'special_instructions': 'Test booking for payment flow',
            'notes': 'Service: Test Service\nCategory: Test Category\nProvider: Admin User\nDuration: 2 hours',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Insert booking
        result = db['services_booking'].insert_one(booking_data)
        booking_id = str(result.inserted_id)
        
        print(f"✅ Created test booking: {booking_id}")
        print(f"   Customer: {test_user.email}")
        print(f"   Amount: ₹{booking_data['total_amount']}")
        print(f"   Status: {booking_data['status']}")
        
        return booking_id, test_user
        
    except Exception as e:
        print(f"❌ Error creating test booking: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_payment_urls(booking_id):
    """Test payment URLs"""
    print(f"\n🔗 Testing Payment URLs for booking {booking_id}...")
    
    try:
        from django.urls import reverse
        
        # Test URL generation
        payment_url = reverse('services:payment', kwargs={'booking_id': booking_id})
        process_url = reverse('services:process_payment', kwargs={'booking_id': booking_id})
        success_url = reverse('services:payment_success', kwargs={'booking_id': booking_id})
        
        print(f"✅ Payment page: http://127.0.0.1:8000{payment_url}")
        print(f"✅ Process payment: http://127.0.0.1:8000{process_url}")
        print(f"✅ Success page: http://127.0.0.1:8000{success_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing URLs: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Creating Simple Test Booking for Payment Testing\n")
    
    booking_id, test_user = create_simple_test_booking()
    
    if booking_id and test_user:
        print(f"\n🎉 Test booking created successfully!")
        
        # Test URLs
        test_payment_urls(booking_id)
        
        print(f"\n📝 Manual Testing Steps:")
        print(f"1. Open browser: http://127.0.0.1:8000/login/")
        print(f"2. Login with: {test_user.email} / testpass123")
        print(f"3. Go to payment page: http://127.0.0.1:8000/services/payment/{booking_id}/")
        print(f"4. Select UPI payment method")
        print(f"5. Click 'I have paid ₹500.00' button")
        print(f"6. Should redirect to: http://127.0.0.1:8000/services/payment/success/{booking_id}/")
        print(f"7. Check browser console (F12) for any JavaScript errors")
        
        print(f"\n🔧 Direct Test URLs:")
        print(f"   Payment: http://127.0.0.1:8000/services/payment/{booking_id}/")
        print(f"   Success: http://127.0.0.1:8000/services/payment/success/{booking_id}/")
        
    else:
        print("\n❌ Failed to create test booking")
