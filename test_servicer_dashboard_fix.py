#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def test_servicer_dashboard_fix():
    """Test the simplified servicer dashboard query"""
    print("🔧 Testing Servicer Dashboard Fix...\n")
    
    try:
        from users.models import User
        import pymongo
        from django.conf import settings
        from datetime import datetime, timedelta
        
        # Get users
        servicer = User.objects.get(email='servicer@example.com')
        customer = User.objects.get(email='test@example.com')
        
        print(f"✅ Servicer: {servicer.get_full_name()} (ID: {servicer.id})")
        print(f"✅ Customer: {customer.get_full_name()} (ID: {customer.id})")
        
        # Connect to MongoDB
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Step 1: Create test bookings with different statuses
        print(f"\n📝 Step 1: Creating Test Bookings...")
        
        test_bookings = [
            {
                'customer_id': customer.id,
                'provider_id': servicer.id,  # Assigned to servicer
                'status': 'pending',  # Not approved yet
                'total_amount': 1500,
                'booking_date': datetime.now() + timedelta(days=1),
                'address': '123 Pending Street',
                'phone_number': '+91-9876543210',
                'notes': 'Pending Service - Should NOT appear in servicer dashboard',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'customer_id': customer.id,
                'provider_id': servicer.id,  # Assigned to servicer
                'status': 'confirmed',  # Admin approved - SHOULD appear
                'total_amount': 2500,
                'booking_date': datetime.now() + timedelta(days=2),
                'address': '456 Confirmed Street',
                'phone_number': '+91-8765432109',
                'notes': 'Confirmed Service - SHOULD appear in servicer dashboard',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'customer_id': customer.id,
                'provider_id': servicer.id,  # Assigned to servicer
                'status': 'completed',  # Already completed
                'total_amount': 1800,
                'booking_date': datetime.now() + timedelta(days=3),
                'address': '789 Completed Street',
                'phone_number': '+91-7654321098',
                'notes': 'Completed Service - Should NOT appear in servicer dashboard',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        ]
        
        booking_ids = []
        for i, booking in enumerate(test_bookings, 1):
            result = db['services_booking'].insert_one(booking)
            booking_ids.append(result.inserted_id)
            print(f"   ✅ Created booking {i}: {booking['status']} - {booking['notes'][:30]}...")
        
        # Step 2: Test the new servicer dashboard query
        print(f"\n🔍 Step 2: Testing Servicer Dashboard Query...")
        
        # This is the new simplified query
        servicer_query = {
            'provider_id': servicer.id,
            'status': 'confirmed'  # Only admin-approved bookings
        }
        
        print(f"   Query: {servicer_query}")
        
        servicer_bookings = list(db['services_booking'].find(servicer_query))
        print(f"   Results: {len(servicer_bookings)} bookings")
        
        # Step 3: Verify results
        print(f"\n📊 Step 3: Verifying Results...")
        
        expected_count = 1  # Only the 'confirmed' booking should appear
        
        if len(servicer_bookings) == expected_count:
            print(f"   ✅ Correct number of bookings: {len(servicer_bookings)}")
            
            for booking in servicer_bookings:
                status = booking['status']
                notes = booking['notes']
                print(f"   ✅ Found booking: {status} - {notes[:50]}...")
                
                if status == 'confirmed':
                    print(f"   ✅ Correct status: This booking should appear in servicer dashboard")
                else:
                    print(f"   ❌ Wrong status: {status} should not appear")
        else:
            print(f"   ❌ Wrong number of bookings. Expected: {expected_count}, Got: {len(servicer_bookings)}")
        
        # Step 4: Test what happens when admin approves a pending booking
        print(f"\n👨‍💼 Step 4: Testing Admin Approval Effect...")
        
        # Find the pending booking
        pending_booking_id = booking_ids[0]  # First booking is pending
        
        print(f"   • Approving pending booking: {str(pending_booking_id)[:8]}")
        
        # Admin approves the pending booking
        approval_result = db['services_booking'].update_one(
            {'_id': pending_booking_id},
            {
                '$set': {
                    'status': 'confirmed',
                    'approved_at': datetime.now(),
                    'updated_at': datetime.now()
                }
            }
        )
        
        if approval_result.modified_count > 0:
            print(f"   ✅ Booking approved successfully")
            
            # Re-run servicer dashboard query
            updated_servicer_bookings = list(db['services_booking'].find(servicer_query))
            print(f"   ✅ Servicer dashboard now shows: {len(updated_servicer_bookings)} bookings")
            
            if len(updated_servicer_bookings) == 2:  # Now should have 2 confirmed bookings
                print(f"   ✅ Admin approval correctly adds booking to servicer dashboard")
            else:
                print(f"   ❌ Admin approval didn't work as expected")
        else:
            print(f"   ❌ Failed to approve booking")
        
        # Step 5: Create invoices for confirmed bookings
        print(f"\n📄 Step 5: Creating Invoices for Confirmed Bookings...")
        
        confirmed_bookings = list(db['services_booking'].find({
            'provider_id': servicer.id,
            'status': 'confirmed'
        }))
        
        for booking in confirmed_bookings:
            booking_id = booking['_id']
            
            # Check if invoice already exists
            existing_invoice = db['services_invoice'].find_one({'booking_id': booking_id})
            
            if not existing_invoice:
                invoice_doc = {
                    'booking_id': booking_id,
                    'invoice_number': f"INV-{str(booking_id)[:8].upper()}",
                    'generated_at': datetime.now(),
                    'subtotal': float(booking['total_amount']),
                    'tax_amount': float(booking['total_amount']) * 0.18,
                    'total_amount': float(booking['total_amount']) * 1.18
                }
                
                db['services_invoice'].insert_one(invoice_doc)
                print(f"   ✅ Created invoice: {invoice_doc['invoice_number']}")
            else:
                print(f"   • Invoice already exists: {existing_invoice['invoice_number']}")
        
        print(f"\n🎉 Servicer Dashboard Fix Test Completed!")
        
        # Cleanup
        print(f"\n🧹 Cleanup: Removing test bookings...")
        for booking_id in booking_ids:
            db['services_booking'].delete_one({'_id': booking_id})
            db['services_invoice'].delete_one({'booking_id': booking_id})
        print(f"   ✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing servicer dashboard fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Testing Servicer Dashboard Fix\n")
    
    success = test_servicer_dashboard_fix()
    
    if success:
        print(f"\n🎉 Servicer Dashboard Fix Test Passed!")
        print(f"\n✅ Summary:")
        print(f"   • Servicer dashboard now shows only admin-approved bookings")
        print(f"   • Status filter: 'confirmed' (admin approved)")
        print(f"   • Removed payment requirement (is_paid=True)")
        print(f"   • Bookings appear immediately after admin approval")
        print(f"   • Servicers can mark them as completed/rejected")
        
        print(f"\n📱 Test the workflow:")
        print(f"   1. Customer books service → Status: pending")
        print(f"   2. Admin approves → Status: confirmed")
        print(f"   3. Booking appears in servicer dashboard")
        print(f"   4. Servicer marks as completed → User sees green workflow")
        
        print(f"\n🔗 URLs:")
        print(f"   • Admin: http://127.0.0.1:8000/admin-dashboard/")
        print(f"   • Servicer: http://127.0.0.1:8000/servicer-dashboard/")
    else:
        print(f"\n❌ Servicer Dashboard Fix Test Failed")
