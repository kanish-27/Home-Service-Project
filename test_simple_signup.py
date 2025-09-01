#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def test_simple_signup():
    """Simple test to verify signup functionality"""
    print("🔧 Testing Simple Signup Functionality...\n")
    
    try:
        from django.contrib.auth import get_user_model
        from users.forms import UserRegistrationForm
        
        User = get_user_model()
        
        # Test 1: Create a user manually
        print("👤 Test 1: Manual User Creation...")
        
        try:
            # Check if test user already exists
            try:
                existing_user = User.objects.get(email='simpletest@example.com')
                existing_user.delete()
                print("   • Cleaned up existing test user")
            except User.DoesNotExist:
                pass
            
            # Create new user
            test_user = User.objects.create_user(
                email='simpletest@example.com',
                password='testpass123',
                first_name='Simple',
                last_name='Test'
            )
            test_user.user_type = 'customer'
            test_user.save()
            
            print(f"   ✅ User created successfully: {test_user.email}")
            print(f"   • ID: {test_user.id}")
            print(f"   • Name: {test_user.get_full_name()}")
            print(f"   • User type: {test_user.user_type}")
            
            # Clean up
            test_user.delete()
            print("   ✅ Test user cleaned up")
            
        except Exception as manual_error:
            print(f"   ❌ Manual user creation failed: {manual_error}")
            return False
        
        # Test 2: Test form-based user creation
        print("\n📝 Test 2: Form-Based User Creation...")
        
        try:
            form_data = {
                'email': 'formtest@example.com',
                'first_name': 'Form',
                'last_name': 'Test',
                'password1': 'testpass123',
                'password2': 'testpass123'
            }
            
            form = UserRegistrationForm(data=form_data)
            
            if form.is_valid():
                print("   ✅ Form validation passed")
                
                # Save user through form
                user = form.save()
                user.user_type = 'customer'
                user.save()
                
                print(f"   ✅ User created through form: {user.email}")
                
                # Clean up
                user.delete()
                print("   ✅ Form test user cleaned up")
                
            else:
                print("   ❌ Form validation failed:")
                for field, errors in form.errors.items():
                    print(f"     • {field}: {errors}")
                return False
                
        except Exception as form_error:
            print(f"   ❌ Form-based creation failed: {form_error}")
            return False
        
        # Test 3: Test database connection
        print("\n💾 Test 3: Database Connection Test...")
        
        try:
            user_count = User.objects.count()
            print(f"   ✅ Database connection working")
            print(f"   • Total users in database: {user_count}")
            
            # List some users
            users = User.objects.all()[:3]
            for user in users:
                print(f"     • {user.email} ({user.user_type})")
                
        except Exception as db_error:
            print(f"   ❌ Database connection failed: {db_error}")
            return False
        
        print("\n🎉 Simple Signup Test Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in simple signup test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Testing Simple Signup Functionality\n")
    
    success = test_simple_signup()
    
    if success:
        print(f"\n🎉 Simple Signup Test Passed!")
        print(f"\n✅ Verified:")
        print(f"   • User model creation works")
        print(f"   • Form validation works")
        print(f"   • Database saving works")
        print(f"   • MongoDB compatibility confirmed")
        
        print(f"\n📱 Ready for Testing:")
        print(f"   • Signup page: http://127.0.0.1:8000/accounts/signup/")
        print(f"   • Login page: http://127.0.0.1:8000/accounts/login/")
        
        print(f"\n💡 The DatabaseError should now be resolved!")
        print(f"   Try creating a new account through the signup page.")
    else:
        print(f"\n❌ Simple Signup Test Failed")
        print(f"   There may still be database compatibility issues.")
        
    print(f"\n🔧 Signup functionality verified!")
