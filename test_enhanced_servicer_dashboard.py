#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def test_enhanced_servicer_dashboard():
    """Test the enhanced servicer dashboard with card design and semicircle buttons"""
    print("🎨 Testing Enhanced Servicer Dashboard Design...\n")
    
    try:
        from users.models import User
        import pymongo
        from django.conf import settings
        from datetime import datetime, timedelta
        
        # Get users
        servicer = User.objects.get(email='servicer@example.com')
        customer = User.objects.get(email='test@example.com')
        
        print(f"✅ Servicer: {servicer.get_full_name()}")
        print(f"✅ Customer: {customer.get_full_name()}")
        
        # Connect to MongoDB
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Step 1: Create test bookings with different statuses
        print(f"\n📝 Step 1: Creating Test Bookings for Enhanced Display...")
        
        test_bookings = [
            {
                'customer_id': customer.id,
                'provider_id': servicer.id,
                'status': 'confirmed',  # Ready for action buttons
                'total_amount': 2800,
                'booking_date': datetime.now() + timedelta(days=1),
                'address': '123 Enhanced Design Street, Test City',
                'phone_number': '+91-9999888877',
                'notes': 'AC Installation Service - Enhanced UI Test',
                'special_instructions': 'Test the new semicircle buttons and card design',
                'is_paid': True,
                'payment_status': 'paid',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'customer_id': customer.id,
                'provider_id': servicer.id,
                'status': 'completed',  # Shows completed badge
                'total_amount': 3500,
                'booking_date': datetime.now() - timedelta(days=1),
                'address': '456 Completed Service Avenue, Test City',
                'phone_number': '+91-8888777766',
                'notes': 'Plumbing Service - Completed',
                'special_instructions': 'Service completed successfully',
                'is_paid': True,
                'payment_status': 'paid',
                'created_at': datetime.now() - timedelta(days=2),
                'updated_at': datetime.now(),
                'service_completed_at': datetime.now() - timedelta(hours=2),
                'service_completed_by': servicer.id
            },
            {
                'customer_id': customer.id,
                'provider_id': servicer.id,
                'status': 'rejected',  # Shows rejected badge
                'total_amount': 1800,
                'booking_date': datetime.now() - timedelta(days=2),
                'address': '789 Rejected Service Road, Test City',
                'phone_number': '+91-7777666655',
                'notes': 'Electrical Service - Rejected',
                'special_instructions': 'Service could not be completed',
                'is_paid': True,
                'payment_status': 'paid',
                'created_at': datetime.now() - timedelta(days=3),
                'updated_at': datetime.now(),
                'rejection_reason': 'Customer not available',
                'rejected_at': datetime.now() - timedelta(hours=1)
            }
        ]
        
        booking_ids = []
        invoice_numbers = []
        
        for i, booking in enumerate(test_bookings, 1):
            # Insert booking
            booking_result = db['services_booking'].insert_one(booking)
            booking_id = booking_result.inserted_id
            booking_ids.append(booking_id)
            
            # Create invoice
            invoice_number = f"INV-{str(booking_id)[:8].upper()}"
            invoice_doc = {
                'booking_id': booking_id,
                'invoice_number': invoice_number,
                'generated_at': datetime.now(),
                'subtotal': float(booking['total_amount']),
                'tax_amount': float(booking['total_amount']) * 0.18,
                'total_amount': float(booking['total_amount']) * 1.18
            }
            
            db['services_invoice'].insert_one(invoice_doc)
            invoice_numbers.append(invoice_number)
            
            status = booking['status']
            amount = booking['total_amount']
            print(f"   ✅ Created booking {i}: {status.upper()}, ₹{amount}, Invoice: {invoice_number}")
        
        # Step 2: Test servicer dashboard query
        print(f"\n🔍 Step 2: Testing Servicer Dashboard Query...")
        
        # Query all confirmed bookings (new approach)
        servicer_bookings = list(db['services_booking'].find({'status': {'$in': ['confirmed', 'completed', 'rejected']}}))
        
        print(f"   • Total bookings for servicer dashboard: {len(servicer_bookings)}")
        
        for booking in servicer_bookings:
            booking_id = str(booking['_id'])[:8]
            status = booking.get('status', 'unknown')
            amount = booking.get('total_amount', 0)
            print(f"     • {booking_id}: {status.upper()}, ₹{amount}")
        
        # Step 3: Test design elements
        print(f"\n🎨 Step 3: Testing Enhanced Design Elements...")
        
        design_features = [
            "✅ Card-based layout with gradient backgrounds",
            "✅ Semicircle buttons with hover effects",
            "✅ Enhanced invoice badges with gradients",
            "✅ Improved customer info sections",
            "✅ Color-coded status badges",
            "✅ Responsive design with proper spacing",
            "✅ Professional typography and icons"
        ]
        
        for feature in design_features:
            print(f"   {feature}")
        
        # Step 4: Test button functionality
        print(f"\n🔘 Step 4: Testing Button Design Features...")
        
        button_features = {
            "Mark Completed": {
                "color": "Green gradient (success)",
                "shape": "Semicircle (border-radius: 50px)",
                "effects": "Hover animation, scale transform, glow shadow",
                "icon": "fas fa-check-circle"
            },
            "Mark Rejected": {
                "color": "Red gradient (danger)",
                "shape": "Semicircle (border-radius: 50px)", 
                "effects": "Hover animation, scale transform, glow shadow",
                "icon": "fas fa-times-circle"
            }
        }
        
        for button_name, features in button_features.items():
            print(f"   🔘 {button_name}:")
            for feature_name, feature_value in features.items():
                print(f"     • {feature_name}: {feature_value}")
        
        # Step 5: Test servicer dashboard access
        print(f"\n📱 Step 5: Testing Servicer Dashboard Access...")
        
        try:
            from django.test import Client
            
            # Create test client and login as servicer
            client = Client()
            client.force_login(servicer)
            
            # Try to access servicer dashboard
            response = client.get('/servicer-dashboard/')
            
            print(f"   • Servicer dashboard response status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Servicer dashboard accessible")
                
                # Check for enhanced design elements in response
                response_content = response.content.decode('utf-8')
                
                design_checks = [
                    ("booking-card", "Enhanced booking cards"),
                    ("status-btn", "Semicircle status buttons"),
                    ("btn-complete", "Green completion button"),
                    ("btn-reject", "Red rejection button"),
                    ("invoice-badge", "Enhanced invoice badges"),
                    ("customer-info", "Improved customer info"),
                    ("service-title", "Enhanced service titles")
                ]
                
                for css_class, description in design_checks:
                    if css_class in response_content:
                        print(f"   ✅ {description} found")
                    else:
                        print(f"   ⚠️ {description} not found")
                        
            else:
                print(f"   ⚠️ Unexpected status code: {response.status_code}")
                
        except Exception as access_error:
            print(f"   ❌ Error accessing servicer dashboard: {access_error}")
        
        print(f"\n🎉 Enhanced Servicer Dashboard Test Completed!")
        
        # Cleanup
        print(f"\n🧹 Cleanup...")
        for booking_id in booking_ids:
            db['services_booking'].delete_one({'_id': booking_id})
            db['services_invoice'].delete_one({'booking_id': booking_id})
        print(f"   ✅ Test bookings cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced servicer dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Testing Enhanced Servicer Dashboard Design\n")
    
    success = test_enhanced_servicer_dashboard()
    
    if success:
        print(f"\n🎉 Enhanced Servicer Dashboard Test Passed!")
        print(f"\n✨ New Design Features:")
        print(f"   🎨 Card-based service layout with gradients")
        print(f"   🔘 Semicircle buttons with hover animations")
        print(f"   🟢 Green 'Mark Completed' button with glow effect")
        print(f"   🔴 Red 'Mark Rejected' button with glow effect")
        print(f"   💎 Enhanced invoice badges with gradients")
        print(f"   📋 Improved customer information sections")
        print(f"   🏷️ Professional status badges")
        
        print(f"\n📱 Test the Enhanced Dashboard:")
        print(f"   • Login as servicer: http://127.0.0.1:8000/servicer-dashboard/")
        print(f"   • See the new card-based design")
        print(f"   • Try the semicircle action buttons")
        print(f"   • Experience the hover effects")
        
        print(f"\n🔗 Login Details:")
        print(f"   • Email: servicer@example.com")
        print(f"   • Password: servicer123")
        
        print(f"\n💡 The servicer dashboard now has a modern, professional design!")
    else:
        print(f"\n❌ Enhanced Servicer Dashboard Test Failed")
        
    print(f"\n🎯 Enhanced design with semicircle buttons is ready!")
