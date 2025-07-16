#!/usr/bin/env python
import os
import sys
from pymongo import MongoClient
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

def create_test_booking():
    print("🔧 Creating test booking directly in MongoDB...")
    
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['homeservice_db']
        
        # Collections
        users_collection = db['users_user']
        bookings_collection = db['services_booking']
        services_collection = db['services_service']
        categories_collection = db['services_servicecategory']
        
        # Check existing data
        print(f"Existing users: {users_collection.count_documents({})}")
        print(f"Existing bookings: {bookings_collection.count_documents({})}")
        print(f"Existing services: {services_collection.count_documents({})}")
        
        # Get existing customer
        customer = users_collection.find_one({'email': 'customer@test.com'})
        if not customer:
            # Create customer
            customer_id = users_collection.insert_one({
                'email': 'customer@test.com',
                'first_name': 'Test',
                'last_name': 'Customer',
                'user_type': 'customer',
                'is_active': True,
                'is_staff': False,
                'is_superuser': False,
                'date_joined': datetime.now(),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'password': 'pbkdf2_sha256$260000$test$test',
                'username': 'customer_test',
                'phone_number': '9876543210'
            }).inserted_id
            customer = {'_id': customer_id, 'email': 'customer@test.com'}
            print(f"✅ Created customer: {customer['email']}")
        
        # Get existing provider
        provider = users_collection.find_one({'email': 'provider@test.com'})
        if not provider:
            # Create provider
            provider_id = users_collection.insert_one({
                'email': 'provider@test.com',
                'first_name': 'Test',
                'last_name': 'Provider',
                'user_type': 'provider',
                'is_active': True,
                'is_staff': False,
                'is_superuser': False,
                'date_joined': datetime.now(),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'password': 'pbkdf2_sha256$260000$test$test',
                'username': 'provider_test',
                'phone_number': '9876543211'
            }).inserted_id
            provider = {'_id': provider_id, 'email': 'provider@test.com'}
            print(f"✅ Created provider: {provider['email']}")
        
        # Create simple test booking
        booking_data = {
            'customer_id': customer['_id'],
            'provider_id': provider['_id'],
            'service_id': None,  # We'll set this to None for now
            'status': 'pending',
            'booking_date': datetime.now() + timedelta(days=1),
            'total_amount': 2500.00,
            'address': '123 Test Street, Mumbai, Maharashtra',
            'phone_number': '9876543210',
            'notes': 'Test booking for admin approval',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'payment_status': 'pending',
            'is_paid': False
        }
        
        # Insert booking
        booking_id = bookings_collection.insert_one(booking_data).inserted_id
        print(f"✅ Created test booking: {booking_id}")
        
        # Create another booking
        booking_data2 = {
            'customer_id': customer['_id'],
            'provider_id': provider['_id'],
            'service_id': None,
            'status': 'pending',
            'booking_date': datetime.now() + timedelta(days=2),
            'total_amount': 3000.00,
            'address': '456 Another Street, Delhi, India',
            'phone_number': '9876543210',
            'notes': 'Another test booking',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'payment_status': 'pending',
            'is_paid': False
        }
        
        booking_id2 = bookings_collection.insert_one(booking_data2).inserted_id
        print(f"✅ Created second test booking: {booking_id2}")
        
        # Summary
        total_bookings = bookings_collection.count_documents({})
        pending_bookings = bookings_collection.count_documents({'status': 'pending'})
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total bookings: {total_bookings}")
        print(f"   Pending bookings: {pending_bookings}")
        print(f"   Customer email: customer@test.com")
        print(f"   Admin email: admin@homeservice.com")
        print(f"   Admin password: admin123")
        print(f"\n🎯 Ready for testing! Go to: http://127.0.0.1:8000/services/admin-bookings/")
        
    except Exception as e:
        print(f"❌ Error creating test booking: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_test_booking()
