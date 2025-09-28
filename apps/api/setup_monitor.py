#!/usr/bin/env python3
"""
Install and setup script for Facebook Message Monitor
"""
import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"[OK] Installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"[ERROR] Failed to install {package}")
        return False

def check_package(package):
    """Check if a package is installed"""
    try:
        __import__(package)
        print(f"[OK] {package} is available")
        return True
    except ImportError:
        print(f"[WARNING] {package} not found")
        return False

def setup_facebook_monitor():
    """Setup Facebook Message Monitor"""
    print("[ROCKET] Setting up Facebook Message Monitor")
    print("=" * 50)
    
    # Check required packages
    required_packages = [
        ("selenium", "selenium"),
        ("flask", "flask"),
        ("flask_cors", "flask-cors"),
        ("webdriver_manager", "webdriver-manager"),
        ("python-dotenv", "python-dotenv")
    ]
    
    optional_packages = [
        ("agentmail", "agentmail")
    ]
    
    print("[PACKAGE] Checking required packages...")
    missing_required = []
    for module_name, pip_name in required_packages:
        if not check_package(module_name):
            missing_required.append(pip_name)
    
    if missing_required:
        print(f"\n📥 Installing missing packages: {', '.join(missing_required)}")
        for package in missing_required:
            install_package(package)
    
    print("\n[PACKAGE] Checking optional packages...")
    for module_name, pip_name in optional_packages:
        if not check_package(module_name):
            print(f"[BULB] Optional: Install {pip_name} for email forwarding")
            print(f"   pip install {pip_name}")
    
    # Check Chrome driver
    print("\n[GLOBE] Checking Chrome WebDriver...")
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        ChromeDriverManager().install()
        print("[OK] Chrome WebDriver ready")
    except Exception as e:
        print(f"[WARNING] Chrome WebDriver setup issue: {e}")
    
    # Check environment file
    print("\n⚙️ Checking configuration...")
    if os.path.exists('.env'):
        print("[OK] .env file found")
        with open('.env', 'r') as f:
            content = f.read()
            if 'AGENTMAIL_API_KEY' in content:
                print("[OK] AgentMail API key configured")
            else:
                print("[BULB] Add AGENTMAIL_API_KEY to .env for email forwarding")
    else:
        print("[WARNING] .env file not found - create one with your API keys")
    
    print("\n[TARGET] Setup Summary:")
    print("  [OK] Facebook Message Monitor ready")
    print("  [ROCKET] Run: python production_test.py")
    print("  [LIGHTNING] Quick test: python production_test.py --quick")
    print("  [GLOBE] API endpoint: POST /api/facebook/start-realtime-monitor")
    
    print("\n📋 Next steps:")
    print("  1. Make sure you're logged into Facebook")
    print("  2. Run the production test to verify everything works")
    print("  3. Set your AgentMail API key for email forwarding")
    print("  4. Deploy and monitor real-time Facebook messages!")

if __name__ == "__main__":
    setup_facebook_monitor()