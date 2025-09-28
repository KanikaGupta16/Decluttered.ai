#!/usr/bin/env python3
"""
Decluttered.ai Agent Deployment Script
Deploys all mailbox agents to run simultaneously
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Agent configurations (excluding camera_agent per user request)
AGENTS = {
    "detection_agent": "agents/detection_agent.py",
    "ai_evaluator_agent": "agents/ai_evaluator_agent.py",
    "image_processor_agent": "agents/image_processor_agent.py",
    "report_coordinator_agent": "agents/report_coordinator_agent.py",
    "web_api_agent": "agents/web_api_agent.py"
}

class AgentDeployer:
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.base_dir = Path(__file__).parent

    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("🔍 Checking dependencies...")

        # Map package names to their import names
        package_imports = {
            'uagents': 'uagents',
            'ultralytics': 'ultralytics',
            'opencv-python': 'cv2',
            'google-generativeai': 'google.generativeai',
            'fastapi': 'fastapi',
            'python-dotenv': 'dotenv'
        }

        missing = []

        for package, import_name in package_imports.items():
            try:
                __import__(import_name)
                print(f"  ✅ {package}")
            except ImportError:
                missing.append(package)
                print(f"  ❌ {package}")

        if missing:
            print(f"\n⚠️  Missing packages: {', '.join(missing)}")
            print("Run: pip install -r requirements.txt")
            return False

        print("✅ All dependencies satisfied\n")
        return True

    def check_environment(self):
        """Check if required environment variables are set"""
        print("🔍 Checking environment variables...")

        required_vars = ['GOOGLE_API_KEY']
        missing = []

        for var in required_vars:
            if os.getenv(var):
                print(f"  ✅ {var}")
            else:
                missing.append(var)
                print(f"  ❌ {var}")

        if missing:
            print(f"\n⚠️  Missing environment variables: {', '.join(missing)}")
            print("Please set them in your .env file")
            return False

        print("✅ Environment configured correctly\n")
        return True

    def start_agent(self, name: str, script_path: str) -> bool:
        """Start a single agent"""
        full_path = self.base_dir / script_path

        if not full_path.exists():
            print(f"❌ Agent script not found: {full_path}")
            return False

        try:
            print(f"🚀 Starting {name}...")
            process = subprocess.Popen(
                [sys.executable, str(full_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.base_dir
            )

            self.processes[name] = process
            time.sleep(2)  # Give agent time to start

            if process.poll() is None:
                print(f"  ✅ {name} started successfully (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"  ❌ {name} failed to start")
                print(f"     Error: {stderr.decode()}")
                return False

        except Exception as e:
            print(f"  ❌ Failed to start {name}: {e}")
            return False

    def stop_all_agents(self):
        """Stop all running agents"""
        print("\n🛑 Stopping all agents...")

        for name, process in self.processes.items():
            try:
                if process.poll() is None:
                    print(f"  Stopping {name}...")
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"  ✅ {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"  ⚠️  Force killing {name}...")
                process.kill()
            except Exception as e:
                print(f"  ❌ Error stopping {name}: {e}")

        self.processes.clear()

    def check_agent_status(self):
        """Check status of all agents"""
        print("\n📊 Agent Status:")

        for name, process in self.processes.items():
            if process.poll() is None:
                print(f"  ✅ {name}: Running (PID: {process.pid})")
            else:
                print(f"  ❌ {name}: Stopped")

    def deploy_all(self):
        """Deploy all agents"""
        print("🚀 Decluttered.ai Agent Deployment")
        print("=" * 50)

        # Pre-deployment checks
        if not self.check_dependencies():
            return False

        if not self.check_environment():
            return False

        # Start agents in order
        print("🚀 Starting agents...")
        success_count = 0

        for name, script_path in AGENTS.items():
            if self.start_agent(name, script_path):
                success_count += 1
            time.sleep(1)  # Stagger startup

        print(f"\n📊 Deployment Summary:")
        print(f"  ✅ Successfully started: {success_count}/{len(AGENTS)} agents")

        if success_count == len(AGENTS):
            print("\n🎉 All agents deployed successfully!")
            print("\n📋 Next Steps:")
            print("1. Agents are now running as mailbox agents")
            print("2. They will automatically connect to Agentverse")
            print("3. Check the Agentverse dashboard for agent registration")
            print("4. Test the system by running: python test_agent_system.py")
            print("\n⚠️  Keep this terminal open to monitor agents")
            print("   Press Ctrl+C to stop all agents")
            return True
        else:
            print(f"\n⚠️  Some agents failed to start. Check logs above.")
            return False

    def monitor_agents(self):
        """Monitor agents and handle shutdown"""
        try:
            while True:
                time.sleep(30)
                # Check if any agents have stopped
                stopped_agents = []
                for name, process in self.processes.items():
                    if process.poll() is not None:
                        stopped_agents.append(name)

                if stopped_agents:
                    print(f"\n⚠️  Agents stopped: {', '.join(stopped_agents)}")
                    self.check_agent_status()

                time.sleep(30)

        except KeyboardInterrupt:
            print("\n\n🛑 Shutdown signal received...")
            self.stop_all_agents()
            print("✅ All agents stopped. Goodbye!")

def main():
    deployer = AgentDeployer()

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        deployer.stop_all_agents()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Deploy agents
    if deployer.deploy_all():
        deployer.monitor_agents()
    else:
        print("\n❌ Deployment failed. Please fix errors and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()