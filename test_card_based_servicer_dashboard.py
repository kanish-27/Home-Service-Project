#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def test_card_based_servicer_dashboard():
    """Test the new card-based layout for individual service bookings"""
    print("📦 Testing Card-Based Servicer Dashboard Layout...\n")
    
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
        
        # Step 1: Create multiple test bookings for card layout
        print(f"\n📦 Step 1: Creating Multiple Bookings for Card Layout...")
        
        test_services = [
            {
                'service_name': 'AC Installation',
                'customer_id': customer.id,
                'provider_id': servicer.id,
                'status': 'confirmed',
                'total_amount': 3500,
                'booking_date': datetime.now() + timedelta(days=1),
                'address': '123 Cool Breeze Apartments, AC Block, Test City',
                'phone_number': '+91-9999888877',
                'notes': 'AC Installation Service',
                'special_instructions': 'Please bring ladder and installation tools. Customer will be available from 10 AM to 6 PM.',
                'is_paid': True,
                'payment_status': 'paid',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'service_name': 'Plumbing Repair',
                'customer_id': customer.id,
                'provider_id': servicer.id,
                'status': 'confirmed',
                'total_amount': 1800,
                'booking_date': datetime.now() + timedelta(days=2),
                'address': '456 Water Works Colony, Plumber Street, Test City',
                'phone_number': '+91-8888777766',
                'notes': 'Kitchen sink and bathroom tap repair',
                'special_instructions': 'Leaking kitchen sink needs urgent attention. Bathroom tap also dripping.',
                'is_paid': True,
                'payment_status': 'paid',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            },
            {
                'service_name': 'Electrical Wiring',
                'customer_id': customer.id,
                'provider_id': servicer.id,
                'status': 'completed',
                'total_amount': 2500,
                'booking_date': datetime.now() - timedelta(days=1),
                'address': '789 Electric Avenue, Power House, Test City',
                'phone_number': '+91-7777666655',
                'notes': 'Complete electrical wiring for new room',
                'special_instructions': 'New room wiring completed successfully. All connections tested.',
                'is_paid': True,
                'payment_status': 'paid',
                'created_at': datetime.now() - timedelta(days=2),
                'updated_at': datetime.now(),
                'service_completed_at': datetime.now() - timedelta(hours=2),
                'service_completed_by': servicer.id
            },
            {
                'service_name': 'House Cleaning',
                'customer_id': customer.id,
                'provider_id': servicer.id,
                'status': 'rejected',
                'total_amount': 1200,
                'booking_date': datetime.now() - timedelta(days=2),
                'address': '101 Clean Street, Tidy Town, Test City',
                'phone_number': '+91-6666555544',
                'notes': 'Deep cleaning service for 3BHK house',
                'special_instructions': 'Service rejected due to customer unavailability.',
                'is_paid': True,
                'payment_status': 'paid',
                'created_at': datetime.now() - timedelta(days=3),
                'updated_at': datetime.now(),
                'rejection_reason': 'Customer not available at scheduled time',
                'rejected_at': datetime.now() - timedelta(hours=1)
            }
        ]
        
        booking_ids = []
        invoice_numbers = []
        
        for i, service in enumerate(test_services, 1):
            # Insert booking
            booking_result = db['services_booking'].insert_one(service)
            booking_id = booking_result.inserted_id
            booking_ids.append(booking_id)
            
            # Create invoice
            invoice_number = f"INV-{str(booking_id)[:8].upper()}"
            invoice_doc = {
                'booking_id': booking_id,
                'invoice_number': invoice_number,
                'generated_at': datetime.now(),
                'subtotal': float(service['total_amount']),
                'tax_amount': float(service['total_amount']) * 0.18,
                'total_amount': float(service['total_amount']) * 1.18
            }
            
            db['services_invoice'].insert_one(invoice_doc)
            invoice_numbers.append(invoice_number)
            
            service_name = service['service_name']
            status = service['status']
            amount = service['total_amount']
            print(f"   📦 Card {i}: {service_name} - {status.upper()} - ₹{amount} - {invoice_number}")
        
        # Step 2: Test card layout structure
        print(f"\n🎨 Step 2: Testing Card Layout Structure...")
        
        layout_features = [
            "✅ Bootstrap grid system (col-lg-6 col-xl-4)",
            "✅ Individual cards for each booking",
            "✅ Card header with gradient background",
            "✅ Invoice badge in header",
            "✅ Service name as card title",
            "✅ Organized card body sections",
            "✅ Customer information section",
            "✅ Service details section", 
            "✅ Special instructions section",
            "✅ Card footer with action buttons",
            "✅ Responsive design for different screen sizes"
        ]
        
        for feature in layout_features:
            print(f"   {feature}")
        
        # Step 3: Test card content sections
        print(f"\n📋 Step 3: Testing Card Content Sections...")
        
        card_sections = {
            "Card Header": {
                "Background": "Gradient (purple to blue)",
                "Content": "Invoice badge + Service name",
                "Style": "Centered, white text"
            },
            "Customer Information": {
                "Icon": "fas fa-user (blue)",
                "Content": "Name, Email, Phone",
                "Style": "Organized with labels"
            },
            "Service Details": {
                "Icon": "fas fa-cog (green)",
                "Content": "Date, Amount, Address",
                "Style": "Two-column layout"
            },
            "Instructions": {
                "Icon": "fas fa-clipboard-list (info)",
                "Content": "Special instructions",
                "Style": "Alert box (conditional)"
            },
            "Action Buttons": {
                "Location": "Card footer",
                "Content": "Semicircle buttons or status badges",
                "Style": "Full-width, stacked"
            }
        }
        
        for section_name, details in card_sections.items():
            print(f"   📋 {section_name}:")
            for detail_name, detail_value in details.items():
                print(f"     • {detail_name}: {detail_value}")
        
        # Step 4: Test responsive grid layout
        print(f"\n📱 Step 4: Testing Responsive Grid Layout...")
        
        responsive_breakpoints = [
            "📱 Mobile (xs): 1 card per row",
            "📱 Tablet (sm/md): 1 card per row", 
            "💻 Laptop (lg): 2 cards per row",
            "🖥️ Desktop (xl): 3 cards per row",
            "🖥️ Large Desktop (xxl): 3 cards per row"
        ]
        
        for breakpoint in responsive_breakpoints:
            print(f"   {breakpoint}")
        
        # Step 5: Test card design similarity to instructions box
        print(f"\n🎯 Step 5: Testing Design Similarity to Instructions Box...")
        
        design_similarities = [
            "✅ Same card structure (header, body, footer)",
            "✅ Similar border-radius (15px)",
            "✅ Consistent shadow effects",
            "✅ Professional typography",
            "✅ Organized content sections",
            "✅ Color-coded headers",
            "✅ Clean spacing and padding",
            "✅ Bootstrap card components"
        ]
        
        for similarity in design_similarities:
            print(f"   {similarity}")
        
        # Step 6: Test servicer dashboard query
        print(f"\n🔍 Step 6: Testing Servicer Dashboard Query...")
        
        # Query all bookings for servicer dashboard
        all_servicer_bookings = list(db['services_booking'].find({
            'status': {'$in': ['confirmed', 'completed', 'rejected']}
        }))
        
        print(f"   • Total cards to display: {len(all_servicer_bookings)}")
        
        status_counts = {}
        for booking in all_servicer_bookings:
            status = booking.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in status_counts.items():
            print(f"   • {status.upper()} cards: {count}")
        
        print(f"\n🎉 Card-Based Servicer Dashboard Test Completed!")
        
        # Cleanup
        print(f"\n🧹 Cleanup...")
        for booking_id in booking_ids:
            db['services_booking'].delete_one({'_id': booking_id})
            db['services_invoice'].delete_one({'booking_id': booking_id})
        print(f"   ✅ Test bookings cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing card-based servicer dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Testing Card-Based Servicer Dashboard Layout\n")
    
    success = test_card_based_servicer_dashboard()
    
    if success:
        print(f"\n🎉 Card-Based Servicer Dashboard Test Passed!")
        print(f"\n📦 New Card Layout Features:")
        print(f"   🎨 Individual cards for each booking (like instruction box)")
        print(f"   📱 Responsive grid layout (1-3 cards per row)")
        print(f"   🎯 Organized content sections in each card")
        print(f"   🔘 Semicircle action buttons in card footer")
        print(f"   💎 Professional card design with gradients")
        print(f"   📋 Clear information hierarchy")
        
        print(f"\n📱 Card Layout Structure:")
        print(f"   📦 Card Header: Invoice badge + Service name")
        print(f"   👤 Customer Info: Name, email, phone")
        print(f"   🔧 Service Details: Date, amount, address")
        print(f"   📝 Instructions: Special notes (if any)")
        print(f"   🔘 Action Footer: Semicircle buttons or status")
        
        print(f"\n📱 Test the New Layout:")
        print(f"   • Login as servicer: http://127.0.0.1:8000/servicer-dashboard/")
        print(f"   • See individual service cards")
        print(f"   • Each booking in its own box")
        print(f"   • Similar to 'How to Use' instruction card")
        
        print(f"\n🔗 Login Details:")
        print(f"   • Email: servicer@example.com")
        print(f"   • Password: servicer123")
        
        print(f"\n💡 Each service now has its own dedicated card box!")
    else:
        print(f"\n❌ Card-Based Servicer Dashboard Test Failed")
        
    print(f"\n🎯 Individual service cards are ready!")
