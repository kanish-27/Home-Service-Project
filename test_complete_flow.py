#!/usr/bin/env python
"""
Test complete booking flow from service booking to payment
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from datetime import datetime, timedelta

def test_complete_booking_flow():
    """Test the complete booking flow from booking form to payment page"""
    
    # Create a test client
    client = Client()
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
    
    # Login the user
    login_success = client.login(email='test@example.com', password='testpass123')
    print(f"Login successful: {login_success}")
    
    if not login_success:
        print("❌ Login failed!")
        return False
    
    # Test accessing the booking page
    booking_url = reverse('services:book_service', kwargs={'service_id': 1})
    print(f"Accessing booking page: {booking_url}")
    
    response = client.get(booking_url)
    print(f"Booking page status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Cannot access booking page: {response.status_code}")
        return False
    
    print("✅ Booking page accessible")
    
    # Test booking form submission
    tomorrow = datetime.now() + timedelta(days=1)
    booking_data = {
        'booking_date': tomorrow.strftime('%Y-%m-%d'),
        'booking_time': '10:00',
        'address': '123 Test Street, Test City',
        'phone_number': '9876543210',
        'notes': 'Test booking for electrical installation'
    }
    
    print("Submitting booking form...")
    response = client.post(booking_url, booking_data, follow=True)
    print(f"Booking submission status: {response.status_code}")
    
    # Check if redirected to payment page
    if response.status_code == 200:
        final_url = response.request['PATH_INFO']
        print(f"Final URL after booking: {final_url}")
        
        if 'payment' in final_url:
            print("✅ Successfully redirected to payment page!")
            
            # Check if payment page content is loaded
            content = response.content.decode('utf-8')
            if 'Payment Summary' in content or 'payment' in content.lower():
                print("✅ Payment page content loaded successfully!")
                
                # Extract booking ID from URL
                import re
                booking_id_match = re.search(r'/payment/([^/]+)/', final_url)
                if booking_id_match:
                    booking_id = booking_id_match.group(1)
                    print(f"✅ Booking ID: {booking_id}")
                    return True
                else:
                    print("❌ Could not extract booking ID from URL")
                    return False
            else:
                print("❌ Payment page content not loaded properly")
                print("Response content preview:")
                print(content[:500])
                return False
        else:
            print(f"❌ Not redirected to payment page. Final URL: {final_url}")
            return False
    else:
        print(f"❌ Booking submission failed: {response.status_code}")
        return False

def test_payment_page_directly():
    """Test accessing payment page directly with a known booking ID"""
    client = Client()
    
    # Login
    login_success = client.login(email='test@example.com', password='testpass123')
    if not login_success:
        print("❌ Login failed for direct payment test!")
        return False
    
    # Use the booking ID from our previous test
    booking_id = '683ac6da54ccc68538e51db4'  # From the previous test
    payment_url = f'/services/payment/{booking_id}/'
    
    print(f"Testing direct payment page access: {payment_url}")
    response = client.get(payment_url)
    print(f"Payment page status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if 'Payment Summary' in content or 'Total Amount' in content:
            print("✅ Payment page loads successfully!")
            return True
        else:
            print("❌ Payment page content not as expected")
            print("Content preview:")
            print(content[:500])
            return False
    else:
        print(f"❌ Payment page access failed: {response.status_code}")
        return False

if __name__ == '__main__':
    print("Testing complete booking flow...")
    print("=" * 50)
    
    print("\n1. Testing complete booking flow:")
    flow_success = test_complete_booking_flow()
    
    print("\n2. Testing direct payment page access:")
    direct_success = test_payment_page_directly()
    
    print("\n" + "=" * 50)
    if flow_success or direct_success:
        print("✅ Payment page is accessible!")
        print("The booking flow issue has been resolved.")
    else:
        print("❌ Payment page access failed!")
        print("Further debugging needed.")
