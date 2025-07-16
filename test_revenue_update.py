#!/usr/bin/env python
"""
Test script to create a new booking and test the revenue update workflow
"""
import pymongo
from datetime import datetime, timedelta
from bson import ObjectId

def create_test_booking():
    """Create a new test booking to test the approval workflow"""
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['homeservice_db']
        bookings_collection = db['services_booking']
        users_collection = db['users_user']
        
        print("🧪 CREATING TEST BOOKING FOR REVENUE UPDATE TEST")
        print("=" * 60)
        
        # Find admin and customer users
        admin_user = users_collection.find_one({'user_type': 'admin'})
        customer_user = users_collection.find_one({'user_type': 'customer'})
        
        if not admin_user or not customer_user:
            print("❌ Admin or customer user not found!")
            return
        
        # Create a new test booking
        new_booking = {
            'customer_id': customer_user['_id'],
            'provider_id': admin_user['_id'],  # Using admin as provider for simplicity
            'service_id': None,
            'status': 'pending',  # Start as pending
            'booking_date': datetime.now() + timedelta(days=3),
            'total_amount': 1500.0,  # ₹1,500 test amount
            'address': '123 Test Street, Test City, India',
            'phone_number': '9999999999',
            'notes': 'Test booking for revenue update verification',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'payment_status': 'pending',
            'is_paid': False  # Start as unpaid
        }
        
        # Insert the booking
        result = bookings_collection.insert_one(new_booking)
        booking_id = result.inserted_id
        
        print(f"✅ Created test booking: {booking_id}")
        print(f"   Customer: {customer_user.get('email', 'Unknown')}")
        print(f"   Amount: ₹{new_booking['total_amount']}")
        print(f"   Status: {new_booking['status']}")
        print(f"   Paid: {new_booking['is_paid']}")
        
        print(f"\n🎯 TEST WORKFLOW:")
        print(f"   1. Go to: http://127.0.0.1:8000/services/admin-pending-bookings/")
        print(f"   2. Approve the new booking (₹1,500)")
        print(f"   3. Mark it as paid using the script below")
        print(f"   4. Check dashboard - revenue should increase by ₹1,500")
        
        print(f"\n💰 TO MARK AS PAID (run this after approval):")
        print(f"   python mark_booking_paid.py {booking_id}")
        
        # Create a script to mark this specific booking as paid
        mark_paid_script = f'''#!/usr/bin/env python
import pymongo
from datetime import datetime

def mark_booking_paid():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['homeservice_db']
    bookings_collection = db['services_booking']
    
    from bson import ObjectId
    booking_id = ObjectId('{booking_id}')
    
    result = bookings_collection.update_one(
        {{'_id': booking_id}},
        {{
            '$set': {{
                'is_paid': True,
                'payment_status': 'paid',
                'payment_method': 'test_payment',
                'paid_at': datetime.now(),
                'updated_at': datetime.now()
            }}
        }}
    )
    
    if result.modified_count > 0:
        print(f"✅ Marked booking {{booking_id}} as paid!")
        print(f"🔄 Refresh dashboard to see revenue increase by ₹1,500")
    else:
        print(f"❌ Failed to mark booking as paid")

if __name__ == '__main__':
    mark_booking_paid()
'''
        
        with open('mark_booking_paid.py', 'w') as f:
            f.write(mark_paid_script)
        
        print(f"\n📝 Created helper script: mark_booking_paid.py")
        
        # Show current stats
        total_bookings = bookings_collection.count_documents({})
        pending_bookings = bookings_collection.count_documents({'status': 'pending'})
        
        print(f"\n📊 CURRENT STATS:")
        print(f"   Total bookings: {total_bookings}")
        print(f"   Pending bookings: {pending_bookings}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_test_booking()
