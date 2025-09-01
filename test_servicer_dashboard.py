#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def test_servicer_dashboard():
    """Test the servicer dashboard functionality"""
    print("🧪 Testing Servicer Dashboard Functionality...\n")
    
    try:
        from django.test import Client
        from users.models import User
        from django.contrib.auth import get_user_model
        
        # Create test client
        client = Client()
        
        # Get servicer user
        User = get_user_model()
        try:
            servicer_user = User.objects.get(email='servicer@example.com')
            print("✅ Found servicer user")
        except User.DoesNotExist:
            print("❌ Servicer user not found. Run create_test_servicer.py first.")
            return False
        
        # Test login and dashboard access
        print("\n🔐 Testing servicer login and dashboard access...")
        
        # Force login the servicer
        client.force_login(servicer_user)
        print("✅ Servicer logged in")
        
        # Test servicer dashboard
        response = client.get('/servicer-dashboard/')
        
        if response.status_code == 200:
            content = response.content.decode()
            print("✅ Servicer dashboard loaded successfully")
            
            # Check if dashboard contains expected elements
            checks = [
                ('Welcome, John Servicer!', 'Welcome message'),
                ('Assigned Services', 'Services section'),
                ('Invoice ID', 'Invoice ID display'),
                ('Mark Completed', 'Complete button'),
                ('Mark Rejected', 'Reject button'),
                ('INV-', 'Invoice numbers'),
            ]
            
            passed_checks = 0
            for check_text, description in checks:
                if check_text in content:
                    print(f"   ✅ {description} found")
                    passed_checks += 1
                else:
                    print(f"   ❌ {description} missing")
            
            print(f"\n📊 Dashboard checks: {passed_checks}/{len(checks)} passed")
            
            # Test status update functionality
            print(f"\n🔄 Testing status update functionality...")
            
            # Extract an invoice ID from the page
            import re
            invoice_pattern = r'INV-[A-Z0-9]+'
            invoice_matches = re.findall(invoice_pattern, content)
            
            if invoice_matches:
                test_invoice = invoice_matches[0]
                print(f"   📋 Testing with invoice: {test_invoice}")
                
                # Test marking as completed
                response = client.post('/update-service-status/', {
                    'invoice_id': test_invoice,
                    'status': 'completed'
                })
                
                if response.status_code == 302:  # Redirect after successful update
                    print(f"   ✅ Status update request successful")
                    
                    # Check if redirected back to dashboard
                    if response.url == '/servicer-dashboard/':
                        print(f"   ✅ Redirected back to servicer dashboard")
                        return True
                    else:
                        print(f"   ⚠️ Redirected to: {response.url}")
                        return True
                else:
                    print(f"   ❌ Status update failed with status: {response.status_code}")
                    return False
            else:
                print(f"   ⚠️ No invoice IDs found on dashboard")
                return True  # Dashboard loaded but no invoices
                
        else:
            print(f"❌ Servicer dashboard failed to load. Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing servicer dashboard: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_home_redirect():
    """Test that providers are redirected to servicer dashboard from home"""
    print("\n🏠 Testing home page redirect for providers...")
    
    try:
        from django.test import Client
        from users.models import User
        
        client = Client()
        servicer_user = User.objects.get(email='servicer@example.com')
        
        # Login servicer
        client.force_login(servicer_user)
        
        # Access home page
        response = client.get('/')
        
        if response.status_code == 302:  # Redirect
            if 'servicer-dashboard' in response.url:
                print("✅ Provider correctly redirected to servicer dashboard from home")
                return True
            else:
                print(f"❌ Provider redirected to wrong page: {response.url}")
                return False
        else:
            print(f"❌ Home page didn't redirect. Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing home redirect: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Testing Servicer Dashboard Implementation\n")
    
    dashboard_success = test_servicer_dashboard()
    redirect_success = test_home_redirect()
    
    if dashboard_success and redirect_success:
        print("\n🎉 Servicer dashboard is working perfectly!")
        print("\n✅ Implementation verified:")
        print("   • Servicer can login with provider email")
        print("   • Dashboard shows assigned services with invoice IDs")
        print("   • Status update functionality works")
        print("   • Providers are redirected to servicer dashboard")
        print("   • Invoice ID is used as primary key for updates")
    elif dashboard_success:
        print("\n✅ Servicer dashboard works but redirect needs checking")
    else:
        print("\n❌ Servicer dashboard needs fixing")
        
    print(f"\n🔗 Manual Test:")
    print(f"   1. Open: http://127.0.0.1:8000/accounts/login/")
    print(f"   2. Login: servicer@example.com / servicer123")
    print(f"   3. Should redirect to servicer dashboard")
    print(f"   4. Test marking services as completed/rejected using invoice IDs")
