#!/usr/bin/env python3
"""
One-time setup script for Decluttered.ai Price APIs
Sets up Google and Facebook login cookies for future automated use
"""

import requests
import time
import os
import subprocess
import sys

def check_api_running(url, service_name):
    """Check if API is running"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name} is running")
            return True
        else:
            print(f"❌ {service_name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {service_name} is not running: {e}")
        return False

def setup_image_recognition():
    """Setup Google login for image recognition"""
    print("\n🖼️ STEP 1: Image Recognition API Setup")
    print("=" * 50)
    
    if not check_api_running("http://localhost:3001/health", "Image Recognition API"):
        print("⚠️ Please start the Image Recognition API first:")
        print("   python main.py")
        return False
    
    print("📷 Image Recognition API uses Google account cookies")
    print("🔄 The first image upload will handle Google login automatically")
    print("✅ No manual setup needed!")
    return True

def setup_facebook_login():
    """Setup Facebook login for marketplace scraping"""
    print("\n🛒 STEP 2: Facebook Login Setup")
    print("=" * 50)
    
    if not check_api_running("http://localhost:3002/health", "Price Scraper API"):
        print("⚠️ Please start the Price Scraper API first:")
        print("   python price_scraper.py")
        return False
    
    # Check if already logged in
    try:
        health_response = requests.get("http://localhost:3002/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            if health_data.get('facebook_logged_in'):
                print("✅ Facebook already logged in!")
                return True
    except:
        pass
    
    print("🔐 Setting up Facebook login for marketplace access...")
    print("⚠️  This is required - Facebook blocks anonymous marketplace browsing")
    
    try:
        # Trigger Facebook login
        response = requests.post("http://localhost:3002/api/facebook/login", timeout=300)  # 5 minute timeout
        input("Press Enter after you have completed Facebook login in the browser...")

        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Facebook login setup complete!")
                print("💾 Cookies saved for future use")
                return True
            else:
                print(f"❌ Facebook login failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Login request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

def test_both_apis():
    """Test both APIs with sample data"""
    print("\n🧪 STEP 3: Testing Complete Pipeline")
    print("=" * 50)
    
    # Test price scraping with known product
    print("🛒 Testing price scraping...")
    
    try:
        price_payload = {
            "name": "Anker Soundcore Liberty 4 NC",
            "platforms": ["facebook", "ebay"]
        }
        
        response = requests.post("http://localhost:3002/api/prices", json=price_payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                data = result['data']
                comps = data.get('comps', [])
                summary = data.get('summary', {})
                
                print(f"✅ Found {len(comps)} comparable listings")
                if summary.get('avg'):
                    print(f"💰 Average price: ${summary['avg']}")
                    print(f"📊 Price range: ${summary.get('min', 'N/A')}-${summary.get('max', 'N/A')}")
                
                platform_counts = summary.get('count_by_platform', {})
                print(f"🛒 By platform: {platform_counts}")
                
                return True
            else:
                print(f"❌ Price scraping failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Price API returned status {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Testing error: {e}")
        return False

def main():
    """Main setup process"""
    print("🚀 Decluttered.ai Price APIs Setup")
    print("This will configure Google and Facebook logins for automated price scraping")
    print("=" * 70)
    
    # Check if both APIs are running
    print("🔍 Checking API status...")
    
    image_api_running = check_api_running("http://localhost:3001/health", "Image Recognition API")
    price_api_running = check_api_running("http://localhost:3002/health", "Price Scraper API")
    
    if not image_api_running or not price_api_running:
        print("\n❌ Setup cannot continue - both APIs must be running")
        print("\nTo start the APIs:")
        print("Terminal 1: python main.py              # Image Recognition (port 3001)")
        print("Terminal 2: python price_scraper.py     # Price Scraping (port 3002)")
        print("\nThen run this setup script again.")
        return False
    
    # Setup steps
    steps_completed = 0
    
    if setup_image_recognition():
        steps_completed += 1
    
    if setup_facebook_login():
        steps_completed += 1
    
    if steps_completed >= 2:
        if test_both_apis():
            steps_completed += 1
    
    # Final summary
    print(f"\n📋 SETUP SUMMARY")
    print("=" * 50)
    print(f"Steps completed: {steps_completed}/3")
    
    if steps_completed == 3:
        print("🎉 SETUP COMPLETE!")
        print("✅ Both APIs are configured and working")
        print("🚀 Ready for production use!")
        
        print("\n📝 Usage:")
        print("1. Upload image → Image Recognition API identifies product")
        print("2. Use product name → Price Scraper API gets market data")
        print("3. Show user suggested listing price")
        
        print("\n💡 Integration tips:")
        print("- Image recognition: ~5-10 seconds")
        print("- Price scraping: ~15-30 seconds") 
        print("- Consider async processing for better UX")
        print("- Cache popular product prices for 24 hours")
        
        return True
    else:
        print("⚠️ Setup incomplete - please resolve the issues above")
        return False

if __name__ == "__main__":
    print("Make sure you have both APIs running before starting setup:")
    print("Terminal 1: python main.py")
    print("Terminal 2: python price_scraper.py")
    print()
    
    input("Press Enter when both APIs are running...")
    
    success = main()
    
    if success:
        print(f"\n🎯 Next steps:")
        print("1. Integrate into your Decluttered.ai workflow")
        print("2. Test with real product images") 
        print("3. Monitor pricing accuracy vs actual sales")
        print("4. Consider adding more platforms (Mercari, OfferUp, etc.)")
    else:
        print(f"\n🔧 Troubleshooting:")
        print("- Check that both APIs started without errors")
        print("- Ensure you have internet connectivity")
        print("- For Facebook issues, try logging in manually in the browser")
        print("- Check the terminal outputs for detailed error messages")