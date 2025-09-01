#!/usr/bin/env python
"""
Simple script to check booking data directly from MongoDB
"""
import pymongo
from datetime import datetime

def check_bookings():
    """Check booking data directly from MongoDB"""
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['homeservice_db']
        bookings_collection = db['services_booking']
        
        print("🔍 CHECKING BOOKING DATA DIRECTLY FROM MONGODB")
        print("=" * 60)
        
        # Get all bookings
        all_bookings = list(bookings_collection.find())
        print(f"📊 Total Bookings: {len(all_bookings)}")
        
        if not all_bookings:
            print("❌ No bookings found in database!")
            return
        
        # Check each booking
        confirmed_count = 0
        paid_count = 0
        confirmed_and_paid_count = 0
        total_revenue = 0
        
        print(f"\n📋 Booking Details:")
        print("-" * 60)
        
        for i, booking in enumerate(all_bookings, 1):
            booking_id = str(booking.get('_id', 'N/A'))
            status = booking.get('status', 'unknown')
            is_paid = booking.get('is_paid', False)
            payment_status = booking.get('payment_status', 'unknown')
            total_amount = booking.get('total_amount', 0)
            
            print(f"{i}. ID: {booking_id[:8]}...")
            print(f"   Status: {status}")
            print(f"   Is Paid: {is_paid}")
            print(f"   Payment Status: {payment_status}")
            print(f"   Amount: ₹{total_amount}")
            
            # Count statistics
            if status in ['confirmed', 'completed']:
                confirmed_count += 1
                
            if is_paid:
                paid_count += 1
                
            if status in ['confirmed', 'completed'] and is_paid:
                confirmed_and_paid_count += 1
                total_revenue += float(total_amount) if total_amount else 0
            
            print("-" * 40)
        
        print(f"\n📈 STATISTICS:")
        print(f"   ✅ Confirmed/Completed: {confirmed_count}")
        print(f"   💰 Paid: {paid_count}")
        print(f"   🎯 Confirmed AND Paid: {confirmed_and_paid_count}")
        print(f"   💵 Total Revenue: ₹{total_revenue}")
        
        print(f"\n🔧 SOLUTION:")
        if confirmed_count > 0 and paid_count == 0:
            print("   ❌ Bookings are approved but not marked as paid!")
            print("   📝 You need to:")
            print("   1. Go to payment page for each booking")
            print("   2. Complete the payment process")
            print("   3. Then revenue will show in dashboard")
        elif confirmed_count > 0 and paid_count > 0 and confirmed_and_paid_count == 0:
            print("   ❌ Some bookings are approved, some are paid, but none are BOTH!")
            print("   📝 Each booking needs to be both approved AND paid")
        elif confirmed_and_paid_count > 0:
            print("   ✅ Revenue should be showing in dashboard!")
            print(f"   💰 Expected revenue: ₹{total_revenue}")
        else:
            print("   ❌ No bookings are both approved and paid yet")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_bookings()
