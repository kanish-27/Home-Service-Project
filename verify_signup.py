#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def verify_signup():
    """Verify that the signup fix is working"""
    print("👤 Verifying Signup Fix...\n")
    
    try:
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Test user creation
        print("📝 Testing User Creation...")
        
        test_email = 'signuptest@example.com'
        
        # Clean up any existing user
        User.objects.filter(email=test_email).delete()
        
        # Create user
        user = User.objects.create_user(
            email=test_email,
            password='testpass123',
            first_name='Signup',
            last_name='Test',
            username=test_email,
            user_type='customer'
        )
        
        print("   ✅ User created successfully")
        print(f"   • Email: {user.email}")
        print(f"   • Username: {user.username}")
        print(f"   • User Type: {user.user_type}")
        
        # Clean up
        user.delete()
        
        print("\n🎉 Signup Fix Verified!")
        print("\n✅ The signup functionality should now work without DatabaseError")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    verify_signup()
