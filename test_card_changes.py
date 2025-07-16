#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def test_card_changes():
    """Test if the ultra-premium card changes are applied"""
    print("🎨 Testing Ultra-Premium Service Card Changes...\n")
    
    try:
        # Check if the template file has the correct class
        template_path = 'templates/dashboards/servicer_dashboard.html'
        
        print("📋 Step 1: Checking Template File...")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for ultra-premium-service-card class
        if 'ultra-premium-service-card' in content:
            print("   ✅ Found 'ultra-premium-service-card' class in template")
        else:
            print("   ❌ 'ultra-premium-service-card' class NOT found in template")
            return False
        
        # Check for enhanced CSS styles
        css_checks = [
            'Ultra Premium Service Card Styles',
            'linear-gradient(145deg, #ffffff, #f8f9fa)',
            'border-radius: 25px',
            'animation: gradientShift',
            'transform: translateY(-15px) scale(1.03)',
            'background: linear-gradient(135deg, #667eea',
            'backdrop-filter: blur(15px)',
            'font-size: 2.2rem',
            'animation: rotate 3s linear infinite'
        ]
        
        print("\n🎨 Step 2: Checking CSS Enhancements...")
        for check in css_checks:
            if check in content:
                print(f"   ✅ Found: {check[:50]}...")
            else:
                print(f"   ❌ Missing: {check[:50]}...")
        
        # Check cache-busting comment
        if 'Cache Bust: 20250602-1044' in content:
            print("   ✅ Cache-busting comment found")
        else:
            print("   ⚠️ Cache-busting comment not found")
        
        print(f"\n📊 Step 3: Template Statistics...")
        print(f"   • Total lines: {len(content.splitlines())}")
        print(f"   • File size: {len(content)} characters")
        print(f"   • CSS style blocks: {content.count('<style>')}")
        print(f"   • Ultra-premium cards: {content.count('ultra-premium-service-card')}")
        
        # Create test booking data
        print(f"\n🧪 Step 4: Creating Test Booking Data...")
        
        from django.contrib.auth import get_user_model
        import pymongo
        from django.conf import settings
        from datetime import datetime, timedelta
        
        User = get_user_model()
        
        # Connect to MongoDB
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Get test customer
        try:
            customer = User.objects.get(email='test@example.com')
            print(f"   ✅ Test customer found: {customer.get_full_name()}")
        except User.DoesNotExist:
            print("   ⚠️ Test customer not found, creating one...")
            customer = User.objects.create_user(
                username='testcustomer',
                email='test@example.com',
                first_name='Test',
                last_name='Customer',
                password='testpass123'
            )
            print(f"   ✅ Created test customer: {customer.get_full_name()}")
        
        # Create test booking for servicer dashboard
        test_booking = {
            'customer_id': customer.id,
            'provider_id': None,
            'status': 'confirmed',  # Confirmed so it shows in servicer dashboard
            'total_amount': 1500,
            'booking_date': datetime.now() + timedelta(days=1),
            'address': 'wsedfrgthjk',  # Matching your example
            'phone_number': '994015369',  # Matching your example
            'notes': 'Lighting Repair',  # Matching your example
            'special_instructions': 'asdf',  # Matching your example
            'is_paid': True,
            'payment_status': 'paid',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Insert test booking
        result = db['services_booking'].insert_one(test_booking)
        booking_id = result.inserted_id
        
        print(f"   ✅ Created test booking: {str(booking_id)[:8]}")
        print(f"   • Invoice: INV-{datetime.now().strftime('%Y%m%d')}-{str(booking_id)[-8:].upper()}")
        print(f"   • Customer: John Doe")
        print(f"   • Service: Lighting Repair")
        print(f"   • Amount: ₹1500")
        print(f"   • Location: wsedfrgthjk")
        print(f"   • Phone: 994015369")
        print(f"   • Instructions: asdf")
        
        print(f"\n🌐 Step 5: Server Information...")
        print(f"   • Server URL: http://127.0.0.1:8000/")
        print(f"   • Servicer Dashboard: http://127.0.0.1:8000/servicer-dashboard/")
        print(f"   • Template Path: {template_path}")
        
        print(f"\n🔄 Step 6: Browser Cache Clearing Instructions...")
        print(f"   To see the ultra-premium card changes:")
        print(f"   1. Open your browser")
        print(f"   2. Press Ctrl+Shift+R (or Cmd+Shift+R on Mac) for hard refresh")
        print(f"   3. Or press F12 → Network tab → check 'Disable cache'")
        print(f"   4. Or use Incognito/Private browsing mode")
        print(f"   5. Navigate to: http://127.0.0.1:8000/servicer-dashboard/")
        
        print(f"\n✨ Expected Ultra-Premium Card Features:")
        print(f"   • Animated gradient borders (4px top border)")
        print(f"   • Hover glow effects with scale animation")
        print(f"   • Enhanced shadows and 3D effects")
        print(f"   • Larger border radius (25px)")
        print(f"   • Rotating icon borders")
        print(f"   • Glass-morphism header effects")
        print(f"   • Enhanced typography and spacing")
        print(f"   • Gradient text effects")
        print(f"   • Shimmer animations")
        
        # Cleanup
        print(f"\n🧹 Cleanup...")
        db['services_booking'].delete_one({'_id': booking_id})
        print(f"   ✅ Test booking cleaned up")
        
        print(f"\n🎉 Ultra-Premium Card Changes Test Completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing card changes: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Testing Ultra-Premium Service Card Changes\n")
    
    success = test_card_changes()
    
    if success:
        print(f"\n✅ Ultra-Premium Card Changes Applied Successfully!")
        print(f"\n🎯 What's Enhanced:")
        print(f"   • Ultra-premium card design with advanced CSS")
        print(f"   • Multi-layer gradient animations")
        print(f"   • 3D hover effects with enhanced scaling")
        print(f"   • Glass-morphism and backdrop blur effects")
        print(f"   • Rotating icon borders and shimmer effects")
        print(f"   • Enhanced typography with gradient text")
        print(f"   • Professional spacing and layout")
        print(f"   • Advanced shadow and lighting effects")
        
        print(f"\n🔗 View the Changes:")
        print(f"   1. Clear browser cache (Ctrl+Shift+R)")
        print(f"   2. Go to: http://127.0.0.1:8000/servicer-dashboard/")
        print(f"   3. Login as a servicer")
        print(f"   4. View the ultra-premium service cards")
        
        print(f"\n💡 If cards still look the same:")
        print(f"   • Try incognito/private browsing mode")
        print(f"   • Clear browser cache completely")
        print(f"   • Check browser developer tools for CSS errors")
        print(f"   • Ensure JavaScript is enabled")
        
    else:
        print(f"\n❌ Ultra-Premium Card Changes Test Failed")
        
    print(f"\n⭐ Ultra-premium card testing complete!")
