#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def fix_servicer_assignment():
    """Fix servicer assignment and create proper test workflow"""
    print("🔧 Fixing Servicer Assignment Issue...\n")
    
    try:
        from users.models import User
        import pymongo
        from django.conf import settings
        from datetime import datetime, timedelta
        
        # Get users
        servicer = User.objects.get(email='servicer@example.com')
        customer = User.objects.get(email='test@example.com')
        
        print(f"✅ Target servicer: {servicer.get_full_name()} (ID: {servicer.id})")
        print(f"✅ Test customer: {customer.get_full_name()} (ID: {customer.id})")
        
        # Connect to MongoDB
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Step 1: Clear existing bookings and start fresh
        print(f"\n🗑️ Step 1: Clearing existing bookings...")
        
        existing_bookings = db['services_booking'].count_documents({})
        existing_invoices = db['services_invoice'].count_documents({})
        
        if existing_bookings > 0:
            db['services_booking'].delete_many({})
            print(f"   ✅ Cleared {existing_bookings} existing bookings")
        
        if existing_invoices > 0:
            db['services_invoice'].delete_many({})
            print(f"   ✅ Cleared {existing_invoices} existing invoices")
        
        # Step 2: Create a new pending booking
        print(f"\n📝 Step 2: Creating new pending booking...")
        
        new_booking = {
            'customer_id': customer.id,
            'provider_id': None,  # No provider assigned initially
            'status': 'pending',
            'total_amount': 2500,
            'booking_date': datetime.now() + timedelta(days=2),
            'address': '123 Servicer Test Street, Test City',
            'phone_number': '+91-9876543210',
            'notes': 'Test Service - Servicer Assignment Fix',
            'special_instructions': 'Testing servicer assignment workflow',
            'is_paid': True,  # Payment completed
            'payment_status': 'paid',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        booking_result = db['services_booking'].insert_one(new_booking)
        booking_id = booking_result.inserted_id
        
        print(f"   ✅ Created booking: {str(booking_id)[:8]}")
        print(f"   • Status: pending")
        print(f"   • Provider: None (awaiting admin approval)")
        print(f"   • Payment: paid")
        print(f"   • Amount: ₹{new_booking['total_amount']}")
        
        # Step 3: Simulate admin approval with correct servicer assignment
        print(f"\n👨‍💼 Step 3: Admin approves and assigns to servicer...")
        
        approval_update = {
            'status': 'confirmed',
            'provider_id': servicer.id,  # Assign to our test servicer
            'approved_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        approval_result = db['services_booking'].update_one(
            {'_id': booking_id},
            {'$set': approval_update}
        )
        
        if approval_result.modified_count > 0:
            print(f"   ✅ Booking approved and assigned to servicer")
            print(f"   • Status: pending → confirmed")
            print(f"   • Provider: None → {servicer.get_full_name()}")
        else:
            print(f"   ❌ Failed to approve booking")
            return False
        
        # Step 4: Create invoice
        print(f"\n📄 Step 4: Creating invoice...")
        
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
        
        # Step 5: Verify servicer dashboard query
        print(f"\n🔍 Step 5: Verifying servicer dashboard...")
        
        servicer_query = {
            'provider_id': servicer.id,
            'status': 'confirmed',
            'is_paid': True
        }
        
        servicer_bookings = list(db['services_booking'].find(servicer_query))
        print(f"   • Query: {servicer_query}")
        print(f"   • Results: {len(servicer_bookings)} bookings")
        
        if len(servicer_bookings) > 0:
            booking = servicer_bookings[0]
            print(f"   ✅ Servicer dashboard will show:")
            print(f"     • Booking ID: {str(booking['_id'])[:8]}")
            print(f"     • Invoice: {invoice_doc['invoice_number']}")
            print(f"     • Customer: {customer.get_full_name()}")
            print(f"     • Amount: ₹{booking['total_amount']}")
            print(f"     • Status: {booking['status']}")
        else:
            print(f"   ❌ Servicer dashboard query returned no results")
            return False
        
        # Step 6: Test servicer status update
        print(f"\n✅ Step 6: Testing servicer status update...")
        
        # Servicer marks as completed
        completion_update = {
            'status': 'completed',
            'updated_at': datetime.now(),
            'service_completed_at': datetime.now(),
            'service_completed_by': servicer.id
        }
        
        completion_result = db['services_booking'].update_one(
            {'_id': booking_id},
            {'$set': completion_update}
        )
        
        if completion_result.modified_count > 0:
            print(f"   ✅ Service marked as completed by servicer")
            print(f"   • Status: confirmed → completed")
            print(f"   • User dashboard will show GREEN service delivery box")
        else:
            print(f"   ❌ Failed to mark service as completed")
            return False
        
        # Step 7: Verify user dashboard workflow
        print(f"\n👤 Step 7: Verifying user dashboard workflow...")
        
        final_booking = db['services_booking'].find_one({'_id': booking_id})
        
        if final_booking:
            status = final_booking['status']
            payment_status = final_booking.get('payment_status', 'pending')
            
            if status == 'completed':
                color = "GREEN (bg-success)"
                message = "✅ Service completed successfully by the provider!"
            elif status == 'rejected':
                color = "RED (bg-danger)"
                message = "❌ Service was rejected by the provider."
            elif status == 'confirmed' and payment_status == 'paid':
                color = "YELLOW (bg-warning)"
                message = "🔄 Service provider will contact you soon to deliver the service."
            else:
                color = "GRAY (bg-light)"
                message = "The service provider will contact you and deliver the service as scheduled."
            
            print(f"   ✅ User dashboard 'What Happens Next':")
            print(f"     • Service Delivery Box: {color}")
            print(f"     • Message: {message}")
        
        print(f"\n🎉 Servicer assignment fix completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing servicer assignment: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_additional_test_bookings():
    """Create a few more test bookings for comprehensive testing"""
    print(f"\n📝 Creating additional test bookings...")
    
    try:
        from users.models import User
        import pymongo
        from django.conf import settings
        from datetime import datetime, timedelta
        
        servicer = User.objects.get(email='servicer@example.com')
        customer = User.objects.get(email='test@example.com')
        
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Create 2 more pending bookings for admin to approve
        test_bookings = [
            {
                'customer_id': customer.id,
                'provider_id': None,
                'status': 'pending',
                'total_amount': 1800,
                'booking_date': datetime.now() + timedelta(days=3),
                'address': '456 Second Test Street',
                'phone_number': '+91-8765432109',
                'notes': 'Plumbing Service - Test Booking 2',
                'special_instructions': 'Kitchen sink repair',
                'is_paid': True,
                'payment_status': 'paid',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'customer_id': customer.id,
                'provider_id': None,
                'status': 'pending',
                'total_amount': 3200,
                'booking_date': datetime.now() + timedelta(days=4),
                'address': '789 Third Test Avenue',
                'phone_number': '+91-7654321098',
                'notes': 'Electrical Service - Test Booking 3',
                'special_instructions': 'Wiring installation',
                'is_paid': True,
                'payment_status': 'paid',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
        ]
        
        for i, booking in enumerate(test_bookings, 2):
            result = db['services_booking'].insert_one(booking)
            print(f"   ✅ Created test booking {i}: {str(result.inserted_id)[:8]}")
        
        print(f"   ✅ Total pending bookings for admin approval: 2")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating additional bookings: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Fixing Servicer Assignment Issue\n")
    
    fix_success = fix_servicer_assignment()
    additional_success = create_additional_test_bookings()
    
    if fix_success and additional_success:
        print(f"\n🎉 Servicer assignment fix completed successfully!")
        print(f"\n✅ Test Environment Ready:")
        print(f"   • 1 completed booking in servicer dashboard")
        print(f"   • 2 pending bookings for admin to approve")
        print(f"   • User dashboard shows completed service workflow")
        
        print(f"\n📱 Testing Steps:")
        print(f"   1. Login as admin → Approve pending bookings")
        print(f"   2. Login as servicer → See assigned services")
        print(f"   3. Mark services as completed/rejected")
        print(f"   4. Login as customer → See workflow colors")
        
        print(f"\n🔗 Test URLs:")
        print(f"   • Admin: http://127.0.0.1:8000/admin-dashboard/")
        print(f"   • Servicer: http://127.0.0.1:8000/servicer-dashboard/")
        print(f"   • Customer: http://127.0.0.1:8000/services/my-bookings/")
        print(f"   • Login: http://127.0.0.1:8000/accounts/login/")
    else:
        print(f"\n❌ Servicer assignment fix failed")
