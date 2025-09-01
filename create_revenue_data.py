#!/usr/bin/env python
"""
Create sample revenue data for testing admin dashboard
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from users.models import User
from services.models import Service, Booking
from django.utils import timezone

def create_revenue_data():
    """Create sample paid bookings to test revenue display"""
    print("💰 CREATING REVENUE DATA FOR ADMIN DASHBOARD")
    print("=" * 50)
    
    try:
        # Get existing users and services
        try:
            customer = User.objects.get(email='customer@example.com')
            print(f"✅ Found customer: {customer.email}")
        except User.DoesNotExist:
            print("❌ Customer not found. Please run create_test_users.py first")
            return False
        
        # Get available services
        services = Service.objects.filter(is_active=True, is_available=True)
        if not services.exists():
            print("❌ No services found. Please add services first")
            return False
        
        print(f"✅ Found {services.count()} services")
        
        # Create paid bookings for revenue
        revenue_bookings = [
            {
                'service': services[0] if services.count() > 0 else None,
                'amount': 2500,
                'days_ago': 5
            },
            {
                'service': services[1] if services.count() > 1 else services[0],
                'amount': 1200,
                'days_ago': 3
            },
            {
                'service': services[2] if services.count() > 2 else services[0],
                'amount': 3500,
                'days_ago': 1
            }
        ]
        
        total_created_revenue = 0
        
        for i, booking_data in enumerate(revenue_bookings):
            if not booking_data['service']:
                continue
                
            booking_date = timezone.now() - timedelta(days=booking_data['days_ago'])
            
            # Check if booking already exists
            existing_booking = Booking.objects.filter(
                service=booking_data['service'],
                customer=customer,
                is_paid=True
            ).first()
            
            if existing_booking:
                print(f"💰 Paid booking exists: {existing_booking.service.name} - ₹{existing_booking.total_amount or existing_booking.service.price}")
                total_created_revenue += existing_booking.total_amount or existing_booking.service.price
                continue
            
            # Create new paid booking
            booking = Booking.objects.create(
                service=booking_data['service'],
                customer=customer,
                provider=booking_data['service'].provider,
                booking_date=booking_date,
                address=f'Revenue Test Address {i+1}, Mumbai, Maharashtra',
                phone_number='+91 9876543210',
                status='completed',
                payment_status='paid',
                is_paid=True,
                total_amount=booking_data['amount'],
                special_instructions=f'Paid booking for revenue testing - ₹{booking_data["amount"]}'
            )
            
            print(f"✅ Created paid booking: {booking.service.name} - ₹{booking.total_amount}")
            total_created_revenue += booking.total_amount
        
        # Calculate total revenue
        all_paid_bookings = Booking.objects.filter(is_paid=True)
        total_revenue = sum(
            booking.total_amount or booking.service.price 
            for booking in all_paid_bookings
        )
        
        print(f"\n💰 REVENUE SUMMARY:")
        print(f"   Total Paid Bookings: {all_paid_bookings.count()}")
        print(f"   Total Revenue: ₹{total_revenue}")
        print(f"   New Revenue Created: ₹{total_created_revenue}")
        
        print(f"\n🎯 ADMIN DASHBOARD TEST:")
        print("   1. Login as admin: admin@homeservice.com / admin123")
        print("   2. Go to: http://127.0.0.1:8000/admin-dashboard/")
        print(f"   3. Revenue should show: ₹{total_revenue}")
        print("   4. Cards should have beautiful gradient colors")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_revenue_data()
    if success:
        print("\n🎉 Revenue data created! Test the admin dashboard now.")
    else:
        print("\n❌ Please check the errors above.")
