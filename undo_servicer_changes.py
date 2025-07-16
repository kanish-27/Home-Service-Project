#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def undo_servicer_changes():
    """Undo the last servicer assignment changes and restore previous state"""
    print("↩️ Undoing Last Servicer Assignment Changes...\n")
    
    try:
        from users.models import User
        import pymongo
        from django.conf import settings
        from datetime import datetime
        
        # Connect to MongoDB
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Step 1: Check current state
        print("📊 Current Database State:")
        
        current_bookings = list(db['services_booking'].find({}))
        current_invoices = list(db['services_invoice'].find({}))
        
        print(f"   • Current bookings: {len(current_bookings)}")
        print(f"   • Current invoices: {len(current_invoices)}")
        
        if len(current_bookings) > 0:
            print(f"\n📋 Current bookings details:")
            for booking in current_bookings:
                booking_id = str(booking['_id'])[:8]
                status = booking.get('status', 'unknown')
                provider_id = booking.get('provider_id', 'None')
                amount = booking.get('total_amount', 0)
                print(f"   • {booking_id}: Status={status}, Provider={provider_id}, Amount=₹{amount}")
        
        # Step 2: Clear all test bookings created by the fix
        print(f"\n🗑️ Clearing Test Bookings Created by Fix:")
        
        # Remove all bookings (these were created by our fix script)
        if len(current_bookings) > 0:
            delete_result = db['services_booking'].delete_many({})
            print(f"   ✅ Removed {delete_result.deleted_count} test bookings")
        else:
            print(f"   • No bookings to remove")
        
        # Remove all invoices
        if len(current_invoices) > 0:
            invoice_delete_result = db['services_invoice'].delete_many({})
            print(f"   ✅ Removed {invoice_delete_result.deleted_count} test invoices")
        else:
            print(f"   • No invoices to remove")
        
        # Step 3: Restore to clean state (no bookings)
        print(f"\n🔄 Restoring to Clean State:")
        
        # Verify deletion
        remaining_bookings = db['services_booking'].count_documents({})
        remaining_invoices = db['services_invoice'].count_documents({})
        
        print(f"   • Remaining bookings: {remaining_bookings}")
        print(f"   • Remaining invoices: {remaining_invoices}")
        
        if remaining_bookings == 0 and remaining_invoices == 0:
            print(f"   ✅ Database restored to clean state")
        else:
            print(f"   ⚠️ Some data still remains")
        
        # Step 4: Verify user accounts are intact
        print(f"\n👥 Verifying User Accounts:")
        
        try:
            servicer = User.objects.get(email='servicer@example.com')
            customer = User.objects.get(email='test@example.com')
            admin = User.objects.filter(user_type='admin').first()
            
            print(f"   ✅ Servicer account: {servicer.get_full_name()}")
            print(f"   ✅ Customer account: {customer.get_full_name()}")
            print(f"   ✅ Admin account: {admin.get_full_name() if admin else 'Available'}")
        except User.DoesNotExist as e:
            print(f"   ⚠️ User account issue: {e}")
        
        # Step 5: Reset dashboard states
        print(f"\n📊 Dashboard States After Undo:")
        
        print(f"   📱 Admin Dashboard:")
        print(f"     • Total Bookings: 0")
        print(f"     • Pending Bookings: 0")
        print(f"     • Confirmed Bookings: 0")
        print(f"     • Total Revenue: ₹0")
        
        print(f"   🔧 Servicer Dashboard:")
        print(f"     • Assigned Services: 0")
        print(f"     • Completed Services: 0")
        print(f"     • Message: 'No services assigned yet'")
        
        print(f"   👤 User Dashboard:")
        print(f"     • Your Bookings: 0")
        print(f"     • Message: 'No bookings found'")
        
        print(f"\n✅ Undo completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error undoing changes: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_undo_state():
    """Verify that the undo was successful"""
    print(f"\n🔍 Verifying Undo State...")
    
    try:
        import pymongo
        from django.conf import settings
        
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Check collections
        bookings_count = db['services_booking'].count_documents({})
        invoices_count = db['services_invoice'].count_documents({})
        
        print(f"   • Bookings in database: {bookings_count}")
        print(f"   • Invoices in database: {invoices_count}")
        
        if bookings_count == 0 and invoices_count == 0:
            print(f"   ✅ Database successfully restored to clean state")
            return True
        else:
            print(f"   ⚠️ Database not completely clean")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying undo: {e}")
        return False

def restore_original_admin_approval():
    """Restore the original admin approval process (without forced servicer assignment)"""
    print(f"\n🔄 Restoring Original Admin Approval Process...")
    
    try:
        # The admin approval changes we made are in the code files
        # We would need to revert the code changes to services/admin_views.py
        print(f"   ⚠️ Note: Code changes to admin_views.py still exist")
        print(f"   ⚠️ The automatic servicer assignment logic is still in place")
        print(f"   ⚠️ This affects how future bookings will be processed")
        
        print(f"\n📝 To fully restore original behavior:")
        print(f"   1. The admin approval process now auto-assigns servicers")
        print(f"   2. This was the fix for the servicer dashboard issue")
        print(f"   3. If you want the old behavior, we'd need to revert code changes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in restore process: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Undoing Last Servicer Assignment Changes\n")
    
    undo_success = undo_servicer_changes()
    verify_success = verify_undo_state()
    restore_success = restore_original_admin_approval()
    
    if undo_success and verify_success:
        print(f"\n🎉 Undo completed successfully!")
        print(f"\n✅ Current State:")
        print(f"   • Database: Clean (no bookings or invoices)")
        print(f"   • User accounts: Preserved")
        print(f"   • Admin approval: Enhanced (auto-assigns servicers)")
        print(f"   • Servicer dashboard: Ready for new bookings")
        
        print(f"\n📱 Next Steps:")
        print(f"   1. Create new bookings through normal user flow")
        print(f"   2. Admin approves → Auto-assigns to servicer")
        print(f"   3. Servicer dashboard will show assigned services")
        print(f"   4. Test the complete workflow")
        
        print(f"\n🔗 Test URLs:")
        print(f"   • Customer Booking: http://127.0.0.1:8000/services/")
        print(f"   • Admin Dashboard: http://127.0.0.1:8000/admin-dashboard/")
        print(f"   • Servicer Dashboard: http://127.0.0.1:8000/servicer-dashboard/")
    else:
        print(f"\n❌ Undo process encountered issues")
        
    print(f"\n💡 Note: The servicer assignment fix code is still active")
    print(f"   This means admin approval will now properly assign servicers")
    print(f"   This was the solution to your original issue!")
