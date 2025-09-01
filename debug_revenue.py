#!/usr/bin/env python
"""
Debug script to check booking data and revenue calculation
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from services.models import Booking, Service
from django.db.models import Sum, Count

def debug_revenue():
    """Debug revenue calculation"""
    print("🔍 DEBUGGING REVENUE CALCULATION")
    print("=" * 50)
    
    # Get all bookings
    all_bookings = Booking.objects.all()
    print(f"📊 Total Bookings: {all_bookings.count()}")
    
    # Check booking statuses
    status_counts = Booking.objects.values('status').annotate(count=Count('id'))
    print(f"\n📈 Booking Status Breakdown:")
    for status in status_counts:
        print(f"   {status['status']}: {status['count']}")
    
    # Check payment statuses
    payment_counts = Booking.objects.values('is_paid').annotate(count=Count('id'))
    print(f"\n💳 Payment Status Breakdown:")
    for payment in payment_counts:
        paid_status = "Paid" if payment['is_paid'] else "Unpaid"
        print(f"   {paid_status}: {payment['count']}")
    
    # Check confirmed bookings
    confirmed_bookings = Booking.objects.filter(status__in=['confirmed', 'completed'])
    print(f"\n✅ Confirmed/Completed Bookings: {confirmed_bookings.count()}")
    
    # Check paid bookings
    paid_bookings = Booking.objects.filter(is_paid=True)
    print(f"💰 Paid Bookings: {paid_bookings.count()}")
    
    # Check confirmed AND paid bookings (this should generate revenue)
    revenue_bookings = Booking.objects.filter(
        status__in=['confirmed', 'completed'],
        is_paid=True
    )
    print(f"🎯 Confirmed AND Paid Bookings: {revenue_bookings.count()}")
    
    # Calculate revenue
    total_revenue = revenue_bookings.aggregate(total=Sum('total_amount'))['total'] or 0
    print(f"💵 Total Revenue: ₹{total_revenue}")
    
    # Show individual revenue bookings
    if revenue_bookings.exists():
        print(f"\n📋 Revenue-generating bookings:")
        for booking in revenue_bookings:
            print(f"   ID: {booking.id}, Status: {booking.status}, Paid: {booking.is_paid}, Amount: ₹{booking.total_amount}")
    else:
        print(f"\n❌ No bookings found that are both confirmed AND paid!")
        
        # Show what we have
        print(f"\n🔍 Let's see what bookings exist:")
        for booking in all_bookings[:10]:  # Show first 10
            print(f"   ID: {booking.id}, Status: {booking.status}, Paid: {booking.is_paid}, Amount: ₹{booking.total_amount}")
    
    print(f"\n" + "=" * 50)
    print(f"🎯 SOLUTION:")
    print(f"   For revenue to show, bookings need to be:")
    print(f"   1. ✅ Admin approved (status = 'confirmed' or 'completed')")
    print(f"   2. ✅ Payment successful (is_paid = True)")
    print(f"   Both conditions must be met!")

if __name__ == '__main__':
    debug_revenue()
