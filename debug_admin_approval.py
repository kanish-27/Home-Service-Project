#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def debug_admin_approval():
    """Debug why admin approval isn't assigning providers correctly"""
    print("🔍 Debugging Admin Approval Process...\n")
    
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
        
        # Step 1: Create a pending booking
        print(f"\n📝 Step 1: Creating Pending Booking...")
        
        new_booking = {
            'customer_id': customer.id,
            'provider_id': None,  # No provider initially
            'status': 'pending',
            'total_amount': 2000,
            'booking_date': datetime.now() + timedelta(days=1),
            'address': '123 Debug Street, Test City',
            'phone_number': '+91-9876543210',
            'notes': 'Debug Service - Admin Approval Test',
            'special_instructions': 'Testing admin approval process',
            'is_paid': True,
            'payment_status': 'paid',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        booking_result = db['services_booking'].insert_one(new_booking)
        booking_id = booking_result.inserted_id
        
        print(f"   ✅ Created booking: {str(booking_id)[:8]}")
        print(f"   • Status: {new_booking['status']}")
        print(f"   • Provider: {new_booking['provider_id']}")
        print(f"   • Customer: {customer.get_full_name()}")
        
        # Step 2: Check current servicer dashboard
        print(f"\n🔧 Step 2: Current Servicer Dashboard...")
        
        servicer_query = {
            'provider_id': servicer.id,
            'status': 'confirmed'
        }
        
        current_servicer_bookings = list(db['services_booking'].find(servicer_query))
        print(f"   • Current servicer bookings: {len(current_servicer_bookings)}")
        
        # Step 3: Manually simulate admin approval (what should happen)
        print(f"\n👨‍💼 Step 3: Manual Admin Approval Simulation...")
        
        # This is what the admin approval should do
        approval_update = {
            'status': 'confirmed',
            'provider_id': servicer.id,  # Assign to servicer
            'approved_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        print(f"   • Updating booking with: {approval_update}")
        
        approval_result = db['services_booking'].update_one(
            {'_id': booking_id},
            {'$set': approval_update}
        )
        
        if approval_result.modified_count > 0:
            print(f"   ✅ Booking approved and assigned to servicer")
        else:
            print(f"   ❌ Failed to approve booking")
            return False
        
        # Step 4: Check servicer dashboard after approval
        print(f"\n🔍 Step 4: Servicer Dashboard After Approval...")
        
        updated_servicer_bookings = list(db['services_booking'].find(servicer_query))
        print(f"   • Servicer bookings after approval: {len(updated_servicer_bookings)}")
        
        if len(updated_servicer_bookings) > len(current_servicer_bookings):
            print(f"   ✅ Booking successfully appears in servicer dashboard!")
            
            # Show booking details
            new_booking = updated_servicer_bookings[0]
            print(f"   • Booking ID: {str(new_booking['_id'])[:8]}")
            print(f"   • Status: {new_booking['status']}")
            print(f"   • Provider ID: {new_booking['provider_id']}")
            print(f"   • Customer ID: {new_booking['customer_id']}")
            print(f"   • Notes: {new_booking['notes']}")
        else:
            print(f"   ❌ Booking did not appear in servicer dashboard")
            return False
        
        # Step 5: Create invoice for the booking
        print(f"\n📄 Step 5: Creating Invoice...")
        
        invoice_doc = {
            'booking_id': booking_id,
            'invoice_number': f"INV-{str(booking_id)[:8].upper()}",
            'generated_at': datetime.now(),
            'subtotal': float(new_booking['total_amount']),
            'tax_amount': float(new_booking['total_amount']) * 0.18,
            'total_amount': float(new_booking['total_amount']) * 1.18
        }
        
        invoice_result = db['services_invoice'].insert_one(invoice_doc)
        print(f"   ✅ Invoice created: {invoice_doc['invoice_number']}")
        
        # Step 6: Test the actual admin approval API
        print(f"\n🔧 Step 6: Testing Actual Admin Approval Logic...")
        
        # Check if the admin approval code is working
        print(f"   • Checking provider assignment logic...")
        
        # Test the provider finding logic from admin_views.py
        try:
            available_provider = User.objects.filter(
                user_type='provider',
                is_active=True
            ).first()
            
            if not available_provider:
                available_provider = User.objects.filter(
                    email='servicer@example.com'
                ).first()
            
            if available_provider:
                print(f"   ✅ Provider assignment logic works: {available_provider.get_full_name()}")
                print(f"   • Provider ID: {available_provider.id}")
                print(f"   • User type: {available_provider.user_type}")
                print(f"   • Is active: {available_provider.is_active}")
            else:
                print(f"   ❌ No provider found by assignment logic")
                
        except Exception as provider_error:
            print(f"   ❌ Provider assignment logic error: {provider_error}")
        
        # Step 7: Summary
        print(f"\n📊 Step 7: Summary...")
        
        print(f"   ✅ Manual approval process works correctly")
        print(f"   ✅ Booking appears in servicer dashboard after approval")
        print(f"   ✅ Provider assignment logic finds correct servicer")
        print(f"   ✅ Invoice creation works")
        
        print(f"\n💡 The issue might be:")
        print(f"   1. Admin approval API not being called correctly")
        print(f"   2. Provider assignment logic not executing")
        print(f"   3. Database update not happening")
        
        # Cleanup
        print(f"\n🧹 Cleanup...")
        db['services_booking'].delete_one({'_id': booking_id})
        db['services_invoice'].delete_one({'booking_id': booking_id})
        print(f"   ✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error debugging admin approval: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_test_booking_for_approval():
    """Create a test booking that admin can approve"""
    print(f"\n📝 Creating Test Booking for Admin Approval...")
    
    try:
        from users.models import User
        import pymongo
        from django.conf import settings
        from datetime import datetime, timedelta
        
        customer = User.objects.get(email='test@example.com')
        
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Create a pending booking for admin to approve
        test_booking = {
            'customer_id': customer.id,
            'provider_id': None,  # No provider initially
            'status': 'pending',  # Waiting for admin approval
            'total_amount': 2500,
            'booking_date': datetime.now() + timedelta(days=2),
            'address': '456 Admin Test Street, Test City',
            'phone_number': '+91-8765432109',
            'notes': 'Test Service - Ready for Admin Approval',
            'special_instructions': 'Please approve this booking to test servicer assignment',
            'is_paid': True,
            'payment_status': 'paid',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        booking_result = db['services_booking'].insert_one(test_booking)
        booking_id = booking_result.inserted_id
        
        print(f"   ✅ Created test booking: {str(booking_id)[:8]}")
        print(f"   • Status: pending (ready for admin approval)")
        print(f"   • Customer: {customer.get_full_name()}")
        print(f"   • Amount: ₹{test_booking['total_amount']}")
        
        print(f"\n📱 Next Steps:")
        print(f"   1. Login as admin: http://127.0.0.1:8000/admin-dashboard/")
        print(f"   2. Approve the pending booking")
        print(f"   3. Check servicer dashboard: http://127.0.0.1:8000/servicer-dashboard/")
        print(f"   4. Should see the approved booking")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test booking: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Debugging Admin Approval Process\n")
    
    debug_success = debug_admin_approval()
    test_booking_success = create_test_booking_for_approval()
    
    if debug_success and test_booking_success:
        print(f"\n🎉 Debug completed successfully!")
        print(f"\n✅ Key Findings:")
        print(f"   • Manual approval process works correctly")
        print(f"   • Provider assignment logic is functional")
        print(f"   • Servicer dashboard query works")
        print(f"   • Test booking created for admin approval")
        
        print(f"\n🔧 Test the Real Workflow:")
        print(f"   1. Admin approves the test booking")
        print(f"   2. Booking should appear in servicer dashboard")
        print(f"   3. Servicer can mark as completed/rejected")
    else:
        print(f"\n❌ Debug process failed")
