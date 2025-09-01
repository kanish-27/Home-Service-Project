#!/usr/bin/env python
"""
Test the actual booking submission to ServiceBookingView
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from services.views import ServiceBookingView
from datetime import datetime, timedelta

def test_actual_booking_submission():
    """Test actual booking submission to ServiceBookingView"""
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
        'booking_time': '10:00',
        'address': '123 Test Street, Test City',
        'phone_number': '9876543210',
        'notes': 'Test booking for electrical installation'
    }
    
    # Create a POST request
    request = factory.post('/services/book/1/', form_data)
    request.user = user
    
    # Create the view instance
    view = ServiceBookingView()
    view.kwargs = {'service_id': 1}
    
    try:
        print("Submitting booking to ServiceBookingView...")
        response = view.post(request, service_id=1)
        
        print(f"Response status: {response.status_code}")
        
        if hasattr(response, 'url'):
            print(f"Redirect URL: {response.url}")
            if 'payment' in response.url:
                print("✅ Successfully redirected to payment page!")
                return True
            else:
                print(f"❌ Unexpected redirect: {response.url}")
                return False
        else:
            print("❌ No redirect occurred")
            return False
            
    except Exception as e:
        print(f"❌ Error during booking submission: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

def check_server_logs():
    """Check if there are any server logs to read"""
    print("\nChecking for server debug output...")
    # The debug prints should appear in the server console
    print("(Check the server terminal for DEBUG messages)")

if __name__ == '__main__':
    print("Testing actual booking submission...")
    print("=" * 50)
    
    success = test_actual_booking_submission()
    
    if success:
        print(f"\n✅ Booking submission successful!")
        print("The booking should now redirect to the payment page.")
    else:
        print(f"\n❌ Booking submission failed!")
        
    check_server_logs()
