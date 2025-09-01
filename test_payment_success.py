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

def test_payment_success_directly():
    """Test payment success page directly"""
    print("🧪 Testing Payment Success Page...")
    
    try:
        # Import models after Django setup
        from services.models import Booking
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
        
        # Login the test user
        login_success = client.login(email='test@example.com', password='testpass123')
        if not login_success:
            print("❌ Failed to login test user")
            return False
        
        # Test with a dummy booking ID
        test_booking_id = "507f1f77bcf86cd799439011"  # Sample ObjectId format
        
        # Test payment success page
        success_url = reverse('services:payment_success', kwargs={'booking_id': test_booking_id})
        response = client.get(success_url)
        
        print(f"Payment success URL: {success_url}")
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Payment success page loads successfully")
            
            # Check if the page contains success message
            content = response.content.decode()
            if 'Payment Successful' in content:
                print("✅ Success message found on page")
            else:
                print("⚠️ Success message not found on page")
                
            return True
        else:
            print(f"❌ Payment success page failed to load: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing payment success: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_upi_payment_simulation():
    """Simulate UPI payment process"""
    print("\n🧪 Testing UPI Payment Simulation...")
    
    try:
        from services.models import Booking
        from users.models import User
        
        # Create test client
        client = Client()
        
        # Login test user
        login_success = client.login(email='test@example.com', password='testpass123')
        if not login_success:
            print("❌ Failed to login test user")
            return False
        
        # Use a dummy booking ID for testing
        test_booking_id = "507f1f77bcf86cd799439011"
        
        # Test UPI payment submission
        process_payment_url = reverse('services:process_payment', kwargs={'booking_id': test_booking_id})
        payment_data = {
            'payment_method': 'upi'
        }
        
        print(f"Submitting UPI payment to: {process_payment_url}")
        response = client.post(process_payment_url, payment_data, follow=True)
        
        print(f"Response status: {response.status_code}")
        print(f"Final URL: {response.request['PATH_INFO'] if hasattr(response, 'request') else 'Unknown'}")
        
        # Check redirect chain
        if hasattr(response, 'redirect_chain'):
            print(f"Redirect chain: {response.redirect_chain}")
        
        if response.status_code == 200:
            content = response.content.decode()
            if 'Payment Successful' in content or 'success' in content.lower():
                print("✅ UPI payment simulation successful!")
                return True
            else:
                print("⚠️ Payment processed but success message not found")
                print(f"Page title: {content[content.find('<title>'):content.find('</title>')+8] if '<title>' in content else 'No title found'}")
        else:
            print(f"❌ UPI payment simulation failed: {response.status_code}")
            
        return False
        
    except Exception as e:
        print(f"❌ Error in UPI payment simulation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Testing Payment Success Flow\n")
    
    # Test payment success page directly
    success1 = test_payment_success_directly()
    
    # Test UPI payment simulation
    success2 = test_upi_payment_simulation()
    
    if success1 and success2:
        print("\n🎉 All payment tests passed!")
    else:
        print("\n❌ Some payment tests failed.")
        
    print("\n📝 Manual Testing Steps:")
    print("1. Open browser and go to http://127.0.0.1:8000")
    print("2. Login with any user account")
    print("3. Book a service to create a booking")
    print("4. Go to payment page for that booking")
    print("5. Select UPI payment method")
    print("6. Click 'I have paid' button")
    print("7. Check browser console (F12) for debug messages")
    print("8. Should redirect to payment success page")
