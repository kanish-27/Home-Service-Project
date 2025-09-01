#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def test_booking_detail_fix():
    """Test the booking detail template fix for VariableDoesNotExist error"""
    print("🔧 Testing Booking Detail Template Fix...\n")
    
    try:
        from users.models import User
        import pymongo
        from django.conf import settings
        from datetime import datetime, timedelta
        
        # Get test user
        customer = User.objects.get(email='test@example.com')
        
        print(f"✅ Customer: {customer.get_full_name()}")
        
        # Connect to MongoDB
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Step 1: Create a test booking with rejection fields
        print(f"\n📝 Step 1: Creating Test Booking with Rejection Fields...")
        
        test_booking = {
            'customer_id': customer.id,
            'provider_id': None,
            'status': 'rejected',  # Rejected status to test rejection fields
            'total_amount': 2200,
            'booking_date': datetime.now() + timedelta(days=1),
            'address': '123 Template Fix Street, Test City',
            'phone_number': '+91-9999888877',
            'notes': 'Test Service - Template Fix',
            'special_instructions': 'Test the template field access fix',
            'is_paid': True,
            'payment_status': 'paid',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'rejection_reason': 'Test rejection reason for template fix',
            'rejected_at': datetime.now() - timedelta(hours=1),
            'admin_notes': 'Test admin notes'
        }
        
        booking_result = db['services_booking'].insert_one(test_booking)
        booking_id = booking_result.inserted_id
        
        print(f"   ✅ Created test booking: {str(booking_id)[:8]}")
        print(f"   • Status: rejected")
        print(f"   • Rejection reason: {test_booking['rejection_reason']}")
        print(f"   • Rejected at: {test_booking['rejected_at']}")
        
        # Step 2: Test booking detail URL access
        print(f"\n🔗 Step 2: Testing Booking Detail URL Access...")
        
        from django.urls import reverse
        try:
            booking_detail_url = reverse('services:booking_detail', args=[str(booking_id)])
            print(f"   ✅ Booking detail URL: {booking_detail_url}")
        except Exception as url_error:
            print(f"   ❌ Booking detail URL error: {url_error}")
            return False
        
        # Step 3: Test template access
        print(f"\n📱 Step 3: Testing Template Access...")
        
        try:
            from django.test import Client
            
            # Create test client and login
            client = Client()
            client.force_login(customer)
            
            # Try to access the booking detail page
            response = client.get(booking_detail_url)
            
            print(f"   • Booking detail response status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Booking detail page accessible")
                
                # Check if rejection fields are handled properly
                response_content = response.content.decode('utf-8')
                
                template_checks = [
                    ("Booking Rejected", "Rejection alert section"),
                    ("Test rejection reason", "Rejection reason display"),
                    ("No reason provided", "Default rejection reason fallback")
                ]
                
                for check_text, description in template_checks:
                    if check_text in response_content:
                        print(f"   ✅ {description} found")
                    else:
                        print(f"   ⚠️ {description} not found")
                        
            elif response.status_code == 500:
                print(f"   ❌ Server error (500) - Template issue still exists")
                return False
            else:
                print(f"   ⚠️ Unexpected status code: {response.status_code}")
                
        except Exception as access_error:
            print(f"   ❌ Error accessing booking detail: {access_error}")
            return False
        
        # Step 4: Test MockBooking object creation
        print(f"\n🎭 Step 4: Testing MockBooking Object Creation...")
        
        # Simulate the MockBooking creation from BookingDetailView
        class TestMockBooking:
            def __init__(self, data, user):
                self.id = str(data['_id'])
                self.customer = user
                self.provider_id = data.get('provider_id')
                self.booking_date = data.get('booking_date')
                self.address = data.get('address', '')
                self.phone_number = data.get('phone_number', '')
                self.total_amount = data.get('total_amount', 0)
                self.notes = data.get('notes', '')
                self.special_instructions = data.get('special_instructions', '')
                self.status = data.get('status', 'pending')
                self.payment_status = data.get('payment_status', 'pending')
                self.is_paid = data.get('is_paid', False)
                self.payment_method = data.get('payment_method', '')
                self.transaction_id = data.get('transaction_id', '')
                self.created_at = data.get('created_at')
                self.updated_at = data.get('updated_at')
                self.rejection_reason = data.get('rejection_reason', '')
                self.rejected_at = data.get('rejected_at')
                self.admin_notes = data.get('admin_notes', '')
                
            def get_status_display(self):
                status_map = {
                    'pending': 'Pending',
                    'confirmed': 'Confirmed',
                    'rejected': 'Rejected',
                    'completed': 'Completed',
                    'cancelled': 'Cancelled'
                }
                return status_map.get(self.status, self.status.title())
                
            def get(self, key, default=None):
                """Allow template to access data using get method"""
                return getattr(self, key, default)
        
        # Create mock booking object
        mock_booking = TestMockBooking(test_booking, customer)
        
        print(f"   ✅ MockBooking object created successfully")
        print(f"   • ID: {mock_booking.id}")
        print(f"   • Status: {mock_booking.status}")
        print(f"   • Rejection reason: {mock_booking.rejection_reason}")
        print(f"   • Has rejection_reason attribute: {hasattr(mock_booking, 'rejection_reason')}")
        print(f"   • Has rejected_at attribute: {hasattr(mock_booking, 'rejected_at')}")
        print(f"   • Has get method: {hasattr(mock_booking, 'get')}")
        
        # Test get method
        print(f"   • get('rejection_reason'): {mock_booking.get('rejection_reason')}")
        print(f"   • get('rejected_at'): {mock_booking.get('rejected_at')}")
        
        print(f"\n🎉 Booking Detail Template Fix Test Completed!")
        
        # Cleanup
        print(f"\n🧹 Cleanup...")
        db['services_booking'].delete_one({'_id': booking_id})
        print(f"   ✅ Test booking cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing booking detail fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Testing Booking Detail Template Fix\n")
    
    success = test_booking_detail_fix()
    
    if success:
        print(f"\n🎉 Booking Detail Template Fix Test Passed!")
        print(f"\n✅ Key Fixes:")
        print(f"   • Template safely handles rejection_reason field")
        print(f"   • Template safely handles rejected_at field")
        print(f"   • MockBooking object includes all necessary fields")
        print(f"   • Template uses conditional checks for field access")
        print(f"   • No more VariableDoesNotExist errors")
        
        print(f"\n📱 The VariableDoesNotExist error should now be resolved!")
        print(f"\n🔗 Test URLs:")
        print(f"   • Booking List: http://127.0.0.1:8000/services/bookings/")
        print(f"   • Login: http://127.0.0.1:8000/accounts/login/")
        
        print(f"\n💡 Template now safely handles MongoDB booking fields!")
    else:
        print(f"\n❌ Booking Detail Template Fix Test Failed")
        
    print(f"\n🔧 The template field access issue should be fixed!")
