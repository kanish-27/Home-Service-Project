#!/usr/bin/env python
"""
Script to create sample database records for the booking system.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from users.models import User
from services.models import ServiceCategory, Service, ProviderProfile

def create_sample_records():
    print("Creating sample database records...")
    
    try:
        # Create sample provider user
        provider_user, created = User.objects.get_or_create(
            email='sample.provider@example.com',
            defaults={
                'first_name': 'Sample',
                'last_name': 'Provider',
                'user_type': 'provider',
                'is_active': True
            }
        )
        if created:
            provider_user.set_password('samplepass123')
            provider_user.save()
            print(f"✅ Created provider user: {provider_user.email}")
        else:
            print(f"✅ Provider user already exists: {provider_user.email}")
        
        # Create sample category
        category, created = ServiceCategory.objects.get_or_create(
            name='Sample Services',
            defaults={
                'slug': 'sample-services',
                'description': 'Sample service category for demonstration'
            }
        )
        if created:
            print(f"✅ Created category: {category.name}")
        else:
            print(f"✅ Category already exists: {category.name}")
        
        # Create provider profile
        provider_profile, created = ProviderProfile.objects.get_or_create(
            user=provider_user,
            defaults={
                'business_name': 'Sample Service Provider',
                'description': 'Professional sample service provider',
                'phone_number': '+91-9876543210',
                'is_verified': True
            }
        )
        if created:
            print(f"✅ Created provider profile: {provider_profile.business_name}")
        else:
            print(f"✅ Provider profile already exists: {provider_profile.business_name}")
        
        # Create sample service
        service, created = Service.objects.get_or_create(
            name='Sample Service',
            defaults={
                'description': 'This is a sample service for demonstration purposes',
                'category': category,
                'provider': provider_profile,
                'price': 1500.00,
                'duration': 2,
                'is_active': True,
                'is_available': True
            }
        )
        if created:
            print(f"✅ Created service: {service.name}")
        else:
            print(f"✅ Service already exists: {service.name}")
        
        print()
        print("🎉 Sample records created successfully!")
        print(f"   Provider User ID: {provider_user.id}")
        print(f"   Service ID: {service.id}")
        print(f"   Category ID: {category.id}")
        
        return {
            'provider_user_id': provider_user.id,
            'service_id': service.id,
            'category_id': category.id
        }
        
    except Exception as e:
        print(f"❌ Error creating sample records: {e}")
        return None

if __name__ == '__main__':
    create_sample_records()
