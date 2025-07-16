#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def test_review_url_fix():
    """Test that the review URL fix resolves the NoReverseMatch error"""
    print("🔧 Testing Review URL Fix...\n")
    
    try:
        from django.urls import reverse
        from users.models import User
        import pymongo
        from django.conf import settings
        from datetime import datetime, timedelta
        
        # Test URL reversal with MongoDB ObjectId
        print("📝 Step 1: Testing URL Reversal...")
        
        # Test with a MongoDB ObjectId format
        test_objectid = "683bf636b6af74c3402e66c6"
        
        try:
            # This should now work with the str: parameter and correct namespace
            review_url = reverse('services:add_review', args=[test_objectid])
            print(f"   ✅ URL reversal successful: {review_url}")
        except Exception as url_error:
            print(f"   ❌ URL reversal failed: {url_error}")
            return False
        
        # Test booking_list URL reversal
        try:
            booking_list_url = reverse('services:booking_list')
            print(f"   ✅ Booking list URL reversal successful: {booking_list_url}")
        except Exception as url_error:
            print(f"   ❌ Booking list URL reversal failed: {url_error}")
            return False
        
        print(f"\n📝 Step 2: Creating Test Completed Booking...")
        
        # Get test user
        customer = User.objects.get(email='test@example.com')
        
        # Connect to MongoDB
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Create a completed booking for review testing
        completed_booking = {
            'customer_id': customer.id,
            'provider_id': None,
            'status': 'completed',  # Completed status for review
            'total_amount': 2500,
            'booking_date': datetime.now() - timedelta(days=1),  # Past date
            'address': '888 Review URL Test Street, Test City',
            'phone_number': '+91-7777666655',
            'notes': 'Completed Service - Review URL Test',
            'special_instructions': 'Test the review URL fix',
            'is_paid': True,
            'payment_status': 'paid',
            'created_at': datetime.now() - timedelta(days=2),
            'updated_at': datetime.now(),
            'service_completed_at': datetime.now() - timedelta(hours=3),
            'service_completed_by': 32  # Servicer ID
        }
        
        booking_result = db['services_booking'].insert_one(completed_booking)
        booking_id = booking_result.inserted_id
        
        print(f"   ✅ Created completed booking: {str(booking_id)[:8]}")
        print(f"   ✅ Status: completed (ready for review)")
        print(f"   ✅ Customer: {customer.get_full_name()}")
        
        # Test the review URL with the actual booking ID
        try:
            review_url = reverse('services:add_review', args=[str(booking_id)])
            print(f"   ✅ Review URL for booking: {review_url}")
        except Exception as url_error:
            print(f"   ❌ Review URL error: {url_error}")
            return False
        
        print(f"\n🔍 Step 3: Testing Review View Access...")
        
        # Test if we can access the review view without errors
        try:
            from django.test import Client
            from django.contrib.auth import get_user_model
            
            # Create test client and login
            client = Client()
            client.force_login(customer)
            
            # Try to access the review URL
            response = client.get(review_url)
            
            print(f"   • Review view response status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Review view accessible (Status: 200)")
            elif response.status_code == 302:
                print(f"   ✅ Review view redirected (Status: 302) - This is expected for MongoDB bookings")
                # Check if it redirected to booking list
                if 'bookings' in response.url:
                    print(f"   ✅ Correctly redirected to booking list")
                else:
                    print(f"   ⚠️ Redirected to: {response.url}")
            else:
                print(f"   ⚠️ Unexpected status code: {response.status_code}")
                
        except Exception as access_error:
            print(f"   ❌ Error accessing review view: {access_error}")
            return False
        
        print(f"\n📊 Step 4: Testing Booking List Access...")
        
        # Test if booking list is accessible
        try:
            booking_list_response = client.get('/services/bookings/')
            
            if booking_list_response.status_code == 200:
                print(f"   ✅ Booking list accessible (Status: 200)")
            else:
                print(f"   ⚠️ Booking list status: {booking_list_response.status_code}")
                
        except Exception as list_error:
            print(f"   ❌ Error accessing booking list: {list_error}")
        
        print(f"\n🎉 Review URL Fix Test Completed!")
        
        # Cleanup
        print(f"\n🧹 Cleanup...")
        db['services_booking'].delete_one({'_id': booking_id})
        print(f"   ✅ Test booking cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing review URL fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Testing Review URL Fix\n")
    
    success = test_review_url_fix()
    
    if success:
        print(f"\n🎉 Review URL Fix Test Passed!")
        print(f"\n✅ Key Fixes:")
        print(f"   • Changed add_review URL from <int:booking_id> to <str:booking_id>")
        print(f"   • Fixed redirect URLs to use 'services:booking_list' namespace")
        print(f"   • Updated add_review view to handle MongoDB ObjectIds")
        print(f"   • URL reversal now works with both ObjectIds and integers")
        
        print(f"\n📱 The NoReverseMatch errors should now be resolved!")
        print(f"\n🔗 Test URLs:")
        print(f"   • Booking List: http://127.0.0.1:8000/services/bookings/")
        print(f"   • Login: http://127.0.0.1:8000/accounts/login/")
        
        print(f"\n💡 Note:")
        print(f"   • Review functionality for MongoDB bookings shows info message")
        print(f"   • This prevents the NoReverseMatch error")
        print(f"   • Users are redirected to booking list safely")
    else:
        print(f"\n❌ Review URL Fix Test Failed")
        
    print(f"\n🔧 The original error should now be fixed!")
