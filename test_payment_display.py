#!/usr/bin/env python
"""
Test the payment page display with detailed service information
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from services.views import ServiceBookingView, PaymentView
from datetime import datetime, timedelta

def create_test_booking():
    """Create a test booking and return the booking ID"""
    User = get_user_model()
    
    # Get or create test user
    try:
        user = User.objects.get(email='test@example.com')
        print(f"Using existing user: {user.email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        print(f"Created new user: {user.email}")
    
    # Create a request factory
    factory = RequestFactory()
    
    # Prepare form data
    tomorrow = datetime.now() + timedelta(days=1)
    form_data = {
        'booking_date': tomorrow.strftime('%Y-%m-%d'),
        'booking_time': '14:30',
        'address': '456 Test Avenue, Test City, Test State',
        'phone_number': '9876543210',
        'notes': 'Test booking for plumbing repair service'
    }
    
    # Create a POST request for plumbing service (ID 4)
    request = factory.post('/services/book/4/', form_data)
    request.user = user
    
    # Create the view instance
    view = ServiceBookingView()
    view.kwargs = {'service_id': 4}
    
    try:
        print("Creating test booking for Plumbing Repair...")
        response = view.post(request, service_id=4)
        
        if hasattr(response, 'url') and 'payment' in response.url:
            booking_id = response.url.split('/')[-2]
            print(f"✅ Booking created successfully: {booking_id}")
            return booking_id
        else:
            print("❌ Booking creation failed")
            return None
            
    except Exception as e:
        print(f"❌ Error during booking creation: {e}")
        return None

def test_payment_page_display(booking_id):
    """Test the payment page display"""
    User = get_user_model()
    user = User.objects.get(email='test@example.com')
    
    # Create a request factory
    factory = RequestFactory()
    
    # Create a GET request for payment page
    request = factory.get(f'/services/payment/{booking_id}/')
    request.user = user
    
    # Create the payment view instance
    view = PaymentView()
    view.kwargs = {'booking_id': booking_id}
    
    try:
        print(f"\nTesting payment page display for booking: {booking_id}")
        context = view.get_context_data(booking_id=booking_id)
        
        if context.get('booking'):
            booking = context['booking']
            print(f"✅ Booking found: {booking.id}")
            print(f"   Notes: {booking.notes}")
            
            # Display service information
            print(f"\n📋 Service Information:")
            print(f"   Service Name: {context.get('service_name', 'Not found')}")
            print(f"   Description: {context.get('service_description', 'Not found')}")
            print(f"   Category: {context.get('service_category', 'Not found')}")
            print(f"   Duration: {context.get('service_duration', 'Not found')} hours")
            print(f"   Provider: {context.get('provider_name', 'Not found')}")
            
            # Display pricing information
            print(f"\n💰 Pricing Information:")
            print(f"   Subtotal: ₹{context.get('subtotal', 0)}")
            print(f"   Tax (18%): ₹{context.get('tax_amount', 0)}")
            print(f"   Total: ₹{context.get('total_amount', 0)}")
            
            return True
        else:
            print("❌ Booking not found in context")
            return False
            
    except Exception as e:
        print(f"❌ Error testing payment page: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == '__main__':
    print("Testing payment page service display...")
    print("=" * 50)
    
    # Create a test booking
    booking_id = create_test_booking()
    
    if booking_id:
        # Test the payment page display
        success = test_payment_page_display(booking_id)
        
        if success:
            print(f"\n✅ Payment page display test successful!")
            print(f"You can view the payment page at: http://127.0.0.1:8000/services/payment/{booking_id}/")
            print(f"Login with: test@example.com / testpass123")
        else:
            print(f"\n❌ Payment page display test failed!")
    else:
        print(f"\n❌ Could not create test booking!")
