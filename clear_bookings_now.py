#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def clear_all_bookings_now():
    """Clear all bookings from the database immediately"""
    print("🗑️ Clearing All Bookings from Database...\n")
    
    try:
        import pymongo
        from django.conf import settings
        
        # Connect to MongoDB
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Step 1: Check current count
        print("📊 Current Database Status:")
        mongo_bookings_count = db['services_booking'].count_documents({})
        mongo_invoices_count = db['services_invoice'].count_documents({})
        print(f"   • Bookings: {mongo_bookings_count}")
        print(f"   • Invoices: {mongo_invoices_count}")
        
        if mongo_bookings_count == 0 and mongo_invoices_count == 0:
            print(f"\n✅ Database is already clean - no bookings to delete!")
            return True
        
        # Step 2: Delete all bookings
        print(f"\n🗑️ Deleting All Records...")
        
        # Delete all bookings
        booking_result = db['services_booking'].delete_many({})
        print(f"   ✅ Deleted {booking_result.deleted_count} booking records")
        
        # Delete all invoices
        invoice_result = db['services_invoice'].delete_many({})
        print(f"   ✅ Deleted {invoice_result.deleted_count} invoice records")
        
        # Step 3: Verify deletion
        print(f"\n✅ Verification:")
        remaining_bookings = db['services_booking'].count_documents({})
        remaining_invoices = db['services_invoice'].count_documents({})
        print(f"   • Remaining bookings: {remaining_bookings}")
        print(f"   • Remaining invoices: {remaining_invoices}")
        
        if remaining_bookings == 0 and remaining_invoices == 0:
            print(f"\n🎉 All bookings successfully cleared!")
            
            print(f"\n📊 Dashboard Impact:")
            print(f"   • Admin Dashboard: Recent bookings will show empty")
            print(f"   • User Dashboard: No bookings found")
            print(f"   • Servicer Dashboard: No assigned services")
            print(f"   • Total Revenue: ₹0")
            print(f"   • Booking Count: 0")
            
            print(f"\n🔗 Test Clean State:")
            print(f"   • Admin Dashboard: http://127.0.0.1:8000/admin-dashboard/")
            print(f"   • User Dashboard: http://127.0.0.1:8000/dashboard/")
            print(f"   • Servicer Dashboard: http://127.0.0.1:8000/servicer-dashboard/")
            
            return True
        else:
            print(f"\n⚠️ Some records may still remain")
            return False
        
    except Exception as e:
        print(f"❌ Error clearing bookings: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Clear All Bookings - Quick Script\n")
    
    success = clear_all_bookings_now()
    
    if success:
        print(f"\n🎉 SUCCESS: All bookings have been cleared!")
        print(f"\n💡 Your database is now clean and ready for new bookings.")
        print(f"\n📱 All dashboards will show empty states until new bookings are created.")
    else:
        print(f"\n❌ FAILED: Could not clear all bookings")
        
    print(f"\n🗑️ Booking clearance complete!")
