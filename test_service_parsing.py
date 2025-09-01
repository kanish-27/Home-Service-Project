#!/usr/bin/env python
"""
Test the service information parsing directly
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from services.views import PaymentView

def test_service_parsing():
    """Test the service information parsing methods"""
    
    # Create a PaymentView instance
    view = PaymentView()
    
    # Test different booking notes formats
    test_notes = [
        "Booking for Electrical Installation - Provider: Rajesh Kumar",
        "Booking for Pipe Repair - Provider: Suresh Patel", 
        "Booking for House Cleaning - Provider: Priya Sharma",
        "Booking for AC Repair - Provider: Amit Singh",
        "Booking for Plumbing Service",
        "Some random notes without proper format"
    ]
    
    print("Testing service information parsing...")
    print("=" * 60)
    
    for i, notes in enumerate(test_notes, 1):
        print(f"\n🧪 Test {i}: {notes}")
        print("-" * 40)
        
        # Parse service info
        service_info = view.parse_service_info_from_notes(notes)
        
        # Display results
        for key, value in service_info.items():
            print(f"   {key}: {value}")
    
    # Test the get_service_details_by_name method
    print(f"\n🔍 Testing get_service_details_by_name method:")
    print("-" * 50)
    
    test_service_names = [
        "Electrical Installation",
        "Pipe Repair", 
        "House Cleaning",
        "AC Repair",
        "Non-existent Service"
    ]
    
    for service_name in test_service_names:
        print(f"\n   Service: {service_name}")
        details = view.get_service_details_by_name(service_name)
        if details:
            for key, value in details.items():
                print(f"     {key}: {value}")
        else:
            print(f"     No details found")

if __name__ == '__main__':
    test_service_parsing()
    
    print(f"\n✅ Service parsing test completed!")
    print(f"The payment page should now show detailed service information based on booking notes.")
