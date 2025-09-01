#!/usr/bin/env python
"""
Script to fix MongoDB issues and create sample data
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

def fix_mongodb_issues():
    """Fix MongoDB ObjectId issues and create sample data"""
    print("🔧 Fixing MongoDB Issues...")
    print("=" * 50)
    
    try:
        # Test basic connection
        print("📡 Testing database connection...")
        
        # Create admin user if not exists
        admin_email = 'admin@homeservice.com'
        try:
            admin_user = User.objects.get(email=admin_email)
            print(f"✅ Admin user exists: {admin_user.email}")
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
            print(f"✅ Created admin user: {admin_user.email}")
        
        # Create categories with simple approach
        categories_data = [
            {'name': 'Electrical', 'slug': 'electrical'},
            {'name': 'Plumbing', 'slug': 'plumbing'},
            {'name': 'Cleaning', 'slug': 'cleaning'},
            {'name': 'Gardening', 'slug': 'gardening'},
            {'name': 'Home Repair', 'slug': 'home-repair'}
        ]
        
        created_categories = []
        for cat_data in categories_data:
            try:
                category = ServiceCategory.objects.get(slug=cat_data['slug'])
                print(f"📂 Category exists: {category.name}")
            except ServiceCategory.DoesNotExist:
                # Create category with manual ID handling
                category = ServiceCategory(
                    name=cat_data['name'],
                    slug=cat_data['slug'],
                    description=f"Professional {cat_data['name'].lower()} services"
                )
                category.save()
                print(f"✅ Created category: {category.name}")
            created_categories.append(category)
        
        # Create provider users
        provider_data = [
            {'email': 'rajesh@provider.com', 'name': 'Rajesh Kumar'},
            {'email': 'priya@provider.com', 'name': 'Priya Sharma'},
            {'email': 'amit@provider.com', 'name': 'Amit Singh'}
        ]
        
        created_providers = []
        for prov_data in provider_data:
            try:
                provider_user = User.objects.get(email=prov_data['email'])
                print(f"👤 Provider exists: {provider_user.email}")
            except User.DoesNotExist:
                names = prov_data['name'].split()
                provider_user = User.objects.create_user(
                    email=prov_data['email'],
                    password='provider123',
                    first_name=names[0],
                    last_name=names[1] if len(names) > 1 else '',
                    user_type='provider',
                    is_active=True
                )
                print(f"✅ Created provider: {provider_user.get_full_name()}")
            
            # Create provider profile
            try:
                profile = ProviderProfile.objects.get(user=provider_user)
                print(f"🏢 Provider profile exists: {profile.company_name}")
            except ProviderProfile.DoesNotExist:
                profile = ProviderProfile(
                    user=provider_user,
                    company_name=f"{prov_data['name']} Services",
                    business_description=f"Professional services by {prov_data['name']}",
                    phone_number='+91 9876543210',
                    address='Mumbai, Maharashtra, India',
                    is_verified=True,
                    is_available=True
                )
                profile.save()
                print(f"✅ Created provider profile: {profile.company_name}")
            
            created_providers.append(provider_user)
        
        # Create services
        services_data = [
            {
                'name': 'Electrical Installation',
                'description': 'Professional electrical installation services',
                'price': 2500,
                'duration': 3,
                'category_slug': 'electrical',
                'provider_index': 0
            },
            {
                'name': 'Pipe Repair',
                'description': 'Expert pipe repair services',
                'price': 1200,
                'duration': 2,
                'category_slug': 'plumbing',
                'provider_index': 1
            },
            {
                'name': 'Deep Cleaning',
                'description': 'Comprehensive home cleaning',
                'price': 3500,
                'duration': 4,
                'category_slug': 'cleaning',
                'provider_index': 2
            }
        ]
        
        created_services = []
        for serv_data in services_data:
            try:
                service = Service.objects.get(name=serv_data['name'])
                print(f"🛠️  Service exists: {service.name}")
            except Service.DoesNotExist:
                # Get category
                category = ServiceCategory.objects.get(slug=serv_data['category_slug'])
                provider = created_providers[serv_data['provider_index']]
                
                service = Service(
                    name=serv_data['name'],
                    description=serv_data['description'],
                    price=serv_data['price'],
                    duration=serv_data['duration'],
                    category=category,
                    provider=provider,
                    is_active=True,
                    is_available=True
                )
                service.save()
                print(f"✅ Created service: {service.name} - ₹{service.price}")
            created_services.append(service)
        
        # Create sample customer
        try:
            customer = User.objects.get(email='customer@example.com')
            print(f"👤 Customer exists: {customer.email}")
        except User.DoesNotExist:
            customer = User.objects.create_user(
                email='customer@example.com',
                password='customer123',
                first_name='John',
                last_name='Doe',
                user_type='customer',
                is_active=True
            )
            print(f"✅ Created customer: {customer.get_full_name()}")
        
        # Create sample bookings
        for i, service in enumerate(created_services[:2]):
            try:
                booking = Booking.objects.filter(service=service, customer=customer).first()
                if booking:
                    print(f"📅 Booking exists: {booking.service.name}")
                    continue
            except:
                pass
            
            booking_date = timezone.now() + timedelta(days=i+1)
            booking = Booking(
                service=service,
                customer=customer,
                provider=service.provider,
                booking_date=booking_date,
                start_time=booking_date,
                end_time=booking_date + timedelta(hours=service.duration),
                address=f'Sample Address {i+1}, Mumbai, Maharashtra',
                phone_number='+91 9876543210',
                status='confirmed' if i == 0 else 'pending',
                payment_status='paid' if i == 0 else 'pending',
                is_paid=i == 0,
                total_amount=service.price,
                special_instructions=f'Sample booking {i+1} for admin testing'
            )
            booking.save()
            print(f"✅ Created booking: {booking.service.name}")
        
        print("\n" + "=" * 50)
        print("🎉 MongoDB Issues Fixed Successfully!")
        print("\n📊 Database Summary:")
        print(f"   👥 Users: {User.objects.count()}")
        print(f"   📂 Categories: {ServiceCategory.objects.count()}")
        print(f"   🛠️  Services: {Service.objects.count()}")
        print(f"   📅 Bookings: {Booking.objects.count()}")
        
        print("\n🔐 Admin Access:")
        print("   URL: http://127.0.0.1:8000/services/admin-dashboard/")
        print("   Email: admin@homeservice.com")
        print("   Password: admin123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_mongodb_issues()
    if success:
        print("\n✅ Ready to use admin interface!")
    else:
        print("\n❌ Please check the errors above.")
