#!/usr/bin/env python
"""
Script to mark confirmed bookings as paid for testing revenue calculation
"""
import pymongo
from datetime import datetime

def mark_confirmed_bookings_paid():
    """Mark all confirmed bookings as paid for testing"""
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['homeservice_db']
        bookings_collection = db['services_booking']
        
        print("💰 MARKING CONFIRMED BOOKINGS AS PAID")
        print("=" * 50)
        
        # Find confirmed bookings that are not paid
        confirmed_unpaid = list(bookings_collection.find({
            'status': {'$in': ['confirmed', 'completed']},
            '$or': [
                {'is_paid': {'$ne': True}},
                {'is_paid': {'$exists': False}}
            ]
        }))
        
        print(f"📊 Found {len(confirmed_unpaid)} confirmed but unpaid bookings")
        
        if not confirmed_unpaid:
            print("✅ All confirmed bookings are already marked as paid!")
            
            # Show current revenue calculation
            all_revenue_bookings = list(bookings_collection.find({
                'status': {'$in': ['confirmed', 'completed']},
                'is_paid': True
            }))
            
            total_revenue = sum(float(booking.get('total_amount', 0)) for booking in all_revenue_bookings)
            print(f"💵 Current Revenue: ₹{total_revenue}")
            return
        
        # Mark them as paid
        updated_count = 0
        total_revenue = 0
        
        for booking in confirmed_unpaid:
            booking_id = booking['_id']
            amount = float(booking.get('total_amount', 0))
            
            # Update booking to mark as paid
            result = bookings_collection.update_one(
                {'_id': booking_id},
                {
                    '$set': {
                        'is_paid': True,
                        'payment_status': 'paid',
                        'payment_method': 'test_payment',
                        'paid_at': datetime.now(),
                        'updated_at': datetime.now()
                    }
                }
            )
            
            if result.modified_count > 0:
                updated_count += 1
                total_revenue += amount
                print(f"✅ Marked booking {str(booking_id)[:8]}... as paid (₹{amount})")
        
        print(f"\n🎉 SUCCESS!")
        print(f"   📊 Updated {updated_count} bookings")
        print(f"   💰 Total Revenue Generated: ₹{total_revenue}")
        
        print(f"\n🔄 Now refresh your admin dashboard to see the revenue!")
        print(f"   Dashboard URL: http://127.0.0.1:8000/services/admin-dashboard/")
        
        # Verify the changes
        print(f"\n🔍 VERIFICATION:")
        revenue_bookings = list(bookings_collection.find({
            'status': {'$in': ['confirmed', 'completed']},
            'is_paid': True
        }))
        
        final_revenue = sum(float(booking.get('total_amount', 0)) for booking in revenue_bookings)
        print(f"   ✅ Revenue-generating bookings: {len(revenue_bookings)}")
        print(f"   💵 Total Revenue: ₹{final_revenue}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    mark_confirmed_bookings_paid()
