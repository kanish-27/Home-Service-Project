#!/usr/bin/env python
import os
import sys
from pymongo import MongoClient
from datetime import datetime
import uuid

def create_test_notifications():
    print("🔔 Creating test notifications...")
    
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['homeservice_db']
        
        # Collections
        users_collection = db['users_user']
        notifications_collection = db['users_notification']
        
        # Get existing users
        users = list(users_collection.find({'email': {'$in': ['customer@test.com', 'admin@homeservice.com']}}))
        
        if not users:
            print("❌ No test users found. Please create users first.")
            return
        
        for user in users:
            user_id = user['_id']
            user_email = user['email']
            
            print(f"📧 Creating notifications for {user_email}")
            
            # Create test notifications
            notifications = [
                {
                    'user_id': user_id,
                    'notification_type': 'booking_created',
                    'title': 'New Booking Created',
                    'message': 'Your booking for home cleaning service has been created successfully.',
                    'is_read': False,
                    'related_object_id': None,
                    'related_content_type': 'booking',
                    'created_at': datetime.now()
                },
                {
                    'user_id': user_id,
                    'notification_type': 'booking_confirmed',
                    'title': 'Booking Confirmed',
                    'message': 'Your booking has been confirmed by the service provider.',
                    'is_read': False,
                    'related_object_id': None,
                    'related_content_type': 'booking',
                    'created_at': datetime.now()
                },
                {
                    'user_id': user_id,
                    'notification_type': 'system',
                    'title': 'Welcome to HomeService',
                    'message': 'Welcome to our platform! We are excited to have you on board.',
                    'is_read': True,
                    'related_object_id': None,
                    'related_content_type': None,
                    'created_at': datetime.now()
                },
                {
                    'user_id': user_id,
                    'notification_type': 'payment_received',
                    'title': 'Payment Received',
                    'message': 'We have received your payment of ₹2500 for the home cleaning service.',
                    'is_read': False,
                    'related_object_id': None,
                    'related_content_type': 'payment',
                    'created_at': datetime.now()
                }
            ]
            
            # Insert notifications
            result = notifications_collection.insert_many(notifications)
            print(f"✅ Created {len(result.inserted_ids)} notifications for {user_email}")
        
        # Summary
        total_notifications = notifications_collection.count_documents({})
        unread_notifications = notifications_collection.count_documents({'is_read': False})
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total notifications: {total_notifications}")
        print(f"   Unread notifications: {unread_notifications}")
        print(f"\n🎯 Ready for testing! Go to: http://127.0.0.1:8000/profile/notifications/")
        
    except Exception as e:
        print(f"❌ Error creating test notifications: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_test_notifications()
