#!/usr/bin/env python
"""
Clean up duplicate categories in the database
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

from services.models import ServiceCategory, Service
from collections import defaultdict

def cleanup_duplicate_categories():
    """Remove duplicate categories and keep only one of each"""
    print("Cleaning up duplicate categories...")
    
    # Group categories by slug
    categories_by_slug = defaultdict(list)
    for category in ServiceCategory.objects.all():
        categories_by_slug[category.slug].append(category)
    
    duplicates_found = 0
    duplicates_removed = 0
    
    for slug, categories in categories_by_slug.items():
        if len(categories) > 1:
            duplicates_found += 1
            print(f"\nFound {len(categories)} categories with slug '{slug}':")
            
            # Keep the first one, delete the rest
            keep_category = categories[0]
            duplicate_categories = categories[1:]
            
            print(f"  Keeping: {keep_category.name} (ID: {keep_category.pk})")
            
            for dup_cat in duplicate_categories:
                print(f"  Removing: {dup_cat.name} (ID: {dup_cat.pk})")
                
                # Move any services from duplicate category to the kept category
                services_moved = Service.objects.filter(category=dup_cat).update(category=keep_category)
                if services_moved > 0:
                    print(f"    Moved {services_moved} services to kept category")
                
                # Delete the duplicate category
                dup_cat.delete()
                duplicates_removed += 1
    
    print(f"\nCleanup complete:")
    print(f"  Duplicate category groups found: {duplicates_found}")
    print(f"  Duplicate categories removed: {duplicates_removed}")
    
    # Show final category count
    final_count = ServiceCategory.objects.count()
    print(f"  Final category count: {final_count}")

def show_current_categories():
    """Show all current categories"""
    print("\nCurrent categories in database:")
    categories = ServiceCategory.objects.all().order_by('slug')
    
    for category in categories:
        service_count = Service.objects.filter(category=category).count()
        print(f"  {category.slug}: {category.name} ({service_count} services)")

if __name__ == '__main__':
    print("Database cleanup utility")
    print("=" * 40)
    
    show_current_categories()
    cleanup_duplicate_categories()
    show_current_categories()
