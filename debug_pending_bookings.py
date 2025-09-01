#!/usr/bin/env python
"""
Debug script to check pending bookings discrepancy
"""
import pymongo
from datetime import datetime

def debug_pending_bookings():
    """Check pending bookings in MongoDB vs Django"""
    try:
        # Connect to MongoDB directly
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['homeservice_db']
        bookings_collection = db['services_booking']
        
        print("🔍 DEBUGGING PENDING BOOKINGS DISCREPANCY")
        print("=" * 60)
        
        # Get all bookings from MongoDB
        all_bookings = list(bookings_collection.find())
        print(f"📊 Total bookings in MongoDB: {len(all_bookings)}")
        
        # Check status breakdown
        status_counts = {}
        for booking in all_bookings:
            status = booking.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n📈 Status breakdown:")
        for status, count in status_counts.items():
            print(f"   {status}: {count}")
        
        # Find specifically pending bookings
        pending_bookings = list(bookings_collection.find({'status': 'pending'}))
        print(f"\n⏳ Pending bookings found: {len(pending_bookings)}")
        
        if pending_bookings:
            print(f"\n📋 Pending booking details:")
            for i, booking in enumerate(pending_bookings, 1):
                booking_id = str(booking.get('_id', 'N/A'))
                customer_id = booking.get('customer_id', 'N/A')
                amount = booking.get('total_amount', 0)
                created_at = booking.get('created_at', 'N/A')
                
                print(f"   {i}. ID: {booking_id[:8]}...")
                print(f"      Amount: ₹{amount}")
                print(f"      Created: {created_at}")
                print(f"      Customer ID: {customer_id}")
                print("-" * 40)
        else:
            print("✅ No pending bookings found in MongoDB!")
        
        # Check if there are any bookings with null/undefined status
        null_status_bookings = list(bookings_collection.find({
            '$or': [
                {'status': {'$exists': False}},
                {'status': None},
                {'status': ''}
            ]
        }))
        
        if null_status_bookings:
            print(f"\n⚠️  Found {len(null_status_bookings)} bookings with null/undefined status:")
            for booking in null_status_bookings:
                booking_id = str(booking.get('_id', 'N/A'))
                print(f"   ID: {booking_id[:8]}... - Status: {booking.get('status', 'UNDEFINED')}")
        
        # Test Django ORM query
        print(f"\n🔧 Testing Django ORM query...")
        try:
            import os
            import sys
            import django
            
            # Setup Django
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
            django.setup()
            
            from services.models import Booking
            
            django_pending_count = Booking.objects.filter(status='pending').count()
            print(f"   Django ORM pending count: {django_pending_count}")
            
            # Get the actual Django bookings
            django_pending = Booking.objects.filter(status='pending')
            print(f"   Django pending bookings:")
            for booking in django_pending:
                print(f"      ID: {booking.id}, Status: {booking.status}, Amount: ₹{booking.total_amount}")
                
        except Exception as django_error:
            print(f"   ❌ Django ORM error: {django_error}")
        
        print(f"\n🎯 SOLUTION:")
        if len(pending_bookings) == 0:
            print("   ✅ MongoDB shows no pending bookings")
            print("   🔄 Dashboard cache might be outdated - try refreshing")
            print("   🔧 Or there might be a Django ORM query issue")
        else:
            print(f"   📊 MongoDB shows {len(pending_bookings)} pending booking(s)")
            print("   ✅ Dashboard count is correct")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_pending_bookings()
