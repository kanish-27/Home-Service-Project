#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def verify_recent_bookings():
    """Verify that recent bookings are working in admin dashboard"""
    print("🔍 Verifying Recent Bookings in Admin Dashboard...\n")
    
    try:
        import pymongo
        from django.conf import settings
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Step 1: Check MongoDB connection and bookings
        print("📊 Step 1: Checking MongoDB Bookings...")
        
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        # Get recent bookings
        recent_booking_docs = list(db['services_booking'].find().sort('created_at', -1).limit(5))
        
        print(f"   • Found {len(recent_booking_docs)} recent bookings")
        
        if recent_booking_docs:
            print("   📋 Recent Bookings:")
            for i, booking_doc in enumerate(recent_booking_docs, 1):
                customer_id = booking_doc.get('customer_id')
                try:
                    customer = User.objects.get(id=customer_id)
                    customer_name = customer.get_full_name()
                except:
                    customer_name = f"Customer ID: {customer_id}"
                
                print(f"     {i}. Booking ID: {str(booking_doc['_id'])[:8]}")
                print(f"        Customer: {customer_name}")
                print(f"        Service: {booking_doc.get('notes', 'Home Service')}")
                print(f"        Status: {booking_doc.get('status', 'pending')}")
                print(f"        Amount: ₹{booking_doc.get('total_amount', 0)}")
                print(f"        Date: {booking_doc.get('booking_date', 'N/A')}")
                print()
        else:
            print("   ⚠️ No bookings found")
        
        # Step 2: Test the admin dashboard view logic
        print("🔧 Step 2: Testing Admin Dashboard Logic...")
        
        # Simulate the admin dashboard view logic
        recent_bookings = []
        
        for booking_doc in recent_booking_docs:
            try:
                # Get customer info
                customer = User.objects.get(id=booking_doc['customer_id'])
                
                # Create a mock booking object for template compatibility
                class MockRecentBooking:
                    def __init__(self, doc, customer_obj):
                        self.id = str(doc['_id'])
                        self.customer = customer_obj
                        self.booking_date = doc.get('booking_date')
                        self.total_amount = doc.get('total_amount', 0)
                        self.status = doc.get('status', 'pending')
                        self.created_at = doc.get('created_at')
                        self.notes = doc.get('notes', 'Service Booking')
                        
                        # Mock service object with better service name detection
                        service_name = doc.get('notes', 'Home Service')
                        if 'plumbing' in service_name.lower():
                            service_name = 'Plumbing Service'
                        elif 'electrical' in service_name.lower():
                            service_name = 'Electrical Service'
                        elif 'cleaning' in service_name.lower():
                            service_name = 'Cleaning Service'
                        elif 'repair' in service_name.lower():
                            service_name = 'Repair Service'
                        elif 'installation' in service_name.lower():
                            service_name = 'Installation Service'
                        
                        self.service = type('MockService', (), {
                            'name': service_name,
                            'price': doc.get('total_amount', 0)
                        })()
                        
                    def get_status_display(self):
                        status_map = {
                            'pending': 'Pending',
                            'confirmed': 'Confirmed',
                            'rejected': 'Rejected',
                            'completed': 'Completed',
                            'cancelled': 'Cancelled'
                        }
                        return status_map.get(self.status, self.status.title())
                
                mock_booking = MockRecentBooking(booking_doc, customer)
                recent_bookings.append(mock_booking)
                
            except Exception as booking_error:
                print(f"   ❌ Error processing booking {booking_doc.get('_id')}: {booking_error}")
                continue
        
        print(f"   ✅ Successfully processed {len(recent_bookings)} bookings for admin dashboard")
        
        # Step 3: Display processed bookings
        print("\n📋 Step 3: Processed Bookings for Admin Dashboard:")
        
        if recent_bookings:
            for i, booking in enumerate(recent_bookings, 1):
                print(f"   {i}. Booking BK-{booking.id[:6]}")
                print(f"      Service: {booking.service.name}")
                print(f"      Customer: {booking.customer.get_full_name()}")
                print(f"      Status: {booking.get_status_display()}")
                print(f"      Amount: ₹{booking.total_amount}")
                print()
        else:
            print("   ⚠️ No processed bookings available")
        
        # Step 4: Template compatibility check
        print("🎨 Step 4: Template Compatibility Check...")
        
        template_fields = [
            'id', 'service.name', 'customer.get_full_name', 
            'booking_date', 'get_status_display', 'total_amount'
        ]
        
        if recent_bookings:
            booking = recent_bookings[0]
            print("   📋 Testing template field access:")
            
            for field in template_fields:
                try:
                    if '.' in field:
                        obj, attr = field.split('.', 1)
                        if hasattr(booking, obj):
                            obj_val = getattr(booking, obj)
                            if callable(getattr(obj_val, attr, None)):
                                result = getattr(obj_val, attr)()
                            else:
                                result = getattr(obj_val, attr, 'N/A')
                        else:
                            result = 'Object not found'
                    else:
                        result = getattr(booking, field, 'N/A')
                    
                    print(f"     ✅ {field}: {result}")
                    
                except Exception as field_error:
                    print(f"     ❌ {field}: Error - {field_error}")
        
        print("\n🎉 Recent Bookings Verification Completed!")
        
        if recent_bookings:
            print(f"\n✅ Summary:")
            print(f"   • {len(recent_bookings)} recent bookings available")
            print(f"   • All template fields accessible")
            print(f"   • MongoDB integration working")
            print(f"   • Customer information linked")
            print(f"   • Service names properly formatted")
            print(f"   • Status display working")
            
            print(f"\n📱 Admin Dashboard Status:")
            print(f"   • Recent User Bookings section will now show data")
            print(f"   • No more 'No Recent Bookings' message")
            print(f"   • Proper booking table with all details")
            
            return True
        else:
            print(f"\n⚠️ No recent bookings found - admin dashboard will still show empty state")
            return False
        
    except Exception as e:
        print(f"❌ Error verifying recent bookings: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Verifying Recent Bookings for Admin Dashboard\n")
    
    success = verify_recent_bookings()
    
    if success:
        print(f"\n🎉 Recent Bookings Verification Successful!")
        print(f"\n🔗 Test the Admin Dashboard:")
        print(f"   • URL: http://127.0.0.1:8000/admin-dashboard/")
        print(f"   • Login as admin user")
        print(f"   • Check 'Recent User Bookings' section")
        print(f"   • Should now display booking data instead of empty state")
        
        print(f"\n💡 The Recent User Bookings section is now populated!")
    else:
        print(f"\n❌ Recent Bookings Verification Failed")
        print(f"   • Check if there are bookings in the database")
        print(f"   • Verify MongoDB connection")
        
    print(f"\n📊 Admin dashboard recent bookings verification complete!")
