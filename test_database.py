#!/usr/bin/env python
"""
Test database functionality and create sample data
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

def test_database():
    """Test database functionality and create sample data"""
    print("🔧 TESTING DATABASE FUNCTIONALITY")
    print("=" * 50)
    
    try:
        # Test 1: Database Connection
        print("1. Testing database connection...")
        from django.db import connection
        cursor = connection.cursor()
        print("   ✅ Database connection successful")
        
        # Test 2: Create Admin User
        print("\n2. Creating admin user...")
        admin_email = 'admin@homeservice.com'
        try:
            admin_user = User.objects.get(email=admin_email)
            print(f"   ✅ Admin user exists: {admin_user.email}")
        except User.DoesNotExist:
            admin_user = User.objects.create_user(
                email=admin_email,
                password='admin123',
                first_name='Admin',
                last_name='User',
                is_staff=True,
                is_superuser=True,
                user_type='customer'
            )
            print(f"   ✅ Created admin user: {admin_user.email}")
        
        # Test 3: Create Categories
        print("\n3. Creating service categories...")
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
        
        # Test 4: Create Provider Users
        print("\n4. Creating provider users...")
        provider_data = [
            {'email': 'rajesh@provider.com', 'first_name': 'Rajesh', 'last_name': 'Kumar'},
            {'email': 'priya@provider.com', 'first_name': 'Priya', 'last_name': 'Sharma'},
        ]
        
        created_providers = []
        for prov_data in provider_data:
            try:
                provider_user = User.objects.get(email=prov_data['email'])
                print(f"   👤 Provider exists: {provider_user.email}")
            except User.DoesNotExist:
                provider_user = User.objects.create_user(
                    email=prov_data['email'],
                    password='provider123',
                    first_name=prov_data['first_name'],
                    last_name=prov_data['last_name'],
                    user_type='provider',
                    is_active=True
                )
                print(f"   ✅ Created provider: {provider_user.get_full_name()}")
            
            # Create provider profile
            try:
                profile = ProviderProfile.objects.get(user=provider_user)
                print(f"   🏢 Provider profile exists: {profile.company_name}")
            except ProviderProfile.DoesNotExist:
                profile = ProviderProfile.objects.create(
                    user=provider_user,
                    company_name=f"{provider_user.get_full_name()} Services",
                    business_description=f"Professional services by {provider_user.get_full_name()}",
                    phone_number='+91 9876543210',
                    address='Mumbai, Maharashtra, India',
                    is_verified=True,
                    is_available=True
                )
                print(f"   ✅ Created provider profile: {profile.company_name}")
            
            created_providers.append(provider_user)
        
        # Test 5: Create Services
        print("\n5. Creating services...")
        services_data = [
            {
                'name': 'Electrical Installation',
                'description': 'Professional electrical installation services',
                'price': 2500,
                'duration': 3,
                'category': created_categories[0],  # Electrical
                'provider': created_providers[0]
            },
            {
                'name': 'Pipe Repair',
                'description': 'Expert pipe repair services',
                'price': 1200,
                'duration': 2,
                'category': created_categories[1],  # Plumbing
                'provider': created_providers[1]
            },
            {
                'name': 'Deep Cleaning',
                'description': 'Comprehensive home cleaning',
                'price': 3500,
                'duration': 4,
                'category': created_categories[2],  # Cleaning
                'provider': created_providers[0]
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
        
        # Test 6: Create Customer and Booking
        print("\n6. Creating customer and sample booking...")
        try:
            customer = User.objects.get(email='customer@example.com')
            print(f"   👤 Customer exists: {customer.email}")
        except User.DoesNotExist:
            customer = User.objects.create_user(
                email='customer@example.com',
                password='customer123',
                first_name='John',
                last_name='Doe',
                user_type='customer',
                is_active=True
            )
            print(f"   ✅ Created customer: {customer.get_full_name()}")
        
        # Create sample booking
        if created_services:
            service = created_services[0]
            try:
                booking = Booking.objects.filter(service=service, customer=customer).first()
                if booking:
                    print(f"   📅 Booking exists: {booking.service.name}")
                else:
                    raise Booking.DoesNotExist
            except Booking.DoesNotExist:
                booking_date = timezone.now() + timedelta(days=1)
                booking = Booking.objects.create(
                    service=service,
                    customer=customer,
                    provider=service.provider,
                    booking_date=booking_date,
                    address='Sample Address, Mumbai, Maharashtra',
                    phone_number='+91 9876543210',
                    status='confirmed',
                    payment_status='paid',
                    is_paid=True,
                    total_amount=service.price,
                    special_instructions='Sample booking for testing'
                )
                print(f"   ✅ Created booking: {booking.service.name}")
        
        # Test 7: Database Summary
        print("\n7. Database summary...")
        print(f"   👥 Users: {User.objects.count()}")
        print(f"   📂 Categories: {ServiceCategory.objects.count()}")
        print(f"   🛠️  Services: {Service.objects.count()}")
        print(f"   📅 Bookings: {Booking.objects.count()}")
        print(f"   🏢 Provider Profiles: {ProviderProfile.objects.count()}")
        
        print("\n" + "=" * 50)
        print("🎉 DATABASE TEST COMPLETED SUCCESSFULLY!")
        print("\n🔐 Admin Access:")
        print("   URL: http://127.0.0.1:8000/services/admin-dashboard/")
        print("   Email: admin@homeservice.com")
        print("   Password: admin123")
        
        print("\n🌐 User Access:")
        print("   URL: http://127.0.0.1:8000/")
        print("   Customer: customer@example.com / customer123")
        print("   Provider: rajesh@provider.com / provider123")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_database()
    if success:
        print("\n✅ Database is ready for both admin and user interfaces!")
    else:
        print("\n❌ Please check the errors above.")
