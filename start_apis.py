#!/usr/bin/env python3
"""
Start All API Servers for Decluttered.AI Pipeline
This script starts all required API servers in separate processes
"""

import os
import sys
import time
import subprocess
import signal
import threading
from pathlib import Path

# API server configurations
API_SERVERS = [
    {
        'name': 'Recognition API',
        'script': 'main.py',
        'port': 3001,
        'description': 'Google reverse image search and product identification'
    },
    {
        'name': 'Scraper API', 
        'script': 'scraper.py',
        'port': 3002,
        'description': 'Facebook Marketplace and eBay price scraping'
    },
    {
        'name': 'Facebook API',
        'script': 'listing.py', 
        'port': 3003,
        'description': 'Facebook Marketplace listing automation'
    },
    {
        'name': 'eBay API',
        'script': 'ebay_improved.py',
        'port': 3004, 
        'description': 'eBay listing automation with AI'
    },
    {
        'name': 'Pipeline API',
        'script': 'pipeline_api.py',
        'port': 3005,
        'description': 'Complete pipeline processing via web API'
    }
]

class APIServerManager:
    def __init__(self):
        self.processes = []
        self.api_dir = Path(__file__).parent / 'apps' / 'api'
        
        if not self.api_dir.exists():
            self.api_dir = Path(__file__).parent / 'api'
        
        if not self.api_dir.exists():
            print("❌ Could not find API directory")
            sys.exit(1)
            
        print(f"[FOLDER] Using API directory: {self.api_dir}")
    
    def start_server(self, server_config):
        """Start a single API server"""
        script_path = self.api_dir / server_config['script']
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return None
        
        try:
            print(f"[ROCKET] Starting {server_config['name']} on port {server_config['port']}...")
            
            # Start the process
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(self.api_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if it's still running
            if process.poll() is None:
                print(f"[OK] {server_config['name']} started successfully (PID: {process.pid})")
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"[ERROR] {server_config['name']} failed to start:")
                if stderr:
                    print(f"   Error: {stderr[:200]}...")
                return None
                
        except Exception as e:
            print(f"❌ Failed to start {server_config['name']}: {e}")
            return None
    
    def start_all_servers(self):
        """Start all API servers"""
        print("[FIRE] DECLUTTERED.AI - API SERVER MANAGER")
        print("=" * 50)
        print("Starting all required API servers...")
        print()
        
        for server_config in API_SERVERS:
            process = self.start_server(server_config)
            if process:
                self.processes.append((server_config, process))
            time.sleep(1)  # Stagger startup
        
        print()
        if self.processes:
            print(f"[OK] Started {len(self.processes)}/{len(API_SERVERS)} API servers successfully")
            print()
            print("[LIST] Running Services:")
            for server_config, process in self.processes:
                print(f"   • {server_config['name']}: http://localhost:{server_config['port']}")
                print(f"     {server_config['description']}")
            
            print()
            print("[GLOBE] Frontend Integration:")
            print("   • Next.js frontend should connect to these APIs automatically")
            print("   • Pipeline page: http://localhost:3000/pipeline")
            print("   • Upload an image to start the complete workflow")
            print()
            print("[CHART] Health Check URLs:")
            for server_config, _ in self.processes:
                print(f"   • {server_config['name']}: http://localhost:{server_config['port']}/health")
            
            print()
            print("[STOP] To stop all servers, press Ctrl+C")
            
        else:
            print("[ERROR] No servers started successfully")
            return False
        
        return True
    
    def stop_all_servers(self):
        """Stop all running servers"""
        print("\n[STOP] Stopping all API servers...")
        
        for server_config, process in self.processes:
            try:
                print(f"⏹️ Stopping {server_config['name']}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                    print(f"✅ {server_config['name']} stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    print(f"⚡ Force killing {server_config['name']}...")
                    process.kill()
                    process.wait()
                    
            except Exception as e:
                print(f"⚠️ Error stopping {server_config['name']}: {e}")
        
        print("✅ All servers stopped")
    
    def monitor_servers(self):
        """Monitor server health"""
        while True:
            try:
                time.sleep(10)  # Check every 10 seconds
                
                # Check if any processes have died
                dead_servers = []
                for server_config, process in self.processes:
                    if process.poll() is not None:
                        dead_servers.append((server_config, process))
                
                if dead_servers:
                    print(f"\n⚠️ Detected {len(dead_servers)} dead server(s):")
                    for server_config, process in dead_servers:
                        print(f"   ❌ {server_config['name']} (port {server_config['port']}) has stopped")
                        self.processes.remove((server_config, process))
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"⚠️ Monitoring error: {e}")
    
    def run(self):
        """Main run method"""
        try:
            # Setup signal handling
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Start all servers
            if not self.start_all_servers():
                return 1
            
            # Start monitoring in background
            monitor_thread = threading.Thread(target=self.monitor_servers, daemon=True)
            monitor_thread.start()
            
            # Keep main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
            return 0
            
        except Exception as e:
            print(f"❌ Server manager error: {e}")
            return 1
        finally:
            self.stop_all_servers()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n📡 Received signal {signum}, shutting down...")
        self.stop_all_servers()
        sys.exit(0)

def check_python_version():
    """Check if Python version is adequate"""
    if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'flask': 'flask',
        'flask_cors': 'flask_cors', 
        'ultralytics': 'ultralytics',
        'opencv-python': 'cv2',
        'selenium': 'selenium',
        'requests': 'requests'
    }
    
    missing_packages = []
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install " + ' '.join(missing_packages))
        return False
    
    return True

def main():
    """Main entry point"""
    print("🔥 DECLUTTERED.AI - API SERVER STARTUP")
    print("=" * 50)
    
    # Pre-flight checks
    if not check_python_version():
        return 1
    
    if not check_dependencies():
        return 1
    
    # Create and run server manager
    manager = APIServerManager()
    return manager.run()

if __name__ == '__main__':
    sys.exit(main())