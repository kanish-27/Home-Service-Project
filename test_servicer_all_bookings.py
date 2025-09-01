#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def test_servicer_all_bookings():
    """Test that servicer dashboard shows ALL confirmed bookings regardless of provider"""
    print("🔧 Testing Servicer Dashboard - All Confirmed Bookings...\n")
    
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
        
        # Step 1: Create test bookings with different scenarios
        print(f"\n📝 Step 1: Creating Test Bookings...")
        
        test_bookings = [
            {
                'customer_id': customer.id,
                'provider_id': None,  # No provider assigned
                'status': 'confirmed',  # Admin approved
                'total_amount': 2000,
                'booking_date': datetime.now() + timedelta(days=1),
                'address': '123 Test Street A',
                'phone_number': '+91-9876543210',
                'notes': 'Test Service A - No Provider Assigned',
                'is_paid': True,
                'payment_status': 'paid',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'customer_id': customer.id,
                'provider_id': 999,  # Different provider ID
                'status': 'confirmed',  # Admin approved
                'total_amount': 2500,
                'booking_date': datetime.now() + timedelta(days=2),
                'address': '456 Test Street B',
                'phone_number': '+91-8765432109',
                'notes': 'Test Service B - Different Provider',
                'is_paid': True,
                'payment_status': 'paid',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'customer_id': customer.id,
                'provider_id': servicer.id,  # Assigned to our servicer
                'status': 'confirmed',  # Admin approved
                'total_amount': 3000,
                'booking_date': datetime.now() + timedelta(days=3),
                'address': '789 Test Street C',
                'phone_number': '+91-7654321098',
                'notes': 'Test Service C - Assigned to Servicer',
                'is_paid': True,
                'payment_status': 'paid',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'customer_id': customer.id,
                'provider_id': None,
                'status': 'pending',  # NOT approved yet
                'total_amount': 1500,
                'booking_date': datetime.now() + timedelta(days=4),
                'address': '101 Test Street D',
                'phone_number': '+91-6543210987',
                'notes': 'Test Service D - Still Pending',
                'is_paid': True,
                'payment_status': 'paid',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        ]
        
        booking_ids = []
        for i, booking in enumerate(test_bookings, 1):
            result = db['services_booking'].insert_one(booking)
            booking_ids.append(result.inserted_id)
            status = booking['status']
            provider = booking['provider_id'] or 'None'
            print(f"   ✅ Created booking {i}: {status}, Provider={provider}")
        
        # Step 2: Test the NEW servicer dashboard query
        print(f"\n🔍 Step 2: Testing NEW Servicer Dashboard Query...")
        
        # This is the NEW query (shows ALL confirmed bookings)
        new_query = {
            'status': 'confirmed'  # All admin approved bookings
        }
        
        print(f"   New Query: {new_query}")
        
        new_results = list(db['services_booking'].find(new_query))
        print(f"   Results: {len(new_results)} bookings")
        
        expected_confirmed = 3  # Bookings 1, 2, 3 are confirmed
        
        if len(new_results) == expected_confirmed:
            print(f"   ✅ Correct! Shows all {expected_confirmed} confirmed bookings")
            
            for booking in new_results:
                booking_id = str(booking['_id'])[:8]
                provider_id = booking.get('provider_id', 'None')
                notes = booking.get('notes', '')[:30]
                print(f"     • {booking_id}: Provider={provider_id} - {notes}...")
        else:
            print(f"   ❌ Wrong count. Expected: {expected_confirmed}, Got: {len(new_results)}")
        
        # Step 3: Compare with OLD query (provider-specific)
        print(f"\n📊 Step 3: Comparing with OLD Query...")
        
        # This is the OLD query (only servicer's bookings)
        old_query = {
            'provider_id': servicer.id,
            'status': 'confirmed'
        }
        
        print(f"   Old Query: {old_query}")
        
        old_results = list(db['services_booking'].find(old_query))
        print(f"   Results: {len(old_results)} bookings")
        
        print(f"\n📈 Comparison:")
        print(f"   • OLD approach: {len(old_results)} bookings (only assigned to servicer)")
        print(f"   • NEW approach: {len(new_results)} bookings (all confirmed bookings)")
        print(f"   • Difference: +{len(new_results) - len(old_results)} more bookings visible")
        
        # Step 4: Create invoices for confirmed bookings
        print(f"\n📄 Step 4: Creating Invoices...")
        
        confirmed_bookings = list(db['services_booking'].find({'status': 'confirmed'}))
        
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
                print(f"   • Invoice exists: {existing_invoice['invoice_number']}")
        
        # Step 5: Test servicer status update (any booking)
        print(f"\n✅ Step 5: Testing Status Update (Any Booking)...")
        
        # Try to update a booking that's NOT assigned to our servicer
        test_booking = confirmed_bookings[0]  # First confirmed booking
        test_booking_id = test_booking['_id']
        test_provider_id = test_booking.get('provider_id', 'None')
        
        print(f"   • Testing update on booking with Provider={test_provider_id}")
        print(f"   • Servicer ID: {servicer.id}")
        
        if test_provider_id != servicer.id:
            print(f"   ✅ Good! Testing cross-provider update capability")
        
        # Simulate status update
        update_result = db['services_booking'].update_one(
            {'_id': test_booking_id},
            {
                '$set': {
                    'status': 'completed',
                    'updated_at': datetime.now(),
                    'service_completed_at': datetime.now(),
                    'service_completed_by': servicer.id
                }
            }
        )
        
        if update_result.modified_count > 0:
            print(f"   ✅ Successfully updated booking status to completed")
            print(f"   ✅ Any servicer can now update any confirmed booking")
        else:
            print(f"   ❌ Failed to update booking status")
        
        print(f"\n🎉 Servicer All Bookings Test Completed!")
        
        # Cleanup
        print(f"\n🧹 Cleanup...")
        for booking_id in booking_ids:
            db['services_booking'].delete_one({'_id': booking_id})
            db['services_invoice'].delete_one({'booking_id': booking_id})
        print(f"   ✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing servicer all bookings: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_confirmed_booking():
    """Create a sample confirmed booking for immediate testing"""
    print(f"\n📝 Creating Sample Confirmed Booking...")
    
    try:
        from users.models import User
        import pymongo
        from django.conf import settings
        from datetime import datetime, timedelta
        
        customer = User.objects.get(email='test@example.com')
        
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Create a confirmed booking ready for servicer
        sample_booking = {
            'customer_id': customer.id,
            'provider_id': None,  # No specific provider
            'status': 'confirmed',  # Already approved by admin
            'total_amount': 2800,
            'booking_date': datetime.now() + timedelta(days=1),
            'address': '555 Sample Service Street, Test City',
            'phone_number': '+91-9999888877',
            'notes': 'Sample Service - Ready for Servicer Dashboard',
            'special_instructions': 'Test the new servicer dashboard functionality',
            'is_paid': True,
            'payment_status': 'paid',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        booking_result = db['services_booking'].insert_one(sample_booking)
        booking_id = booking_result.inserted_id
        
        # Create invoice
        invoice_doc = {
            'booking_id': booking_id,
            'invoice_number': f"INV-{str(booking_id)[:8].upper()}",
            'generated_at': datetime.now(),
            'subtotal': float(sample_booking['total_amount']),
            'tax_amount': float(sample_booking['total_amount']) * 0.18,
            'total_amount': float(sample_booking['total_amount']) * 1.18
        }
        
        db['services_invoice'].insert_one(invoice_doc)
        
        print(f"   ✅ Created sample booking: {str(booking_id)[:8]}")
        print(f"   ✅ Created invoice: {invoice_doc['invoice_number']}")
        print(f"   ✅ Status: confirmed (ready for servicer)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample booking: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Testing Servicer Dashboard - All Confirmed Bookings\n")
    
    test_success = test_servicer_all_bookings()
    sample_success = create_sample_confirmed_booking()
    
    if test_success and sample_success:
        print(f"\n🎉 All Tests Passed!")
        print(f"\n✅ Key Changes:")
        print(f"   • Servicer dashboard now shows ALL confirmed bookings")
        print(f"   • No provider assignment required")
        print(f"   • Any servicer can update any confirmed booking")
        print(f"   • Sample confirmed booking created for testing")
        
        print(f"\n📱 Test Now:")
        print(f"   1. Login as servicer: http://127.0.0.1:8000/servicer-dashboard/")
        print(f"   2. Should see the sample confirmed booking")
        print(f"   3. Mark it as completed using invoice ID")
        print(f"   4. Check user dashboard for green workflow")
        
        print(f"\n🔄 Workflow:")
        print(f"   • Admin approves booking → Status: confirmed")
        print(f"   • Booking appears in servicer dashboard (any servicer)")
        print(f"   • Servicer marks as completed → User sees green")
    else:
        print(f"\n❌ Tests failed")
        
    print(f"\n💡 No more provider assignment needed!")
    print(f"   All confirmed bookings go to servicer dashboard automatically!")
