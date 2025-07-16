#!/usr/bin/env python
"""
Create test users for the unified system
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from users.models import User
from services.models import ServiceCategory, Service, Booking, ProviderProfile
from django.utils import timezone

def create_test_users():
    """Create test users for different roles"""
    print("🔧 CREATING TEST USERS FOR UNIFIED SYSTEM")
    print("=" * 60)
    
    try:
        # 1. Create Admin User
        print("1. Creating Admin User...")
        admin_email = 'admin@homeservice.com'
        try:
            admin_user = User.objects.get(email=admin_email)
            print(f"   ✅ Admin exists: {admin_user.email}")
        except User.DoesNotExist:
            admin_user = User.objects.create_user(
                email=admin_email,
                password='admin123',
                first_name='Admin',
                last_name='User',
                is_staff=True,
                is_superuser=True,
                user_type='admin'
            )
            print(f"   ✅ Created admin: {admin_user.email}")
        
        # 2. Create Regular Customer
        print("\n2. Creating Customer User...")
        customer_email = 'customer@example.com'
        try:
            customer_user = User.objects.get(email=customer_email)
            print(f"   ✅ Customer exists: {customer_user.email}")
        except User.DoesNotExist:
            customer_user = User.objects.create_user(
                email=customer_email,
                password='customer123',
                first_name='John',
                last_name='Doe',
                user_type='customer',
                is_active=True
            )
            print(f"   ✅ Created customer: {customer_user.email}")
        
        # 3. Create Provider User
        print("\n3. Creating Provider User...")
        provider_email = 'provider@example.com'
        try:
            provider_user = User.objects.get(email=provider_email)
            print(f"   ✅ Provider exists: {provider_user.email}")
        except User.DoesNotExist:
            provider_user = User.objects.create_user(
                email=provider_email,
                password='provider123',
                first_name='Rajesh',
                last_name='Kumar',
                user_type='provider',
                is_active=True
            )
            print(f"   ✅ Created provider: {provider_user.email}")
        
        # Create provider profile
        try:
            provider_profile = ProviderProfile.objects.get(user=provider_user)
            print(f"   ✅ Provider profile exists: {provider_profile.company_name}")
        except ProviderProfile.DoesNotExist:
            provider_profile = ProviderProfile.objects.create(
                user=provider_user,
                company_name='Kumar Home Services',
                business_description='Professional home services in Mumbai',
                phone_number='+91 9876543210',
                address='Mumbai, Maharashtra, India',
                is_verified=True,
                is_available=True
            )
            print(f"   ✅ Created provider profile: {provider_profile.company_name}")
        
        # 4. Create Sample Categories
        print("\n4. Creating Service Categories...")
        categories_data = [
            {'name': 'Electrical', 'slug': 'electrical', 'description': 'Professional electrical services'},
            {'name': 'Plumbing', 'slug': 'plumbing', 'description': 'Expert plumbing services'},
            {'name': 'Cleaning', 'slug': 'cleaning', 'description': 'Professional cleaning services'},
        ]
        
        created_categories = []
        for cat_data in categories_data:
            try:
                category = ServiceCategory.objects.get(slug=cat_data['slug'])
                print(f"   📂 Category exists: {category.name}")
            except ServiceCategory.DoesNotExist:
                category = ServiceCategory.objects.create(**cat_data)
                print(f"   ✅ Created category: {category.name}")
            created_categories.append(category)
        
        # 5. Create Sample Services
        print("\n5. Creating Sample Services...")
        services_data = [
            {
                'name': 'Electrical Installation',
                'description': 'Professional electrical installation and repair services',
                'price': 2500,
                'duration': 3,
                'category': created_categories[0],  # Electrical
                'provider': provider_user
            },
            {
                'name': 'Pipe Repair',
                'description': 'Expert pipe repair and replacement services',
                'price': 1200,
                'duration': 2,
                'category': created_categories[1],  # Plumbing
                'provider': provider_user
            },
            {
                'name': 'Deep Cleaning',
                'description': 'Comprehensive home deep cleaning service',
                'price': 3500,
                'duration': 4,
                'category': created_categories[2],  # Cleaning
                'provider': provider_user
            }
        ]
        
        created_services = []
        for serv_data in services_data:
            try:
                service = Service.objects.get(name=serv_data['name'], provider=serv_data['provider'])
                print(f"   🛠️  Service exists: {service.name}")
            except Service.DoesNotExist:
                service = Service.objects.create(
                    name=serv_data['name'],
                    description=serv_data['description'],
                    price=serv_data['price'],
                    duration=serv_data['duration'],
                    category=serv_data['category'],
                    provider=serv_data['provider'],
                    is_active=True,
                    is_available=True
                )
                print(f"   ✅ Created service: {service.name} - ₹{service.price}")
            created_services.append(service)
        
        # 6. Create Sample Booking
        print("\n6. Creating Sample Booking...")
        if created_services:
            service = created_services[0]
            try:
                booking = Booking.objects.filter(service=service, customer=customer_user).first()
                if booking:
                    print(f"   📅 Booking exists: {booking.service.name}")
                else:
                    raise Booking.DoesNotExist
            except Booking.DoesNotExist:
                booking_date = timezone.now() + timedelta(days=1)
                booking = Booking.objects.create(
                    service=service,
                    customer=customer_user,
                    provider=service.provider,
                    booking_date=booking_date,
                    address='123 Sample Street, Mumbai, Maharashtra',
                    phone_number='+91 9876543210',
                    status='confirmed',
                    payment_status='paid',
                    is_paid=True,
                    total_amount=service.price,
                    special_instructions='Sample booking for testing the unified system'
                )
                print(f"   ✅ Created booking: {booking.service.name}")
        
        print("\n" + "=" * 60)
        print("🎉 UNIFIED SYSTEM SETUP COMPLETED!")
        
        print("\n🔐 LOGIN CREDENTIALS:")
        print("=" * 30)
        print("👑 ADMIN LOGIN:")
        print(f"   Email: {admin_user.email}")
        print("   Password: admin123")
        print("   Features: Upload services, view all bookings")
        
        print("\n👤 CUSTOMER LOGIN:")
        print(f"   Email: {customer_user.email}")
        print("   Password: customer123")
        print("   Features: Browse services, book services")
        
        print("\n🏢 PROVIDER LOGIN:")
        print(f"   Email: {provider_user.email}")
        print("   Password: provider123")
        print("   Features: Manage own services, view bookings")
        
        print("\n🌐 WEBSITE ACCESS:")
        print("   URL: http://127.0.0.1:8000/")
        print("   Same website for all users!")
        
        print("\n✨ FEATURES:")
        print("   ✅ Role-based navigation")
        print("   ✅ Unified login system")
        print("   ✅ Same website design for all")
        print("   ✅ Admin can upload services")
        print("   ✅ Users can book services")
        print("   ✅ Indian Rupee currency")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_test_users()
    if success:
        print("\n🚀 READY TO TEST THE UNIFIED SYSTEM!")
    else:
        print("\n❌ Please check the errors above.")
