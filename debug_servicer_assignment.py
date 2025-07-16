#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def debug_servicer_assignment():
    """Debug why servicer dashboard shows no assigned services"""
    print("🔍 Debugging Servicer Assignment Issue...\n")
    
    try:
        from users.models import User
        import pymongo
        from django.conf import settings
        from datetime import datetime, timedelta
        
        # Get users
        try:
            servicer = User.objects.get(email='servicer@example.com')
            customer = User.objects.get(email='test@example.com')
            print(f"✅ Found servicer: {servicer.get_full_name()} (ID: {servicer.id})")
            print(f"✅ Found customer: {customer.get_full_name()} (ID: {customer.id})")
        except User.DoesNotExist as e:
            print(f"❌ User not found: {e}")
            return False
        
        # Connect to MongoDB
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Check all bookings in database
        print(f"\n📊 Database Analysis:")
        
        all_bookings = list(db['services_booking'].find({}))
        print(f"   • Total bookings in database: {len(all_bookings)}")
        
        if len(all_bookings) == 0:
            print(f"   ❌ No bookings found! Need to create test bookings first.")
            
            # Create a test booking
            print(f"\n📝 Creating test booking...")
            
            test_booking = {
                'customer_id': customer.id,
                'provider_id': None,  # No provider initially
                'status': 'pending',
                'total_amount': 2000,
                'booking_date': datetime.now() + timedelta(days=1),
                'address': '123 Test Address, Test City',
                'phone_number': '+91-9876543210',
                'notes': 'Test Service for Servicer Assignment',
                'special_instructions': 'Please test servicer assignment',
                'is_paid': True,
                'payment_status': 'paid',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            booking_result = db['services_booking'].insert_one(test_booking)
            booking_id = booking_result.inserted_id
            
            print(f"   ✅ Created test booking: {str(booking_id)[:8]}")
            print(f"   • Status: pending")
            print(f"   • Provider: None (needs admin approval)")
            
            all_bookings = [test_booking]
        
        # Analyze booking statuses
        status_counts = {}
        provider_assignments = {}
        
        for booking in all_bookings:
            status = booking.get('status', 'unknown')
            provider_id = booking.get('provider_id')
            
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if provider_id:
                provider_assignments[provider_id] = provider_assignments.get(provider_id, 0) + 1
        
        print(f"\n📈 Booking Status Breakdown:")
        for status, count in status_counts.items():
            print(f"   • {status}: {count}")
        
        print(f"\n👥 Provider Assignment Breakdown:")
        if provider_assignments:
            for provider_id, count in provider_assignments.items():
                try:
                    provider = User.objects.get(id=provider_id)
                    print(f"   • {provider.get_full_name()} (ID: {provider_id}): {count} bookings")
                except User.DoesNotExist:
                    print(f"   • Unknown Provider (ID: {provider_id}): {count} bookings")
        else:
            print(f"   • No provider assignments found")
        
        # Check servicer's specific assignments
        print(f"\n🔧 Servicer Dashboard Query:")
        
        servicer_query = {
            'provider_id': servicer.id,
            'status': 'confirmed',
            'is_paid': True
        }
        
        print(f"   Query: {servicer_query}")
        
        servicer_bookings = list(db['services_booking'].find(servicer_query))
        print(f"   Results: {len(servicer_bookings)} bookings")
        
        if len(servicer_bookings) == 0:
            print(f"   ❌ No bookings match servicer dashboard criteria")
            
            # Check what's missing
            print(f"\n🔍 Checking what's missing:")
            
            # Check bookings with servicer as provider
            provider_bookings = list(db['services_booking'].find({'provider_id': servicer.id}))
            print(f"   • Bookings assigned to servicer: {len(provider_bookings)}")
            
            # Check confirmed bookings
            confirmed_bookings = list(db['services_booking'].find({'status': 'confirmed'}))
            print(f"   • Confirmed bookings (any provider): {len(confirmed_bookings)}")
            
            # Check paid bookings
            paid_bookings = list(db['services_booking'].find({'is_paid': True}))
            print(f"   • Paid bookings (any provider): {len(paid_bookings)}")
            
            if len(confirmed_bookings) > 0:
                print(f"\n📋 Confirmed bookings details:")
                for booking in confirmed_bookings:
                    provider_id = booking.get('provider_id', 'None')
                    is_paid = booking.get('is_paid', False)
                    print(f"   • Booking {str(booking['_id'])[:8]}: Provider={provider_id}, Paid={is_paid}")
        else:
            print(f"   ✅ Found {len(servicer_bookings)} bookings for servicer")
            for booking in servicer_bookings:
                print(f"   • Booking {str(booking['_id'])[:8]}: {booking.get('notes', 'No notes')}")
        
        # Test admin approval process
        print(f"\n🔧 Testing Admin Approval Process:")
        
        pending_bookings = list(db['services_booking'].find({'status': 'pending'}))
        print(f"   • Pending bookings: {len(pending_bookings)}")
        
        if len(pending_bookings) > 0:
            test_booking = pending_bookings[0]
            booking_id = test_booking['_id']
            
            print(f"   • Testing approval for booking: {str(booking_id)[:8]}")
            
            # Simulate admin approval with provider assignment
            update_data = {
                'status': 'confirmed',
                'provider_id': servicer.id,
                'approved_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            update_result = db['services_booking'].update_one(
                {'_id': booking_id},
                {'$set': update_data}
            )
            
            if update_result.modified_count > 0:
                print(f"   ✅ Successfully approved and assigned to servicer")
                
                # Create invoice
                invoice_doc = {
                    'booking_id': booking_id,
                    'invoice_number': f"INV-{str(booking_id)[:8].upper()}",
                    'generated_at': datetime.now(),
                    'subtotal': float(test_booking.get('total_amount', 0)),
                    'tax_amount': float(test_booking.get('total_amount', 0)) * 0.18,
                    'total_amount': float(test_booking.get('total_amount', 0)) * 1.18
                }
                
                db['services_invoice'].insert_one(invoice_doc)
                print(f"   ✅ Created invoice: {invoice_doc['invoice_number']}")
                
                # Re-check servicer dashboard
                updated_servicer_bookings = list(db['services_booking'].find(servicer_query))
                print(f"   ✅ Servicer dashboard now shows: {len(updated_servicer_bookings)} bookings")
                
                return True
            else:
                print(f"   ❌ Failed to approve booking")
                return False
        else:
            print(f"   • No pending bookings to approve")
            return True
        
    except Exception as e:
        print(f"❌ Error debugging servicer assignment: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Debugging Servicer Assignment Issue\n")
    
    success = debug_servicer_assignment()
    
    if success:
        print(f"\n🎉 Servicer assignment debugging completed!")
        print(f"\n📱 Next Steps:")
        print(f"   1. Refresh servicer dashboard: http://127.0.0.1:8000/servicer-dashboard/")
        print(f"   2. Should now show assigned services")
        print(f"   3. If still empty, check admin approval process")
    else:
        print(f"\n❌ Servicer assignment debugging failed")
        
    print(f"\n🔗 Test URLs:")
    print(f"   • Admin Dashboard: http://127.0.0.1:8000/admin-dashboard/")
    print(f"   • Servicer Dashboard: http://127.0.0.1:8000/servicer-dashboard/")
    print(f"   • Login: http://127.0.0.1:8000/accounts/login/")
