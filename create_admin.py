#!/usr/bin/env python3
"""
Simple script to create an admin user for testing
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from users.models import User

def create_admin_user():
    print("🔐 Creating Admin User...")
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        email='admin@homeservice.com',
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'user_type': 'admin',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True
        }
    )
    
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Created admin user: {admin_user.email}")
    else:
        # Update existing user to ensure it has admin privileges
        admin_user.user_type = 'admin'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Updated admin user: {admin_user.email}")
    
    print(f"\n🔗 Admin Login Credentials:")
    print(f"📧 Email: admin@homeservice.com")
    print(f"🔑 Password: admin123")
    print(f"\n🔗 Login URL: http://127.0.0.1:8000/accounts/login/")
    print(f"🔗 Admin Services URL: http://127.0.0.1:8000/services/admin-services/")
    print(f"\n📝 Instructions:")
    print(f"1. Go to the login URL")
    print(f"2. Login with the credentials above")
    print(f"3. Navigate to the admin services URL")
    print(f"4. You should see the admin services management interface")

if __name__ == '__main__':
    create_admin_user()
