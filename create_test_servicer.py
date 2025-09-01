#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def create_test_servicer():
    """Create a test servicer (provider) user for testing the servicer dashboard"""
    print("🚀 Creating Test Servicer for Dashboard Testing\n")
    
    try:
        from users.models import User
        from services.models import ProviderProfile
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Create servicer user
        servicer_email = 'servicer@example.com'
        servicer_password = 'servicer123'
        
        # Check if servicer already exists
        try:
            servicer_user = User.objects.get(email=servicer_email)
            print(f"✅ Servicer user already exists: {servicer_email}")
        except User.DoesNotExist:
            # Create new servicer user
            servicer_user = User.objects.create_user(
                email=servicer_email,
                password=servicer_password,
                first_name='John',
                last_name='Servicer',
                user_type='provider'
            )
            print(f"✅ Created servicer user: {servicer_email}")
        
        # Create or get provider profile
        try:
            provider_profile = ProviderProfile.objects.get(user=servicer_user)
            print(f"✅ Provider profile already exists")
        except ProviderProfile.DoesNotExist:
            provider_profile = ProviderProfile.objects.create(
                user=servicer_user,
                company_name='John\'s Home Services',
                business_description='Professional home service provider',
                phone_number='+91-9876543210',
                address='123 Service Street, City',
                is_verified=True,
                is_available=True
            )
            print(f"✅ Created provider profile: {provider_profile.company_name}")
        
        # Create test bookings with invoices for this servicer
        print(f"\n📝 Creating test bookings for servicer...")
        
        # Get or create customer
        try:
            customer = User.objects.get(email='test@example.com')
        except User.DoesNotExist:
            customer = User.objects.create_user(
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='Customer',
                user_type='customer'
            )
            print(f"✅ Created test customer: test@example.com")
        
        # Create test bookings using MongoDB
        import pymongo
        from django.conf import settings
        from bson import ObjectId
        from datetime import datetime, timedelta
        
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Clear existing test bookings for this provider
        db['services_booking'].delete_many({'provider_id': servicer_user.id})
        db['services_invoice'].delete_many({})
        
        # Create test bookings
        test_bookings = [
            {
                'service_name': 'Plumbing Repair',
                'amount': 1500,
                'address': '123 Main Street, Apartment 4B',
                'phone': '+91-9876543210',
                'instructions': 'Fix kitchen sink leak'
            },
            {
                'service_name': 'Electrical Work',
                'amount': 2200,
                'address': '456 Oak Avenue, House 12',
                'phone': '+91-8765432109',
                'instructions': 'Install ceiling fan in bedroom'
            },
            {
                'service_name': 'AC Repair',
                'amount': 1800,
                'address': '789 Pine Road, Villa 3',
                'phone': '+91-7654321098',
                'instructions': 'AC not cooling properly'
            }
        ]
        
        created_bookings = []
        for i, booking_data in enumerate(test_bookings):
            # Create booking
            booking_doc = {
                'customer_id': customer.id,
                'provider_id': servicer_user.id,
                'status': 'confirmed',
                'total_amount': booking_data['amount'],
                'booking_date': datetime.now() + timedelta(days=i+1),
                'address': booking_data['address'],
                'phone_number': booking_data['phone'],
                'notes': f"Booking for {booking_data['service_name']} - Provider: {servicer_user.get_full_name()}",
                'special_instructions': booking_data['instructions'],
                'is_paid': True,
                'payment_status': 'paid',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            booking_result = db['services_booking'].insert_one(booking_doc)
            booking_id = booking_result.inserted_id
            
            # Create invoice
            invoice_doc = {
                'booking_id': booking_id,
                'invoice_number': f"INV-{str(booking_id)[:8].upper()}",
                'generated_at': datetime.now(),
                'subtotal': float(booking_data['amount']),
                'tax_amount': float(booking_data['amount']) * 0.18,
                'total_amount': float(booking_data['amount']) * 1.18
            }
            
            invoice_result = db['services_invoice'].insert_one(invoice_doc)
            
            created_bookings.append({
                'booking_id': str(booking_id),
                'invoice_number': invoice_doc['invoice_number'],
                'service_name': booking_data['service_name'],
                'amount': booking_data['amount']
            })
            
            print(f"   ✅ Created booking: {booking_data['service_name']} - Invoice: {invoice_doc['invoice_number']}")
        
        print(f"\n🎉 Test servicer setup completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   • Servicer Email: {servicer_email}")
        print(f"   • Password: {servicer_password}")
        print(f"   • Company: {provider_profile.company_name}")
        print(f"   • Test Bookings: {len(created_bookings)}")
        
        print(f"\n🔗 Testing URLs:")
        print(f"   • Login: http://127.0.0.1:8000/accounts/login/")
        print(f"   • Servicer Dashboard: http://127.0.0.1:8000/servicer-dashboard/")
        
        print(f"\n📝 Test Instructions:")
        print(f"   1. Login with: {servicer_email} / {servicer_password}")
        print(f"   2. You'll be redirected to servicer dashboard")
        print(f"   3. You should see {len(created_bookings)} assigned services")
        print(f"   4. Each service has an invoice ID for status updates")
        print(f"   5. Test marking services as completed/rejected")
        
        print(f"\n📋 Created Invoice IDs:")
        for booking in created_bookings:
            print(f"   • {booking['invoice_number']} - {booking['service_name']} (₹{booking['amount']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test servicer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_test_servicer()
    
    if success:
        print(f"\n🎉 Test servicer created successfully!")
        print(f"\n🚀 Ready to test servicer dashboard functionality!")
    else:
        print(f"\n❌ Failed to create test servicer.")
