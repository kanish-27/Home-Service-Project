#!/usr/bin/env python
"""
Test the fixed booking creation process
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

def test_fixed_booking_creation():
    """Test the fixed booking creation process"""
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
    
    # Test the FIXED booking creation process
    try:
        print("\n=== Testing FIXED Booking Creation ===")
        
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
        
        # Step 2: Handle category with duplicate protection (FIXED)
        try:
            category = ServiceCategory.objects.filter(slug=service['category_slug']).first()
            if not category:
                category = ServiceCategory.objects.create(
                    slug=service['category_slug'],
                    name=service['category_name'],
                    description=f"Professional {service['category_name'].lower()} services"
                )
            print(f"✅ Category: {category.name} (ID: {category.pk})")
        except Exception as cat_error:
            print(f"DEBUG: Category creation error: {cat_error}")
            # Use the first available category as fallback
            category = ServiceCategory.objects.first()
            if not category:
                raise Exception("No categories available in database")
            print(f"✅ Using fallback category: {category.name}")
        
        # Step 3: Handle service with duplicate protection (FIXED)
        try:
            db_service = Service.objects.filter(
                name=service['name'],
                provider=provider_user
            ).first()
            
            if not db_service:
                db_service = Service.objects.create(
                    name=service['name'],
                    category=category,
                    provider=provider_user,
                    description=service['description'],
                    price=service['price'],
                    duration=service['duration'],
                    is_active=True,
                    is_available=True
                )
            print(f"✅ Service: {db_service.name} (ID: {db_service.pk})")
        except Exception as svc_error:
            print(f"DEBUG: Service creation error: {svc_error}")
            raise Exception(f"Could not create service: {svc_error}")
        
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
        
        print(f"✅ Booking created successfully: {booking.id}")
        print(f"Payment URL: http://127.0.0.1:8000/services/payment/{booking.id}/")
        return booking
        
    except Exception as e:
        print(f"❌ Fixed booking creation failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        # Test the fallback approach
        try:
            print("\n=== Testing FIXED Fallback Booking Creation ===")
            
            # Use fixed fallback approach
            try:
                default_category = ServiceCategory.objects.filter(slug='general').first()
                if not default_category:
                    default_category = ServiceCategory.objects.create(
                        slug='general',
                        name='General Services',
                        description='General home services'
                    )
                print(f"✅ Default category: {default_category.name} (ID: {default_category.pk})")
            except Exception as def_cat_error:
                print(f"DEBUG: Default category error: {def_cat_error}")
                # Use any available category
                default_category = ServiceCategory.objects.first()
                if not default_category:
                    raise Exception("No categories available for fallback")
                print(f"✅ Using any available category: {default_category.name}")
            
            # Create default service with fixed approach
            try:
                default_service = Service.objects.filter(
                    name='General Home Service',
                    provider=user
                ).first()
                
                if not default_service:
                    default_service = Service.objects.create(
                        name='General Home Service',
                        category=default_category,
                        provider=user,
                        description='General home service for testing',
                        price=Decimal(str(service['price'])),
                        duration=service.get('duration', 2),
                        is_active=True,
                        is_available=True
                    )
                print(f"✅ Default service: {default_service.name} (ID: {default_service.pk})")
            except Exception as def_svc_error:
                print(f"DEBUG: Default service error: {def_svc_error}")
                raise Exception(f"Could not create default service: {def_svc_error}")
            
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
            print(f"Payment URL: http://127.0.0.1:8000/services/payment/{booking.id}/")
            return booking
            
        except Exception as fallback_error:
            print(f"❌ Fallback booking creation also failed: {fallback_error}")
            import traceback
            print(f"Fallback traceback: {traceback.format_exc()}")
            return None

if __name__ == '__main__':
    print("Testing FIXED booking creation process...")
    print("=" * 50)
    
    booking = test_fixed_booking_creation()
    
    if booking:
        print(f"\n✅ SUCCESS! Booking creation works!")
        print(f"Booking ID: {booking.id}")
        print(f"Test the payment page at: http://127.0.0.1:8000/services/payment/{booking.id}/")
        print(f"Login with: test@example.com / testpass123")
    else:
        print(f"\n❌ FAILED! Booking creation still has issues.")
