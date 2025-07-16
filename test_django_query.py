#!/usr/bin/env python
"""
Test Django ORM queries for revenue calculation
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from services.models import Booking
from django.db.models import Sum

def test_django_queries():
    """Test Django ORM queries"""
    print("🔍 TESTING DJANGO ORM QUERIES")
    print("=" * 50)
    
    try:
        # Test 1: Count all bookings
        print("1. Testing total bookings count...")
        total_bookings = Booking.objects.count()
        print(f"   ✅ Total bookings: {total_bookings}")
        
        # Test 2: Get confirmed bookings (without is_paid filter)
        print("\n2. Testing confirmed bookings...")
        confirmed_bookings = Booking.objects.filter(status__in=['confirmed', 'completed'])
        confirmed_count = confirmed_bookings.count()
        print(f"   ✅ Confirmed bookings: {confirmed_count}")
        
        # Test 3: Try to get individual booking data
        print("\n3. Testing individual booking data...")
        for booking in confirmed_bookings[:3]:  # First 3 confirmed bookings
            print(f"   ID: {booking.id}, Status: {booking.status}, Amount: ₹{booking.total_amount}")
            # Try to access is_paid field carefully
            try:
                is_paid = getattr(booking, 'is_paid', None)
                print(f"   Is Paid: {is_paid}")
            except Exception as e:
                print(f"   ❌ Error accessing is_paid: {e}")
        
        # Test 4: Try revenue calculation with raw query
        print("\n4. Testing revenue calculation...")
        try:
            # Try the problematic query
            revenue_bookings = Booking.objects.filter(
                status__in=['confirmed', 'completed'],
                is_paid=True
            )
            revenue_count = revenue_bookings.count()
            print(f"   ✅ Revenue bookings count: {revenue_count}")
            
            # Try sum calculation
            total_revenue = revenue_bookings.aggregate(total=Sum('total_amount'))['total'] or 0
            print(f"   ✅ Total revenue: ₹{total_revenue}")
            
        except Exception as e:
            print(f"   ❌ Error with revenue query: {e}")
            
            # Try alternative approach - get confirmed bookings and check manually
            print("\n   🔄 Trying alternative approach...")
            confirmed_bookings = Booking.objects.filter(status__in=['confirmed', 'completed'])
            manual_revenue = 0
            revenue_count = 0
            
            for booking in confirmed_bookings:
                try:
                    if hasattr(booking, 'is_paid') and booking.is_paid:
                        manual_revenue += float(booking.total_amount)
                        revenue_count += 1
                except Exception as booking_error:
                    print(f"   ❌ Error processing booking {booking.id}: {booking_error}")
            
            print(f"   ✅ Manual calculation - Revenue bookings: {revenue_count}")
            print(f"   ✅ Manual calculation - Total revenue: ₹{manual_revenue}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_django_queries()
