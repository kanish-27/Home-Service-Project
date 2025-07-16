#!/usr/bin/env python
"""
Test payment page with real MongoDB booking ID
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from django.contrib.auth import get_user_model
import pymongo
from django.conf import settings

def get_real_booking_ids():
    """Get real booking IDs from MongoDB"""
    try:
        User = get_user_model()
        user = User.objects.get(email='test@example.com')
        
        # Connect to MongoDB directly
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Find bookings for this user
        bookings = list(db['services_booking'].find({'customer_id': user.id}))
        
        print(f"Found {len(bookings)} bookings in MongoDB:")
        for i, booking in enumerate(bookings):
            booking_id = str(booking['_id'])
            notes = booking.get('notes', 'No notes')[:50]
            print(f"   {i+1}. ID: {booking_id}")
            print(f"      Notes: {notes}...")
            print(f"      Amount: ₹{booking.get('total_amount', 0)}")
        
        return [str(booking['_id']) for booking in bookings]
        
    except Exception as e:
        print(f"Error getting booking IDs: {e}")
        return []

def test_payment_page_with_real_id(booking_id):
    """Test payment page with real booking ID"""
    print(f"\n🧪 Testing payment page with ID: {booking_id}")
    
    try:
        from services.views import PaymentView
        from django.test import RequestFactory
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.messages.middleware import MessageMiddleware
        
        User = get_user_model()
        user = User.objects.get(email='test@example.com')
        
        # Create proper request
        factory = RequestFactory()
        request = factory.get(f'/services/payment/{booking_id}/')
        request.user = user
        
        # Add middleware
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        msg_middleware = MessageMiddleware(lambda x: None)
        msg_middleware.process_request(request)
        
        # Test PaymentView
        view = PaymentView()
        view.request = request
        
        context = view.get_context_data(booking_id=booking_id)
        
        if context.get('booking'):
            booking = context['booking']
            print(f"   ✅ SUCCESS! Payment page working")
            print(f"   📋 Service Details:")
            print(f"      Service: {context.get('service_name', 'Unknown')}")
            print(f"      Description: {context.get('service_description', 'N/A')}")
            print(f"      Category: {context.get('service_category', 'N/A')}")
            print(f"      Duration: {context.get('service_duration', 'N/A')} hours")
            print(f"      Provider: {context.get('provider_name', 'Unknown')}")
            print(f"   💰 Pricing:")
            print(f"      Subtotal: ₹{context.get('subtotal', 0)}")
            print(f"      Tax (18%): ₹{context.get('tax_amount', 0)}")
            print(f"      Total: ₹{context.get('total_amount', 0)}")
            print(f"   🔗 Payment URL: http://127.0.0.1:8000/services/payment/{booking_id}/")
            return True
        else:
            print(f"   ❌ FAILED! Booking not found")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

if __name__ == '__main__':
    print("Testing Payment Page with Real Booking IDs")
    print("=" * 50)
    
    # Get real booking IDs
    booking_ids = get_real_booking_ids()
    
    if booking_ids:
        # Test with the first booking ID
        success = test_payment_page_with_real_id(booking_ids[0])
        
        if success:
            print(f"\n✅ PAYMENT PAGE IS WORKING!")
            print(f"You can now access the payment page at:")
            print(f"http://127.0.0.1:8000/services/payment/{booking_ids[0]}/")
            print(f"Login with: test@example.com / testpass123")
        else:
            print(f"\n❌ Payment page still has issues")
    else:
        print(f"\n❌ No booking IDs found to test with")
