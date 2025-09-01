#!/usr/bin/env python
"""
Script to test all pages in the Django homeservice application
"""
import os
import sys
import django
import requests
from urllib.parse import urljoin

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

class PageTester:
    def __init__(self):
        self.client = Client()
        self.base_url = 'http://127.0.0.1:8000'
        self.results = []
        
    def test_url(self, url, name, requires_auth=False, method='GET'):
        """Test a single URL"""
        try:
            full_url = urljoin(self.base_url, url)
            response = requests.get(full_url, timeout=10)
            
            status = response.status_code
            if status == 200:
                result = "✅ PASS"
            elif status == 302 and requires_auth:
                result = "🔒 REDIRECT (Auth Required)"
            elif status == 404:
                result = "❌ NOT FOUND"
            elif status == 500:
                result = "💥 SERVER ERROR"
            else:
                result = f"⚠️  STATUS {status}"
                
            self.results.append({
                'name': name,
                'url': url,
                'status': status,
                'result': result
            })
            
            print(f"{result:<25} {name:<30} {url}")
            
        except requests.exceptions.RequestException as e:
            result = f"❌ CONNECTION ERROR: {str(e)}"
            self.results.append({
                'name': name,
                'url': url,
                'status': 'ERROR',
                'result': result
            })
            print(f"{result:<25} {name:<30} {url}")
    
    def run_tests(self):
        """Run all page tests"""
        print("=" * 80)
        print("TESTING ALL PAGES IN HOMESERVICE APPLICATION")
        print("=" * 80)
        print(f"{'RESULT':<25} {'PAGE NAME':<30} {'URL'}")
        print("-" * 80)
        
        # Public pages
        self.test_url('/', 'Home Page')
        self.test_url('/admin/', 'Admin Login')
        
        # Authentication pages (allauth)
        self.test_url('/accounts/login/', 'Login Page')
        self.test_url('/accounts/signup/', 'Signup Page')
        self.test_url('/accounts/logout/', 'Logout Page')
        
        # Services pages
        self.test_url('/services/', 'Service Categories')
        self.test_url('/services/list/', 'Service List')
        self.test_url('/services/check-mongodb/', 'MongoDB Check')
        self.test_url('/services/mongodb-status/', 'MongoDB Status')
        
        # Provider signup
        self.test_url('/signup/provider/', 'Provider Signup')
        
        # Password reset pages
        self.test_url('/password_reset/', 'Password Reset')
        
        # Protected pages (require authentication)
        print("\n" + "=" * 80)
        print("PROTECTED PAGES (REQUIRE AUTHENTICATION)")
        print("=" * 80)
        
        # User profile pages
        self.test_url('/profile/', 'User Profile', requires_auth=True)
        self.test_url('/profile/edit/', 'Edit Profile', requires_auth=True)
        self.test_url('/profile/change-password/', 'Change Password', requires_auth=True)
        self.test_url('/profile/addresses/', 'Address List', requires_auth=True)
        self.test_url('/profile/addresses/add/', 'Add Address', requires_auth=True)
        self.test_url('/profile/notifications/', 'Notifications', requires_auth=True)
        
        # Provider dashboard pages
        self.test_url('/dashboard/', 'Provider Dashboard', requires_auth=True)
        self.test_url('/dashboard/services/', 'Provider Services', requires_auth=True)
        self.test_url('/dashboard/services/add/', 'Add Service', requires_auth=True)
        self.test_url('/dashboard/bookings/', 'Provider Bookings', requires_auth=True)
        self.test_url('/dashboard/schedule/', 'Provider Schedule', requires_auth=True)
        self.test_url('/dashboard/reviews/', 'Provider Reviews', requires_auth=True)
        self.test_url('/dashboard/profile/', 'Provider Profile', requires_auth=True)
        self.test_url('/dashboard/profile/edit/', 'Edit Provider Profile', requires_auth=True)
        
        # Service-related protected pages
        self.test_url('/services/provider/dashboard/', 'Service Provider Dashboard', requires_auth=True)
        self.test_url('/services/provider/services/', 'Provider Service List', requires_auth=True)
        self.test_url('/services/provider/service/add/', 'Add Service (Services)', requires_auth=True)
        self.test_url('/services/bookings/', 'Booking List', requires_auth=True)
        
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total = len(self.results)
        passed = len([r for r in self.results if '✅' in r['result']])
        redirects = len([r for r in self.results if '🔒' in r['result']])
        errors = len([r for r in self.results if '❌' in r['result'] or '💥' in r['result']])
        
        print(f"Total pages tested: {total}")
        print(f"✅ Passed: {passed}")
        print(f"🔒 Auth redirects: {redirects}")
        print(f"❌ Errors: {errors}")
        
        if errors > 0:
            print("\n⚠️  PAGES WITH ERRORS:")
            for result in self.results:
                if '❌' in result['result'] or '💥' in result['result']:
                    print(f"  - {result['name']}: {result['result']}")

if __name__ == '__main__':
    tester = PageTester()
    tester.run_tests()
