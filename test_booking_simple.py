#!/usr/bin/env python
"""
Simple test to create a booking directly
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from django.contrib.auth import get_user_model
from services.models import Booking, ServiceCategory, Service
from datetime import datetime, timedelta
from decimal import Decimal

def test_booking_creation():
    """Test creating a booking directly"""
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
    
    # Create a test category and service
    try:
        category = ServiceCategory.objects.get(slug='electrical')
        print(f"Using existing category: {category.name}")
    except ServiceCategory.DoesNotExist:
        category = ServiceCategory(
            slug='electrical',
            name='Electrical',
            description='Electrical services'
        )
        category.save()
        print(f"Created new category: {category.name}")

    # Ensure category is saved and has an ID
    if not category.pk:
        category.save()

    print(f"Category ID: {category.pk}")

    # Create a test service
    try:
        service = Service.objects.get(name='Test Electrical Installation')
        print(f"Using existing service: {service.name}")
    except Service.DoesNotExist:
        service = Service(
            name='Test Electrical Installation',
            category=category,
            provider=user,
            description='Test electrical installation service',
            price=Decimal('2500.00'),
            duration=3,
            is_active=True,
            is_available=True
        )
        service.save()
        print(f"Created new service: {service.name}")
    print(f"Service: {service.name}")
    
    # Create a test booking
    tomorrow = datetime.now() + timedelta(days=1)
    
    try:
        booking = Booking.objects.create(
            customer=user,
            service=service,
            provider=user,
            status='pending',
            booking_date=tomorrow,
            address='123 Test Street, Test City',
            phone_number='9876543210',
            total_amount=Decimal('2500.00'),
            special_instructions='Test booking for electrical installation'
        )
        print(f"✅ Booking created successfully: {booking.id}")
        print(f"Booking details: {booking}")
        
        # Test payment URL
        from django.urls import reverse
        payment_url = reverse('services:payment', kwargs={'booking_id': booking.id})
        print(f"Payment URL: http://127.0.0.1:8000{payment_url}")
        
        return booking
        
    except Exception as e:
        print(f"❌ Error creating booking: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None

if __name__ == '__main__':
    booking = test_booking_creation()
    if booking:
        print(f"\n✅ Test completed successfully!")
        print(f"You can now test the payment page at: http://127.0.0.1:8000/services/payment/{booking.id}/")
    else:
        print(f"\n❌ Test failed!")
