#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def create_test_booking_for_admin():
    """Create a simple test booking for admin to approve"""
    print("📝 Creating Test Booking for Admin Approval...\n")
    
    try:
        from users.models import User
        import pymongo
        from django.conf import settings
        from datetime import datetime, timedelta
        
        # Get users (avoid Django ORM issues)
        try:
            servicer = User.objects.get(email='servicer@example.com')
            customer = User.objects.get(email='test@example.com')
            print(f"✅ Found servicer: {servicer.get_full_name()} (ID: {servicer.id})")
            print(f"✅ Found customer: {customer.get_full_name()} (ID: {customer.id})")
        except Exception as user_error:
            print(f"❌ Error finding users: {user_error}")
            return False
        
        # Connect to MongoDB directly
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Create a pending booking for admin approval
        test_booking = {
            'customer_id': customer.id,
            'provider_id': None,  # No provider initially - admin will assign
            'status': 'pending',  # Waiting for admin approval
            'total_amount': 2800,
            'booking_date': datetime.now() + timedelta(days=2),
            'address': '123 Test Admin Approval Street, Test City',
            'phone_number': '+91-9876543210',
            'notes': 'Test Service - Admin Approval Required',
            'special_instructions': 'Please approve this booking to test servicer assignment',
            'is_paid': True,  # Payment completed
            'payment_status': 'paid',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Insert the booking
        booking_result = db['services_booking'].insert_one(test_booking)
        booking_id = booking_result.inserted_id
        
        print(f"✅ Created test booking: {str(booking_id)[:8]}")
        print(f"   • Status: pending (awaiting admin approval)")
        print(f"   • Customer: {customer.get_full_name()}")
        print(f"   • Amount: ₹{test_booking['total_amount']}")
        print(f"   • Provider: None (admin will assign)")
        
        # Verify the booking was created
        created_booking = db['services_booking'].find_one({'_id': booking_id})
        if created_booking:
            print(f"   ✅ Booking verified in database")
        else:
            print(f"   ❌ Booking not found in database")
            return False
        
        print(f"\n📱 Next Steps for Testing:")
        print(f"   1. Login as admin: http://127.0.0.1:8000/admin-dashboard/")
        print(f"   2. You should see 1 pending booking")
        print(f"   3. Approve the booking")
        print(f"   4. Login as servicer: http://127.0.0.1:8000/servicer-dashboard/")
        print(f"   5. You should see the approved booking")
        print(f"   6. Mark it as completed")
        print(f"   7. Login as customer: http://127.0.0.1:8000/services/my-bookings/")
        print(f"   8. Check 'What Happens Next' - should show GREEN")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test booking: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_current_state():
    """Check current state of bookings"""
    print("📊 Checking Current Database State...\n")
    
    try:
        import pymongo
        from django.conf import settings
        
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Count bookings by status
        pending_count = db['services_booking'].count_documents({'status': 'pending'})
        confirmed_count = db['services_booking'].count_documents({'status': 'confirmed'})
        completed_count = db['services_booking'].count_documents({'status': 'completed'})
        total_count = db['services_booking'].count_documents({})
        
        print(f"📈 Booking Status Summary:")
        print(f"   • Pending: {pending_count}")
        print(f"   • Confirmed: {confirmed_count}")
        print(f"   • Completed: {completed_count}")
        print(f"   • Total: {total_count}")
        
        # Check servicer assignments
        servicer_id = 32  # John Servicer's ID
        servicer_bookings = db['services_booking'].count_documents({'provider_id': servicer_id})
        servicer_confirmed = db['services_booking'].count_documents({
            'provider_id': servicer_id,
            'status': 'confirmed'
        })
        
        print(f"\n🔧 Servicer Dashboard Status:")
        print(f"   • Total assigned to servicer: {servicer_bookings}")
        print(f"   • Confirmed for servicer: {servicer_confirmed}")
        
        if servicer_confirmed > 0:
            print(f"   ✅ Servicer dashboard should show {servicer_confirmed} bookings")
        else:
            print(f"   ⚠️ Servicer dashboard will be empty")
        
        # Show recent bookings
        if total_count > 0:
            print(f"\n📋 Recent Bookings:")
            recent_bookings = list(db['services_booking'].find({}).sort('created_at', -1).limit(3))
            for booking in recent_bookings:
                booking_id = str(booking['_id'])[:8]
                status = booking.get('status', 'unknown')
                provider_id = booking.get('provider_id', 'None')
                amount = booking.get('total_amount', 0)
                print(f"   • {booking_id}: {status}, Provider={provider_id}, ₹{amount}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking state: {e}")
        return False

def test_servicer_dashboard_query():
    """Test the exact query used by servicer dashboard"""
    print("\n🔍 Testing Servicer Dashboard Query...\n")
    
    try:
        import pymongo
        from django.conf import settings
        
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        servicer_id = 32  # John Servicer's ID
        
        # This is the exact query from servicer dashboard
        servicer_query = {
            'provider_id': servicer_id,
            'status': 'confirmed'
        }
        
        print(f"🔧 Servicer Dashboard Query:")
        print(f"   Query: {servicer_query}")
        
        results = list(db['services_booking'].find(servicer_query))
        print(f"   Results: {len(results)} bookings")
        
        if len(results) > 0:
            print(f"   ✅ Servicer dashboard will show bookings:")
            for booking in results:
                booking_id = str(booking['_id'])[:8]
                notes = booking.get('notes', 'No notes')[:50]
                amount = booking.get('total_amount', 0)
                print(f"     • {booking_id}: ₹{amount} - {notes}...")
        else:
            print(f"   ⚠️ Servicer dashboard will be empty")
            print(f"   💡 Need admin to approve pending bookings")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing query: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Simple Workflow Test\n")
    
    state_success = check_current_state()
    query_success = test_servicer_dashboard_query()
    booking_success = create_test_booking_for_admin()
    
    if state_success and query_success and booking_success:
        print(f"\n🎉 Test Setup Completed Successfully!")
        print(f"\n✅ Summary:")
        print(f"   • Database state checked")
        print(f"   • Servicer dashboard query tested")
        print(f"   • Test booking created for admin approval")
        
        print(f"\n🔄 Complete Workflow Test:")
        print(f"   1. Admin approves pending booking")
        print(f"   2. Booking gets assigned to servicer")
        print(f"   3. Servicer dashboard shows the booking")
        print(f"   4. Servicer marks as completed")
        print(f"   5. User sees green workflow status")
        
        print(f"\n🔗 Test URLs:")
        print(f"   • Admin: http://127.0.0.1:8000/admin-dashboard/")
        print(f"   • Servicer: http://127.0.0.1:8000/servicer-dashboard/")
        print(f"   • Customer: http://127.0.0.1:8000/services/my-bookings/")
    else:
        print(f"\n❌ Test setup failed")
        
    print(f"\n💡 Key Point:")
    print(f"   The servicer dashboard shows bookings with:")
    print(f"   • provider_id = servicer's ID")
    print(f"   • status = 'confirmed' (admin approved)")
    print(f"   Admin approval must assign the provider_id!")
