"""
Deploy API-based Agents for Decluttered.ai
Deploys all marketplace API integration agents to Agentverse
"""

import subprocess
import sys
import time
from typing import List, Dict

# List of all API-based agents to deploy
API_AGENTS = [
    {
        "name": "Image Recognition Agent",
        "file": "agents/image_recognition_agent.py",
        "port": 8010,
        "description": "Handles Google reverse image search and product identification"
    },
    {
        "name": "Price Scraper Agent",
        "file": "agents/price_scraper_agent.py",
        "port": 8011,
        "description": "Manages Facebook/eBay marketplace price research"
    },
    {
        "name": "Marketplace Listing Agent",
        "file": "agents/marketplace_listing_agent.py",
        "port": 8012,
        "description": "Creates listings on Facebook Marketplace and eBay"
    },
    {
        "name": "eBay Improved Listing Agent",
        "file": "agents/ebay_improved_listing_agent.py",
        "port": 8013,
        "description": "Advanced eBay listing automation with AI guidance"
    },
    {
        "name": "Facebook Login Agent",
        "file": "agents/facebook_login_agent.py",
        "port": 8014,
        "description": "Coordinates Facebook login across multiple APIs"
    },
    {
        "name": "Pipeline Coordinator Agent",
        "file": "agents/pipeline_coordinator_agent.py",
        "port": 8015,
        "description": "Orchestrates complete pipeline from image to marketplace listing"
    }
]

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")

    required_packages = ["uagents", "requests"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False

    return True

def check_api_servers():
    """Check if external API servers are running."""
    print("\n🌐 Checking external API servers...")

    import requests

    api_servers = [
        {"name": "Image Recognition API", "url": "http://localhost:3001/health"},
        {"name": "Price Scraper API", "url": "http://localhost:3002/health"},
        {"name": "Marketplace Listing API", "url": "http://localhost:3003/health"},
        {"name": "eBay Improved API", "url": "http://localhost:3004/health"}
    ]

    all_healthy = True

    for server in api_servers:
        try:
            response = requests.get(server["url"], timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {server['name']}")
            else:
                print(f"  ⚠️  {server['name']} (HTTP {response.status_code})")
                all_healthy = False
        except Exception as e:
            print(f"  ❌ {server['name']} (Not accessible)")
            all_healthy = False

    if not all_healthy:
        print("\n⚠️  Some API servers are not accessible. Agents will retry connections when they start.")

    return True  # Don't block deployment, just warn

def kill_existing_agents():
    """Kill any existing agent processes on the required ports."""
    print("\n🔄 Checking for existing agent processes...")

    ports = [agent["port"] for agent in API_AGENTS]

    for port in ports:
        try:
            # Check if port is in use
            result = subprocess.run(
                ["lsof", "-t", f"-i:{port}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                print(f"  🔄 Killing processes on port {port}: {', '.join(pids)}")

                for pid in pids:
                    try:
                        subprocess.run(["kill", "-9", pid], timeout=5)
                    except Exception as e:
                        print(f"    ⚠️  Failed to kill PID {pid}: {e}")
            else:
                print(f"  ✅ Port {port} is free")

        except subprocess.TimeoutExpired:
            print(f"  ⚠️  Timeout checking port {port}")
        except Exception as e:
            print(f"  ⚠️  Error checking port {port}: {e}")

def deploy_agent(agent_info: Dict) -> bool:
    """Deploy a single agent."""
    print(f"\n🚀 Deploying {agent_info['name']}...")
    print(f"   File: {agent_info['file']}")
    print(f"   Port: {agent_info['port']}")
    print(f"   Description: {agent_info['description']}")

    try:
        # Start the agent in the background
        process = subprocess.Popen(
            [sys.executable, agent_info['file']],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Give it a moment to start
        time.sleep(2)

        # Check if process is still running
        if process.poll() is None:
            print(f"  ✅ {agent_info['name']} started successfully (PID: {process.pid})")
            return True
        else:
            # Process died, get error output
            stdout, stderr = process.communicate()
            print(f"  ❌ {agent_info['name']} failed to start")
            if stderr:
                print(f"     Error: {stderr}")
            return False

    except Exception as e:
        print(f"  ❌ Failed to deploy {agent_info['name']}: {e}")
        return False

def main():
    """Main deployment function."""
    print("=" * 60)
    print("🚀 DEPLOYING DECLUTTERED.AI API AGENTS")
    print("=" * 60)

    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing packages.")
        return False

    # Check API servers
    check_api_servers()

    # Kill existing agents
    kill_existing_agents()

    # Deploy all agents
    print(f"\n🚀 Deploying {len(API_AGENTS)} API agents...")

    successful_deployments = 0
    failed_deployments = []

    for agent_info in API_AGENTS:
        success = deploy_agent(agent_info)
        if success:
            successful_deployments += 1
        else:
            failed_deployments.append(agent_info['name'])

        # Small delay between deployments
        time.sleep(1)

    # Summary
    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 60)

    print(f"✅ Successful deployments: {successful_deployments}/{len(API_AGENTS)}")

    if failed_deployments:
        print(f"❌ Failed deployments: {len(failed_deployments)}")
        for failed in failed_deployments:
            print(f"   - {failed}")

    if successful_deployments == len(API_AGENTS):
        print("\n🎉 All API agents deployed successfully!")
        print("\n📋 Next steps:")
        print("1. Ensure all external API servers (ports 3001-3004) are running")
        print("2. Test Facebook login on APIs that require it")
        print("3. Send test requests to the Pipeline Coordinator Agent")
        print("\n🔗 Pipeline Flow:")
        print("   Image → Image Recognition → Price Scraper → Marketplace Listing")
        print("   └─────→ eBay Improved (for eBay listings)")

    else:
        print(f"\n⚠️  {len(failed_deployments)} agents failed to deploy.")
        print("Check the error messages above and ensure all dependencies are available.")

    return successful_deployments == len(API_AGENTS)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)