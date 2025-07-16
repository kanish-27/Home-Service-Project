#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def test_direct_upi_payment():
    """Test UPI payment without confirmation dialog"""
    print("🧪 Testing Direct UPI Payment (No Confirmation)...")
    
    try:
        from django.test import Client
        from users.models import User
        
        # Create test client
        client = Client()
        
        # Get test user
        test_user = User.objects.filter(email='test@example.com').first()
        if not test_user:
            test_user = User.objects.create_user(
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User',
                user_type='customer'
            )
            print("✅ Created test user")
        
        # Force login the user
        client.force_login(test_user)
        print("✅ Logged in test user")
        
        # Create a test booking ID (using a valid ObjectId format)
        booking_id = "683b4e8424ebc4583fe5d6e1"
        
        # Test UPI payment submission
        process_url = f'/services/payment/{booking_id}/process/'
        payment_data = {
            'payment_method': 'upi'
        }
        
        print(f"Submitting UPI payment to: {process_url}")
        response = client.post(process_url, payment_data, follow=True)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Check if redirected to success page
            if hasattr(response, 'redirect_chain') and response.redirect_chain:
                final_url = response.redirect_chain[-1][0]
                print(f"Final URL: {final_url}")
                
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
                if 'Payment Successful' in content:
                    print("✅ Payment success message found on current page!")
                    return True
                    
        print("❌ Payment submission failed or didn't show success")
        return False
        
    except Exception as e:
        print(f"❌ Error testing direct UPI payment: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Testing Direct UPI Payment (No Confirmation Dialog)\n")
    
    success = test_direct_upi_payment()
    
    if success:
        print("\n🎉 Direct UPI payment is working!")
        print("\n✅ The 'I have paid' button now works without confirmation!")
        print("\n📝 User Experience:")
        print("1. User selects UPI payment method")
        print("2. QR code appears")
        print("3. User clicks 'I have paid ₹[amount]' button")
        print("4. Directly redirects to success page (no popup)")
    else:
        print("\n❌ Direct UPI payment test failed.")
        
    print(f"\n🔗 Manual Test URL:")
    print(f"   http://127.0.0.1:8000/services/payment/683b4e8424ebc4583fe5d6e1/")
