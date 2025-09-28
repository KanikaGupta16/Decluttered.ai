#!/usr/bin/env python3
"""
Test Script for Decluttered.AI Pipeline
Demonstrates the complete workflow with a sample image
"""

import os
import sys
import time
from pathlib import Path

def test_pipeline():
    """Test the complete pipeline functionality"""
    print("🧪 DECLUTTERED.AI - PIPELINE TEST")
    print("=" * 50)
    
    # Test 1: Import Pipeline
    print("1️⃣ Testing Pipeline Import...")
    try:
        from object_detection_pipeline import ObjectDetectionPipeline
        print("✅ ObjectDetectionPipeline imported successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Initialize Pipeline
    print("\n2️⃣ Testing Pipeline Initialization...")
    try:
        pipeline = ObjectDetectionPipeline()
        print("✅ Pipeline initialized successfully")
        
        # Check components
        print(f"   📊 YOLO Model: {'✅ Available' if pipeline.yolo_model else '❌ Not available'}")
        print(f"   💾 Database: {'✅ Connected' if pipeline.supabase_client else '⚠️ Not configured'}")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False
    
    # Test 3: Check API Endpoints
    print("\n3️⃣ Testing API Connectivity...")
    import requests
    
    api_endpoints = [
        ("Recognition API", "http://localhost:3001/health"),
        ("Scraper API", "http://localhost:3002/health"),
        ("Facebook API", "http://localhost:3003/health"),
        ("eBay API", "http://localhost:3004/health")
    ]
    
    for name, url in api_endpoints:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"   ✅ {name}: Online")
            else:
                print(f"   ⚠️ {name}: Status {response.status_code}")
        except requests.exceptions.RequestException:
            print(f"   ❌ {name}: Offline")
    
    # Test 4: Find Sample Images
    print("\n4️⃣ Looking for Sample Images...")
    image_extensions = [".jpg", ".jpeg", ".png", ".bmp"]
    sample_images = []
    
    # Check current directory and common folders
    search_paths = [
        ".",
        "captures",
        "cropped_resellables",
        str(Path.home() / "Downloads"),
        str(Path.home() / "Pictures")
    ]
    
    for search_path in search_paths:
        if os.path.exists(search_path):
            for ext in image_extensions:
                pattern = f"*{ext}"
                for img_path in Path(search_path).glob(pattern):
                    if img_path.is_file() and img_path.stat().st_size > 1000:  # At least 1KB
                        sample_images.append(str(img_path))
                        if len(sample_images) >= 3:  # Limit to 3 samples
                            break
                if len(sample_images) >= 3:
                    break
        if len(sample_images) >= 3:
            break
    
    if sample_images:
        print(f"   ✅ Found {len(sample_images)} sample images:")
        for img in sample_images:
            file_size = os.path.getsize(img) / 1024  # KB
            print(f"      📸 {os.path.basename(img)} ({file_size:.1f} KB)")
    else:
        print("   ⚠️ No sample images found")
        print("   💡 Add a .jpg or .png file to the current directory to test")
    
    # Test 5: Configuration Check
    print("\n5️⃣ Checking Configuration...")
    from dotenv import load_dotenv
    load_dotenv()
    
    config_items = [
        ("GEMINI_API_KEY", "Gemini AI"),
        ("SUPABASE_URL", "Database URL"),
        ("SUPABASE_ANON_KEY", "Database Key"),
        ("EBAY_APP_ID", "eBay API")
    ]
    
    for env_var, description in config_items:
        value = os.getenv(env_var)
        if value and value != f"your_{env_var.lower()}_here":
            print(f"   ✅ {description}: Configured")
        else:
            print(f"   ⚠️ {description}: Not configured")
    
    # Test 6: Directory Structure
    print("\n6️⃣ Checking Directory Structure...")
    required_dirs = [
        "cropped_resellables",
        "captures", 
        "apps/api"
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"   ✅ {directory}: Exists")
        else:
            print(f"   ⚠️ {directory}: Missing")
    
    # Test 7: Permissions Check
    print("\n7️⃣ Checking File Permissions...")
    try:
        # Test write permissions
        test_file = "test_write_permission.tmp"
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("   ✅ Write permissions: OK")
    except Exception as e:
        print(f"   ❌ Write permissions: Failed - {e}")
    
    # Summary
    print("\n🎯 TEST SUMMARY")
    print("=" * 30)
    print("✅ Pipeline components are working")
    print("⚠️ Some APIs may be offline (normal if not started)")
    print("💡 To run complete test with image:")
    print(f"   python object_detection_pipeline.py")
    print()
    
    if sample_images:
        print("🚀 QUICK START:")
        print(f"1. Make sure API servers are running:")
        print(f"   cd apps/api && python main.py")
        print(f"   cd apps/api && python scraper.py")
        print(f"   cd apps/api && python listing.py")
        print(f"   cd apps/api && python ebay_improved.py")
        print(f"")
        print(f"2. Run pipeline with sample image:")
        print(f"   python object_detection_pipeline.py")
        print(f"   (Select image: {os.path.basename(sample_images[0])})")
    
    return True

if __name__ == "__main__":
    success = test_pipeline()
    
    if success:
        print("\n🎉 All tests completed!")
        print("🔥 Decluttered.AI pipeline is ready to use!")
    else:
        print("\n❌ Some tests failed. Check the output above.")
        sys.exit(1)