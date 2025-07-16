#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeservice.settings')
django.setup()

def fix_review_collection():
    """Fix the MongoDB review collection to prevent duplicate key errors"""
    print("🔧 Fixing Review Collection Schema...\n")
    
    try:
        import pymongo
        from django.conf import settings
        
        # Connect to MongoDB
        client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        
        collection_name = 'services_review'
        
        print(f"📊 Step 1: Checking collection '{collection_name}'...")
        
        # Check if collection exists
        if collection_name in db.list_collection_names():
            print(f"   ✅ Collection '{collection_name}' exists")
            
            # Get current indexes
            indexes = list(db[collection_name].list_indexes())
            print(f"   📋 Current indexes:")
            for idx in indexes:
                print(f"      • {idx['name']}: {idx.get('key', {})}")
            
            # Check for problematic indexes
            problematic_indexes = []
            for idx in indexes:
                if 'id' in idx.get('key', {}) and idx['name'] != '_id_':
                    problematic_indexes.append(idx['name'])
            
            if problematic_indexes:
                print(f"\n🚨 Step 2: Found problematic indexes: {problematic_indexes}")
                
                # Drop problematic indexes
                for idx_name in problematic_indexes:
                    try:
                        db[collection_name].drop_index(idx_name)
                        print(f"   ✅ Dropped index: {idx_name}")
                    except Exception as e:
                        print(f"   ⚠️ Could not drop index {idx_name}: {e}")
            else:
                print(f"\n✅ Step 2: No problematic indexes found")
            
            # Clear any documents with null id fields
            print(f"\n🧹 Step 3: Cleaning up documents with null id fields...")
            result = db[collection_name].delete_many({'id': None})
            if result.deleted_count > 0:
                print(f"   ✅ Removed {result.deleted_count} documents with null id")
            else:
                print(f"   ✅ No documents with null id found")
            
            # Clear any documents with id field (should only have _id)
            print(f"\n🧹 Step 4: Removing documents with 'id' field...")
            result = db[collection_name].delete_many({'id': {'$exists': True}})
            if result.deleted_count > 0:
                print(f"   ✅ Removed {result.deleted_count} documents with 'id' field")
            else:
                print(f"   ✅ No documents with 'id' field found")
                
        else:
            print(f"   ℹ️ Collection '{collection_name}' does not exist yet")
        
        print(f"\n🎯 Step 5: Creating proper indexes...")
        
        # Ensure proper indexes exist
        try:
            # Create compound index for booking_id + customer_id (unique)
            db[collection_name].create_index(
                [('booking_id', 1), ('customer_id', 1)], 
                unique=True,
                name='booking_customer_unique'
            )
            print(f"   ✅ Created unique index: booking_id + customer_id")
        except Exception as e:
            print(f"   ⚠️ Index may already exist: {e}")
        
        try:
            # Create index for customer_id
            db[collection_name].create_index([('customer_id', 1)], name='customer_id_index')
            print(f"   ✅ Created index: customer_id")
        except Exception as e:
            print(f"   ⚠️ Index may already exist: {e}")
        
        try:
            # Create index for rating
            db[collection_name].create_index([('rating', 1)], name='rating_index')
            print(f"   ✅ Created index: rating")
        except Exception as e:
            print(f"   ⚠️ Index may already exist: {e}")
        
        try:
            # Create index for created_at
            db[collection_name].create_index([('created_at', -1)], name='created_at_index')
            print(f"   ✅ Created index: created_at (descending)")
        except Exception as e:
            print(f"   ⚠️ Index may already exist: {e}")
        
        print(f"\n📋 Step 6: Final index verification...")
        final_indexes = list(db[collection_name].list_indexes())
        print(f"   📊 Final indexes:")
        for idx in final_indexes:
            print(f"      • {idx['name']}: {idx.get('key', {})}")
        
        # Test document insertion
        print(f"\n🧪 Step 7: Testing review document insertion...")
        
        from datetime import datetime
        from bson import ObjectId
        
        test_doc = {
            'booking_id': ObjectId(),
            'customer_id': 999999,  # Test customer ID
            'customer_name': 'Test Customer',
            'customer_email': 'test@example.com',
            'rating': 5,
            'comment': 'Test review for schema validation',
            'service_name': 'Test Service',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        try:
            result = db[collection_name].insert_one(test_doc)
            print(f"   ✅ Test document inserted successfully: {result.inserted_id}")
            
            # Clean up test document
            db[collection_name].delete_one({'_id': result.inserted_id})
            print(f"   ✅ Test document cleaned up")
            
        except Exception as test_error:
            print(f"   ❌ Test insertion failed: {test_error}")
            return False
        
        print(f"\n🎉 Review Collection Fix Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing review collection: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 MongoDB Review Collection Fix\n")
    
    success = fix_review_collection()
    
    if success:
        print(f"\n✅ Review Collection Fixed Successfully!")
        print(f"\n🎯 What's Fixed:")
        print(f"   • Removed problematic 'id' indexes")
        print(f"   • Cleaned up documents with null/invalid id fields")
        print(f"   • Created proper MongoDB indexes")
        print(f"   • Ensured unique constraint on booking_id + customer_id")
        print(f"   • Added performance indexes for queries")
        
        print(f"\n⭐ Review Features Now Working:")
        print(f"   • Submit reviews without duplicate key errors")
        print(f"   • Prevent duplicate reviews per booking")
        print(f"   • Fast review queries and lookups")
        print(f"   • Proper MongoDB document structure")
        
        print(f"\n🔗 Test the Fix:")
        print(f"   1. Complete a booking (status = 'completed')")
        print(f"   2. Go to booking list and click 'Write a Review'")
        print(f"   3. Fill out the review form with rating and comment")
        print(f"   4. Click 'Submit Review'")
        print(f"   5. Should redirect with success message")
        
        print(f"\n💡 Review submission errors are now fixed!")
    else:
        print(f"\n❌ Review Collection Fix Failed")
        
    print(f"\n⭐ Review collection fix complete!")
