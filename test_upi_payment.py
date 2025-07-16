#!/usr/bin/env python3

import os
import sys
import django
import requests
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def test_upi_payment_submission():
    """Test UPI payment form submission"""
    print("🧪 Testing UPI Payment Form Submission...")
    
    try:
        # Create test client
        client = Client()
        
        # Login test user
        login_success = client.login(email='test@example.com', password='testpass123')
        if not login_success:
            print("❌ Failed to login test user")
            return False
        
        print("✅ Logged in test user")
        
        # Use the booking ID from the previous script
        booking_id = "683b474d89284a9244928a77"
        
        # First, get the payment page to get CSRF token
        payment_url = f'/services/payment/{booking_id}/'
        response = client.get(payment_url)
        
        print(f"Payment page status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to load payment page: {response.status_code}")
            return False
        
        print("✅ Payment page loaded successfully")
        
        # Extract CSRF token from the response
        content = response.content.decode()
        csrf_start = content.find('name="csrfmiddlewaretoken" value="') + len('name="csrfmiddlewaretoken" value="')
        csrf_end = content.find('"', csrf_start)
        csrf_token = content[csrf_start:csrf_end]
        
        print(f"✅ CSRF token extracted: {csrf_token[:10]}...")
        
        # Submit UPI payment
        process_url = f'/services/payment/{booking_id}/process/'
        payment_data = {
            'payment_method': 'upi',
            'csrfmiddlewaretoken': csrf_token
        }
        
        print(f"Submitting UPI payment to: {process_url}")
        response = client.post(process_url, payment_data, follow=True)
        
        print(f"Response status: {response.status_code}")
        
        # Check if redirected to success page
        if hasattr(response, 'redirect_chain') and response.redirect_chain:
            print(f"Redirect chain: {response.redirect_chain}")
            
            # Check if final URL contains 'success'
            final_url = response.redirect_chain[-1][0] if response.redirect_chain else ''
            if 'success' in final_url:
                print("✅ Successfully redirected to payment success page!")
                
                # Check if success message is in the content
                content = response.content.decode()
                if 'Payment Successful' in content:
                    print("✅ Payment success message found!")
                    return True
                else:
                    print("⚠️ Redirected to success page but success message not found")
                    
        else:
            print("❌ No redirect occurred")
            content = response.content.decode()
            print(f"Response content preview: {content[:500]}...")
        
        return False
        
    except Exception as e:
        print(f"❌ Error testing UPI payment: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_success_page():
    """Test direct access to success page"""
    print("\n🧪 Testing Direct Success Page Access...")
    
    try:
        client = Client()
        
        # Login test user
        login_success = client.login(email='test@example.com', password='testpass123')
        if not login_success:
            print("❌ Failed to login test user")
            return False
        
        booking_id = "683b474d89284a9244928a77"
        success_url = f'/services/payment/success/{booking_id}/'
        
        response = client.get(success_url)
        print(f"Success page status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode()
            if 'Payment Successful' in content:
                print("✅ Success page loads correctly with success message!")
                return True
            else:
                print("⚠️ Success page loads but no success message found")
        else:
            print(f"❌ Failed to load success page: {response.status_code}")
        
        return False
        
    except Exception as e:
        print(f"❌ Error testing success page: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Testing UPI Payment Flow\n")
    
    # Test direct success page access first
    success1 = test_direct_success_page()
    
    # Test UPI payment submission
    success2 = test_upi_payment_submission()
    
    if success1 and success2:
        print("\n🎉 All UPI payment tests passed!")
        print("\n✅ The 'I have paid' button should work correctly!")
        print("\n📝 If the button is still not working in the browser:")
        print("1. Check browser console (F12) for JavaScript errors")
        print("2. Make sure you're logged in as test@example.com")
        print("3. Try refreshing the payment page")
        print("4. Check if the form is submitting by watching the Network tab")
    else:
        print("\n❌ Some tests failed. Check the issues above.")
        
    print(f"\n🔗 Test URLs:")
    print(f"   Login: http://127.0.0.1:8000/login/")
    print(f"   Payment: http://127.0.0.1:8000/services/payment/683b474d89284a9244928a77/")
    print(f"   Success: http://127.0.0.1:8000/services/payment/success/683b474d89284a9244928a77/")
