#!/usr/bin/env python
"""
Debug booking creation to find the exact error
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from django.contrib.auth import get_user_model
from services.models import Booking, ServiceCategory, Service
from services.views import ServiceListView
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

def debug_booking_creation():
    """Debug the exact booking creation process"""
    User = get_user_model()
    
    # Get or create test user
    try:
        user = User.objects.get(email='test@example.com')
        print(f"Using existing user: {user.email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        print(f"Created new user: {user.email}")
    
    # Get sample service data (same as in ServiceBookingView)
    service_list_view = ServiceListView()
    sample_services = service_list_view.get_sample_services()
    
    # Get service with ID 1 (same as in the booking form)
    service = None
    for s in sample_services:
        if s['id'] == 1:
            service = s
            break
    
    if not service:
        print("❌ Service not found in sample data")
        return
    
    print(f"Service found: {service['name']}")
    print(f"Service provider: {service['provider']['user']['get_full_name']}")
    print(f"Service category: {service['category_name']}")
    
    # Test the exact same process as ServiceBookingView
    try:
        print("\n=== Testing Primary Booking Creation ===")
        
        # Step 1: Create provider user
        provider_user, created = User.objects.get_or_create(
            email=service['provider']['user']['email'],
            defaults={
                'first_name': service['provider']['user']['get_full_name'].split()[0],
                'last_name': ' '.join(service['provider']['user']['get_full_name'].split()[1:]),
                'user_type': 'provider',
                'is_active': True
            }
        )
        print(f"✅ Provider user: {provider_user.email} (created: {created})")
        
        # Step 2: Create category
        category, created = ServiceCategory.objects.get_or_create(
            slug=service['category_slug'],
            defaults={
                'name': service['category_name'],
                'description': f"Professional {service['category_name'].lower()} services"
            }
        )
        print(f"✅ Category: {category.name} (created: {created})")
        
        # Step 3: Create service
        db_service, created = Service.objects.get_or_create(
            name=service['name'],
            category=category,
            provider=provider_user,
            defaults={
                'description': service['description'],
                'price': service['price'],
                'duration': service['duration'],
                'is_active': True,
                'is_available': True
            }
        )
        print(f"✅ Service: {db_service.name} (created: {created})")
        
        # Step 4: Create booking
        tomorrow = datetime.now() + timedelta(days=1)
        booking_datetime = timezone.make_aware(tomorrow)
        
        booking_amount = Decimal(str(service['price']))
        
        booking = Booking.objects.create(
            customer=user,
            service=db_service,
            provider=provider_user,
            status='pending',
            booking_date=booking_datetime,
            address='123 Test Street, Test City',
            phone_number='9876543210',
            total_amount=booking_amount,
            special_instructions='Test booking',
            notes=f"Booking for {service['name']} - Provider: {service['provider']['user']['get_full_name']}"
        )
        
        print(f"✅ Primary booking created successfully: {booking.id}")
        return booking
        
    except Exception as e:
        print(f"❌ Primary booking creation failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        # Test fallback booking creation
        try:
            print("\n=== Testing Fallback Booking Creation ===")
            
            # Create default category and service
            default_category, created = ServiceCategory.objects.get_or_create(
                slug='general',
                defaults={
                    'name': 'General Services',
                    'description': 'General home services'
                }
            )
            print(f"✅ Default category: {default_category.name} (created: {created})")
            
            default_service, created = Service.objects.get_or_create(
                name='General Home Service',
                category=default_category,
                provider=user,
                defaults={
                    'description': 'General home service for testing',
                    'price': Decimal(str(service['price'])),
                    'duration': service.get('duration', 2),
                    'is_active': True,
                    'is_available': True
                }
            )
            print(f"✅ Default service: {default_service.name} (created: {created})")
            
            # Create fallback booking
            booking = Booking.objects.create(
                customer=user,
                service=default_service,
                provider=user,
                status='pending',
                booking_date=booking_datetime,
                address='123 Test Street, Test City',
                phone_number='9876543210',
                total_amount=Decimal(str(service['price'])),
                special_instructions='Test booking',
                notes=f"Sample booking for {service['name']}"
            )
            
            print(f"✅ Fallback booking created successfully: {booking.id}")
            return booking
            
        except Exception as fallback_error:
            print(f"❌ Fallback booking creation also failed: {fallback_error}")
            import traceback
            print(f"Fallback traceback: {traceback.format_exc()}")
            return None

def test_database_connection():
    """Test basic database operations"""
    print("\n=== Testing Database Connection ===")

    try:
        User = get_user_model()

        # Test User model
        user_count = User.objects.count()
        print(f"✅ Users in database: {user_count}")
        
        # Test ServiceCategory model
        category_count = ServiceCategory.objects.count()
        print(f"✅ Categories in database: {category_count}")
        
        # Test Service model
        service_count = Service.objects.count()
        print(f"✅ Services in database: {service_count}")
        
        # Test Booking model
        booking_count = Booking.objects.count()
        print(f"✅ Bookings in database: {booking_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

if __name__ == '__main__':
    print("Debugging booking creation process...")
    print("=" * 50)
    
    # Test database connection first
    if test_database_connection():
        print("\n" + "=" * 50)
        booking = debug_booking_creation()
        
        if booking:
            print(f"\n✅ Booking creation successful!")
            print(f"Booking ID: {booking.id}")
            print(f"Payment URL: http://127.0.0.1:8000/services/payment/{booking.id}/")
        else:
            print(f"\n❌ Booking creation failed!")
    else:
        print("❌ Database connection failed!")
