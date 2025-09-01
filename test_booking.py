#!/usr/bin/env python
"""
Test script to simulate the booking flow
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

def test_booking_flow():
    """Test the complete booking flow"""
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
    
    # Login
    login_success = client.login(email='test@example.com', password='testpass123')
    print(f"Login successful: {login_success}")
    
    if not login_success:
        print("Login failed!")
        return
    
    # Test booking page access
    booking_url = reverse('services:book_service', kwargs={'service_id': 1})
    print(f"Accessing booking page: {booking_url}")
    
    response = client.get(booking_url)
    print(f"Booking page status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Booking page accessible")
    else:
        print(f"❌ Booking page error: {response.status_code}")
        return
    
    # Test booking submission
    tomorrow = datetime.now() + timedelta(days=1)
    booking_data = {
        'booking_date': tomorrow.strftime('%Y-%m-%d'),
        'booking_time': '10:00',
        'address': '123 Test Street, Test City',
        'phone_number': '9876543210',
        'notes': 'Test booking for electrical installation'
    }
    
    print("Submitting booking...")
    response = client.post(booking_url, booking_data)
    print(f"Booking submission status: {response.status_code}")
    print(f"Response redirect: {response.get('Location', 'No redirect')}")
    
    if response.status_code == 302:
        redirect_url = response.get('Location', '')
        if 'payment' in redirect_url:
            print("✅ Successfully redirected to payment page!")
            print(f"Payment URL: {redirect_url}")
            
            # Test payment page access
            payment_response = client.get(redirect_url)
            print(f"Payment page status: {payment_response.status_code}")
            
            if payment_response.status_code == 200:
                print("✅ Payment page accessible!")
            else:
                print(f"❌ Payment page error: {payment_response.status_code}")
        else:
            print(f"❌ Unexpected redirect: {redirect_url}")
    else:
        print(f"❌ Booking submission failed: {response.status_code}")
        if hasattr(response, 'content'):
            print("Response content preview:")
            print(response.content.decode('utf-8')[:500])

if __name__ == '__main__':
    test_booking_flow()
