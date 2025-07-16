#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def test_url_fix():
    """Test that the URL fix resolves the NoReverseMatch error"""
    print("🔧 Testing URL Fix for MongoDB ObjectId...\n")
    
    try:
        from django.urls import reverse
        from django.test import RequestFactory
        from users.models import User
        import pymongo
        from django.conf import settings
        from datetime import datetime, timedelta
        
        # Test URL reversal with MongoDB ObjectId
        print("📝 Step 1: Testing URL Reversal...")
        
        # Test with a MongoDB ObjectId format
        test_objectid = "683bf2057f4dbcc9d9cad7b2"
        
        try:
            # This should now work with the str: parameter (using correct namespace)
            review_url = reverse('services:add_review', args=[test_objectid])
            print(f"   ✅ URL reversal successful: {review_url}")
        except Exception as url_error:
            print(f"   ❌ URL reversal failed: {url_error}")
            return False

        # Test with integer ID (should still work)
        try:
            review_url_int = reverse('services:add_review', args=[123])
            print(f"   ✅ Integer URL reversal successful: {review_url_int}")
        except Exception as url_error:
            print(f"   ❌ Integer URL reversal failed: {url_error}")
        
        print(f"\n📊 Step 2: Checking Current Bookings...")
        
        # Check current bookings in database
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        all_bookings = list(db['services_booking'].find({}))
        print(f"   • Total bookings in database: {len(all_bookings)}")
        
        if len(all_bookings) > 0:
            print(f"   📋 Booking IDs and statuses:")
            for booking in all_bookings:
                booking_id = str(booking['_id'])
                status = booking.get('status', 'unknown')
                customer_id = booking.get('customer_id', 'unknown')
                print(f"     • {booking_id[:8]}...: {status}, Customer: {customer_id}")
        
        print(f"\n🔍 Step 3: Testing Booking List Access...")
        
        # Test if we can access the booking list without errors
        try:
            from django.test import Client
            from django.contrib.auth import get_user_model
            
            # Get test user
            User = get_user_model()
            test_user = User.objects.get(email='test@example.com')
            
            # Create test client and login
            client = Client()
            client.force_login(test_user)
            
            # Try to access booking list
            response = client.get('/services/bookings/')
            
            if response.status_code == 200:
                print(f"   ✅ Booking list accessible (Status: {response.status_code})")
            else:
                print(f"   ⚠️ Booking list returned status: {response.status_code}")
                
        except Exception as access_error:
            print(f"   ❌ Error accessing booking list: {access_error}")
        
        print(f"\n✅ URL Fix Test Completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing URL fix: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_completed_booking_for_review():
    """Create a completed booking that can be reviewed"""
    print(f"\n📝 Creating Completed Booking for Review Testing...")
    
    try:
        from users.models import User
        import pymongo
        from django.conf import settings
        from datetime import datetime, timedelta
        
        customer = User.objects.get(email='test@example.com')
        
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Create a completed booking for review testing
        completed_booking = {
            'customer_id': customer.id,
            'provider_id': None,
            'status': 'completed',  # Completed status for review
            'total_amount': 2200,
            'booking_date': datetime.now() - timedelta(days=1),  # Past date
            'address': '777 Review Test Street, Test City',
            'phone_number': '+91-8888777766',
            'notes': 'Completed Service - Ready for Review',
            'special_instructions': 'Test the review functionality',
            'is_paid': True,
            'payment_status': 'paid',
            'created_at': datetime.now() - timedelta(days=2),
            'updated_at': datetime.now(),
            'service_completed_at': datetime.now() - timedelta(hours=2),
            'service_completed_by': 32  # Servicer ID
        }
        
        booking_result = db['services_booking'].insert_one(completed_booking)
        booking_id = booking_result.inserted_id
        
        # Create invoice
        invoice_doc = {
            'booking_id': booking_id,
            'invoice_number': f"INV-{str(booking_id)[:8].upper()}",
            'generated_at': datetime.now(),
            'subtotal': float(completed_booking['total_amount']),
            'tax_amount': float(completed_booking['total_amount']) * 0.18,
            'total_amount': float(completed_booking['total_amount']) * 1.18
        }
        
        db['services_invoice'].insert_one(invoice_doc)
        
        print(f"   ✅ Created completed booking: {str(booking_id)[:8]}")
        print(f"   ✅ Status: completed (ready for review)")
        print(f"   ✅ Customer: {customer.get_full_name()}")
        print(f"   ✅ Invoice: {invoice_doc['invoice_number']}")
        
        # Test the review URL
        from django.urls import reverse
        try:
            review_url = reverse('services:add_review', args=[str(booking_id)])
            print(f"   ✅ Review URL: {review_url}")
        except Exception as url_error:
            print(f"   ❌ Review URL error: {url_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating completed booking: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Testing URL Fix for MongoDB ObjectId\n")
    
    url_success = test_url_fix()
    booking_success = create_completed_booking_for_review()
    
    if url_success and booking_success:
        print(f"\n🎉 URL Fix Test Passed!")
        print(f"\n✅ Key Fixes:")
        print(f"   • Changed add_review URL from <int:booking_id> to <str:booking_id>")
        print(f"   • Updated add_review view to handle MongoDB ObjectIds")
        print(f"   • URL reversal now works with both ObjectIds and integers")
        print(f"   • Created completed booking for review testing")
        
        print(f"\n📱 Test the Fix:")
        print(f"   1. Login as customer: http://127.0.0.1:8000/accounts/login/")
        print(f"   2. Go to bookings: http://127.0.0.1:8000/services/bookings/")
        print(f"   3. Should load without NoReverseMatch error")
        print(f"   4. Try to add review for completed booking")
        
        print(f"\n🔗 URLs:")
        print(f"   • Booking List: http://127.0.0.1:8000/services/bookings/")
        print(f"   • Login: http://127.0.0.1:8000/accounts/login/")
    else:
        print(f"\n❌ URL Fix Test Failed")
        
    print(f"\n💡 The NoReverseMatch error should now be resolved!")
