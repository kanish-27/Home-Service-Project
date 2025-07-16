#!/usr/bin/env python
"""
Debug payment page errors
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from django.contrib.auth import get_user_model
from services.models import Booking
from services.views import PaymentView
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware

def debug_payment_page():
    """Debug payment page issues"""
    User = get_user_model()
    
    print("🔍 Debugging payment page errors...")
    print("=" * 50)
    
    # Check if user exists
    try:
        user = User.objects.get(email='test@example.com')
        print(f"✅ User found: {user.email}")
    except User.DoesNotExist:
        print("❌ Test user not found, creating one...")
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        print(f"✅ Created user: {user.email}")
    
    # Check for bookings
    try:
        bookings = list(Booking.objects.filter(customer=user))
        print(f"✅ Found {len(bookings)} bookings for user")
        
        if bookings:
            for i, booking in enumerate(bookings):
                print(f"   Booking {i+1}: ID={booking.id}, Notes={booking.notes[:50]}...")
        else:
            print("❌ No bookings found")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching bookings: {e}")
        return False
    
    # Test payment view with the first booking
    booking = bookings[0]
    booking_id = str(booking.id) if booking.id else "unknown"
    
    print(f"\n🧪 Testing PaymentView with booking ID: {booking_id}")
    
    try:
        # Create a proper request with middleware
        factory = RequestFactory()
        request = factory.get(f'/services/payment/{booking_id}/')
        request.user = user
        
        # Add session middleware
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        # Add messages middleware
        msg_middleware = MessageMiddleware(lambda x: None)
        msg_middleware.process_request(request)
        
        # Create view and test
        view = PaymentView()
        view.request = request
        
        print("   Testing get_context_data...")
        context = view.get_context_data(booking_id=booking_id)
        
        if context.get('booking'):
            print("   ✅ Booking found in context")
            print(f"   Service Name: {context.get('service_name', 'Not found')}")
            print(f"   Total Amount: ₹{context.get('total_amount', 0)}")
            return True
        else:
            print("   ❌ Booking not found in context")
            return False
            
    except Exception as e:
        print(f"   ❌ Error in PaymentView: {e}")
        import traceback
        print(f"   Full traceback: {traceback.format_exc()}")
        return False

def test_payment_url_patterns():
    """Test if payment URL patterns are working"""
    print(f"\n🔗 Testing URL patterns...")
    
    try:
        from django.urls import reverse
        from services.models import Booking
        
        # Get a booking ID
        booking = Booking.objects.first()
        if booking:
            booking_id = str(booking.id) if booking.id else "test-id"
            
            try:
                payment_url = reverse('services:payment', kwargs={'booking_id': booking_id})
                print(f"   ✅ Payment URL pattern works: {payment_url}")
                return True
            except Exception as url_error:
                print(f"   ❌ URL pattern error: {url_error}")
                return False
        else:
            print("   ❌ No bookings to test URL with")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing URLs: {e}")
        return False

def check_template_exists():
    """Check if payment template exists"""
    print(f"\n📄 Checking payment template...")
    
    import os
    template_path = "homeservice/services/templates/services/payment.html"
    
    if os.path.exists(template_path):
        print(f"   ✅ Payment template exists: {template_path}")
        return True
    else:
        print(f"   ❌ Payment template not found: {template_path}")
        return False

if __name__ == '__main__':
    print("Payment Page Error Debugging")
    print("=" * 50)
    
    # Run all debug checks
    checks = [
        ("Payment View", debug_payment_page),
        ("URL Patterns", test_payment_url_patterns), 
        ("Template", check_template_exists)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name} Check:")
        print("-" * 30)
        result = check_func()
        results.append((check_name, result))
    
    # Summary
    print(f"\n📊 Debug Summary:")
    print("=" * 30)
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
    
    if all(result for _, result in results):
        print(f"\n✅ All checks passed! Payment page should work.")
    else:
        print(f"\n❌ Some checks failed. Please fix the issues above.")
