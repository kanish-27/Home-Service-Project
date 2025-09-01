#!/usr/bin/env python
"""
Create admin user for the system
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from users.models import User

def create_admin_user():
    """Create or update admin user"""
    print("🔐 CREATING ADMIN USER")
    print("=" * 30)
    
    try:
        admin_email = 'admin@homeservice.com'
        admin_password = 'admin123'
        
        # Check if admin user already exists
        try:
            admin_user = User.objects.get(email=admin_email)
            print(f"✅ Admin user found: {admin_user.email}")
            print(f"   User type: {admin_user.user_type}")
            print(f"   Is staff: {admin_user.is_staff}")
            print(f"   Is superuser: {admin_user.is_superuser}")
            print(f"   Is active: {admin_user.is_active}")
            
            # Update password to make sure it's correct
            admin_user.set_password(admin_password)
            admin_user.user_type = 'admin'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.is_active = True
            admin_user.save()
            print("✅ Admin user password and permissions updated")
            
        except User.DoesNotExist:
            print("❌ Admin user not found. Creating new admin user...")
            
            # Create new admin user
            admin_user = User.objects.create_user(
                email=admin_email,
                password=admin_password,
                first_name='Admin',
                last_name='User',
                user_type='admin',
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            print(f"✅ Created new admin user: {admin_user.email}")
        
        # Test password
        from django.contrib.auth import authenticate
        test_user = authenticate(email=admin_email, password=admin_password)
        if test_user:
            print("✅ Password authentication test: SUCCESS")
        else:
            print("❌ Password authentication test: FAILED")
            # Try to fix password
            admin_user.set_password(admin_password)
            admin_user.save()
            print("🔧 Password reset and saved again")
            
            # Test again
            test_user = authenticate(email=admin_email, password=admin_password)
            if test_user:
                print("✅ Password authentication test after reset: SUCCESS")
            else:
                print("❌ Password authentication still failing")
        
        print("\n" + "=" * 30)
        print("🎉 ADMIN USER SETUP COMPLETE!")
        
        print("\n🔐 LOGIN CREDENTIALS:")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        
        print("\n🌐 LOGIN URLS:")
        print("   Main Login: http://127.0.0.1:8000/accounts/login/")
        print("   Admin Dashboard: http://127.0.0.1:8000/admin-dashboard/")
        print("   Django Admin: http://127.0.0.1:8000/admin/")
        
        print("\n📋 STEPS TO LOGIN:")
        print("   1. Go to: http://127.0.0.1:8000/accounts/login/")
        print(f"   2. Enter email: {admin_email}")
        print(f"   3. Enter password: {admin_password}")
        print("   4. Click 'Sign In'")
        print("   5. You'll be redirected to admin dashboard")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_admin_user()
    if success:
        print("\n🚀 ADMIN USER IS READY!")
    else:
        print("\n❌ Please check the errors above.")
