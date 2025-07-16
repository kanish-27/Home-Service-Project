#!/usr/bin/env python
"""
Test the payment page context directly
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from services.views import PaymentView
from services.models import Booking

def test_payment_context():
    """Test the payment page context with existing booking"""
    User = get_user_model()
    
    # Get test user
    try:
        user = User.objects.get(email='test@example.com')
        print(f"Using user: {user.email}")
    except User.DoesNotExist:
        print("❌ Test user not found")
        return False
    
    # Get the most recent booking for this user
    try:
        booking = Booking.objects.filter(customer=user).order_by('-created_at').first()
        if not booking:
            print("❌ No bookings found for user")
            return False
        
        print(f"✅ Found booking: {booking.id}")
        print(f"   Notes: {booking.notes}")
        print(f"   Provider: {booking.provider.get_full_name() if booking.provider else 'Unknown'}")
        print(f"   Amount: ₹{booking.total_amount}")
        
    except Exception as e:
        print(f"❌ Error finding booking: {e}")
        return False
    
    # Create payment view and test context
    try:
        view = PaymentView()
        view.request = type('Request', (), {'user': user})()  # Mock request
        
        print(f"\n🧪 Testing PaymentView context...")
        context = view.get_context_data(booking_id=str(booking.id))
        
        if context.get('booking'):
            print(f"✅ Booking found in context")
            
            # Test service info parsing
            print(f"\n📋 Parsed Service Information:")
            print(f"   Service Name: {context.get('service_name', 'Not found')}")
            print(f"   Description: {context.get('service_description', 'Not found')}")
            print(f"   Category: {context.get('service_category', 'Not found')}")
            print(f"   Duration: {context.get('service_duration', 'Not found')} hours")
            print(f"   Provider: {context.get('provider_name', 'Not found')}")
            
            # Test pricing
            print(f"\n💰 Pricing Information:")
            print(f"   Subtotal: ₹{context.get('subtotal', 0)}")
            print(f"   Tax (18%): ₹{context.get('tax_amount', 0)}")
            print(f"   Total: ₹{context.get('total_amount', 0)}")
            
            # Test the parsing method directly
            print(f"\n🔍 Testing parse_service_info_from_notes method:")
            service_info = view.parse_service_info_from_notes(booking.notes)
            for key, value in service_info.items():
                print(f"   {key}: {value}")
            
            return True
        else:
            print("❌ Booking not found in context")
            return False
            
    except Exception as e:
        print(f"❌ Error testing payment context: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == '__main__':
    print("Testing payment page context...")
    print("=" * 50)
    
    success = test_payment_context()
    
    if success:
        print(f"\n✅ Payment context test successful!")
        print(f"The payment page should now show detailed service information.")
    else:
        print(f"\n❌ Payment context test failed!")
