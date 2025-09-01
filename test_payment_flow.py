#!/usr/bin/env python3

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def test_payment_flow():
    """Test the UPI payment flow"""
    print("🧪 Testing UPI Payment Flow...")
    
    try:
        # Import models after Django setup
        from services.models import Service, ServiceCategory, Booking
        from users.models import User
        
        # Create test client
        client = Client()
        
        # Create or get test user
        User = get_user_model()
        test_user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'user_type': 'customer'
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            print("✅ Created test user")
        else:
            print("✅ Using existing test user")
        
        # Login the test user
        login_success = client.login(email='test@example.com', password='testpass123')
        if not login_success:
            print("❌ Failed to login test user")
            return False
        print("✅ Logged in test user")
        
        # Check if there are any bookings
        bookings = Booking.objects.filter(customer=test_user)
        if not bookings.exists():
            print("❌ No bookings found for test user")
            print("💡 Please create a booking first through the website")
            return False
        
        # Get the first booking
        booking = bookings.first()
        print(f"✅ Found booking: {booking.id}")
        
        # Test payment page access
        payment_url = reverse('services:payment', kwargs={'booking_id': str(booking.id)})
        response = client.get(payment_url)
        
        if response.status_code == 200:
            print("✅ Payment page loads successfully")
        else:
            print(f"❌ Payment page failed to load: {response.status_code}")
            return False
        
        # Test UPI payment submission
        process_payment_url = reverse('services:process_payment', kwargs={'booking_id': str(booking.id)})
        payment_data = {
            'payment_method': 'upi'
        }
        
        response = client.post(process_payment_url, payment_data)
        
        if response.status_code == 302:  # Redirect to success page
            print("✅ UPI payment processed successfully")
            print(f"✅ Redirected to: {response.url}")
            
            # Check if redirected to success page
            if 'success' in response.url:
                print("✅ Payment flow completed successfully!")
                return True
            else:
                print("⚠️ Payment processed but not redirected to success page")
                return False
        else:
            print(f"❌ Payment processing failed: {response.status_code}")
            if hasattr(response, 'content'):
                print(f"Response content: {response.content.decode()[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error during payment flow test: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_payment_urls():
    """Check if payment URLs are properly configured"""
    print("\n🔗 Checking Payment URLs...")
    
    try:
        from django.urls import reverse
        
        # Test URL patterns
        test_booking_id = "507f1f77bcf86cd799439011"  # Sample ObjectId
        
        urls_to_test = [
            ('services:payment', {'booking_id': test_booking_id}),
            ('services:process_payment', {'booking_id': test_booking_id}),
            ('services:payment_success', {'booking_id': test_booking_id}),
            ('services:payment_failed', {'booking_id': test_booking_id}),
        ]
        
        for url_name, kwargs in urls_to_test:
            try:
                url = reverse(url_name, kwargs=kwargs)
                print(f"✅ {url_name}: {url}")
            except Exception as e:
                print(f"❌ {url_name}: {e}")
                
    except Exception as e:
        print(f"❌ Error checking URLs: {e}")

if __name__ == '__main__':
    print("🚀 Starting Payment Flow Test\n")
    
    # Check URLs first
    check_payment_urls()
    
    # Test payment flow
    success = test_payment_flow()
    
    if success:
        print("\n🎉 All tests passed! UPI payment flow is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        
    print("\n📝 To test manually:")
    print("1. Go to http://127.0.0.1:8000")
    print("2. Login with test@example.com / testpass123")
    print("3. Book a service")
    print("4. Go to payment page")
    print("5. Select UPI payment method")
    print("6. Click 'I have paid' button")
    print("7. Should redirect to success page")
