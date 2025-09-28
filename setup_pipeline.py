#!/usr/bin/env python3
"""
Setup Script for Decluttered.AI Object Detection Pipeline
This script sets up the complete environment for the integrated pipeline
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python packages...")
    
    # Essential packages for the pipeline
    essential_packages = [
        "ultralytics",
        "opencv-python", 
        "Pillow",
        "torch",
        "torchvision",
        "supabase",
        "requests",
        "python-dotenv",
        "flask",
        "flask-cors", 
        "selenium",
        "webdriver-manager",
        "google-generativeai"
    ]
    
    for package in essential_packages:
        success = run_command(f"pip install {package}", f"Installing {package}")
        if not success:
            print(f"⚠️ Failed to install {package}, continuing...")
    
    # Try to install from requirements.txt if it exists
    if os.path.exists("requirements.txt"):
        run_command("pip install -r requirements.txt", "Installing from requirements.txt")

def download_yolo_model():
    """Download YOLO model if not present"""
    model_file = "yolov9c.pt"
    if not os.path.exists(model_file):
        print(f"📥 Downloading YOLO model: {model_file}")
        try:
            from ultralytics import YOLO
            # This will automatically download the model
            YOLO("yolov9c.pt")
            print("✅ YOLO model downloaded successfully")
        except Exception as e:
            print(f"⚠️ Could not download YOLO model: {e}")
            print("💡 The model will be downloaded automatically on first run")
    else:
        print(f"✅ YOLO model already present: {model_file}")

def create_directories():
    """Create necessary directories"""
    directories = [
        "cropped_resellables",
        "captures",
        "chrome_profile_google",
        "chrome_profile_scraper", 
        "chrome_profile_lister",
        "chrome_profile_ebay"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

def check_environment():
    """Check environment variables"""
    print("🔧 Checking environment configuration...")
    
    required_env_vars = [
        "GEMINI_API_KEY",
        "SUPABASE_URL", 
        "SUPABASE_ANON_KEY"
    ]
    
    env_file_path = ".env"
    env_template = []
    
    if os.path.exists(env_file_path):
        print(f"✅ Environment file found: {env_file_path}")
        with open(env_file_path, 'r') as f:
            env_content = f.read()
            
        for var in required_env_vars:
            if var not in env_content or f"{var}=your_" in env_content:
                print(f"⚠️ {var} not configured properly")
                env_template.append(f"{var}=your_{var.lower()}_here")
            else:
                print(f"✅ {var} configured")
    else:
        print(f"⚠️ Environment file not found: {env_file_path}")
        env_template = [f"{var}=your_{var.lower()}_here" for var in required_env_vars]
    
    if env_template:
        print(f"\n💡 Create or update {env_file_path} with:")
        for line in env_template:
            print(f"   {line}")

def test_imports():
    """Test critical imports"""
    print("🧪 Testing critical imports...")
    
    test_modules = [
        ("ultralytics", "YOLO model support"),
        ("cv2", "OpenCV for image processing"),
        ("PIL", "Pillow for image manipulation"),
        ("supabase", "Database connectivity"),
        ("selenium", "Web automation"),
        ("google.generativeai", "Gemini AI integration"),
        ("flask", "API server support")
    ]
    
    for module, description in test_modules:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
        except ImportError:
            print(f"❌ {module} - {description} (not available)")

def print_usage_instructions():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE! Here's how to use the pipeline:")
    print("="*60)
    print()
    print("1️⃣ SINGLE IMAGE PROCESSING:")
    print("   python object_detection_pipeline.py")
    print("   - Process a single image through the complete pipeline")
    print("   - Includes: Detection → Recognition → Pricing → Listing")
    print()
    print("2️⃣ LEGACY CAMERA MODE:")
    print("   python OD.py")
    print("   - Uses the original camera capture method")
    print("   - Now calls the new integrated pipeline")
    print()
    print("3️⃣ API SERVERS (run in separate terminals):")
    print("   Terminal 1: cd apps/api && python main.py")
    print("   Terminal 2: cd apps/api && python scraper.py") 
    print("   Terminal 3: cd apps/api && python listing.py")
    print("   Terminal 4: cd apps/api && python ebay_improved.py")
    print()
    print("4️⃣ ENVIRONMENT SETUP:")
    print("   - Update .env file with your API keys")
    print("   - Configure Supabase database credentials")
    print("   - Add Gemini API key for AI features")
    print()
    print("💡 PIPELINE FEATURES:")
    print("   ✅ YOLO v9 object detection")
    print("   ✅ Gemini AI object filtering")
    print("   ✅ Google reverse image search")  
    print("   ✅ Facebook + eBay price scraping")
    print("   ✅ Automated marketplace listing")
    print("   ✅ Supabase database integration")
    print("   ✅ Complete workflow automation")
    print()
    print("🚀 Ready to declutter and sell your items!")

def main():
    """Main setup function"""
    print("🔥 DECLUTTERED.AI - SETUP SCRIPT")
    print("=" * 50)
    print("This script will set up the complete object detection pipeline")
    print("with integrated recognition, pricing, and marketplace listing.")
    print()
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", platform.python_version())
        return
    
    print(f"✅ Python version: {platform.python_version()}")
    print(f"✅ Platform: {platform.system()}")
    print()
    
    # Run setup steps
    install_requirements()
    print()
    
    create_directories()
    print()
    
    download_yolo_model()
    print()
    
    check_environment()
    print()
    
    test_imports()
    print()
    
    print_usage_instructions()

if __name__ == "__main__":
    main()