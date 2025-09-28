#!/usr/bin/env python3
"""
Agent Address Discovery Script
Finds and displays addresses of all running Decluttered.ai agents
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import agent configurations
try:
    from agents.detection_agent import detection_agent
    from agents.ai_evaluator_agent import ai_evaluator_agent
    from agents.image_processor_agent import image_processor_agent
    from agents.report_coordinator_agent import report_coordinator_agent
    from agents.web_api_agent import web_api_agent
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

# Agent registry (excluding camera agent per user request)
AGENTS = {
    "Detection Agent": detection_agent,
    "AI Evaluator Agent": ai_evaluator_agent,
    "Image Processor Agent": image_processor_agent,
    "Report Coordinator Agent": report_coordinator_agent,
    "Web API Agent": web_api_agent
}

def get_agent_addresses():
    """Get addresses of all configured agents"""
    print("🔍 Decluttered.ai Agent Addresses")
    print("=" * 50)

    addresses = {}

    for name, agent in AGENTS.items():
        try:
            address = agent.address
            addresses[name] = address
            print(f"📍 {name}:")
            print(f"   Address: {address}")
            print(f"   Short:   {address[:20]}...")
            print()
        except Exception as e:
            print(f"❌ {name}: Error getting address - {e}")
            print()

    return addresses

def generate_address_config(addresses):
    """Generate configuration code for inter-agent communication"""
    print("📋 Configuration Code for Agent Communication:")
    print("=" * 50)

    print("# Add these to your agent files for inter-agent messaging:")
    print()

    for name, address in addresses.items():
        var_name = name.lower().replace(" ", "_").replace("agent", "").strip("_") + "_address"
        print(f'{var_name.upper()} = "{address}"')

    print()
    print("# Example usage in agent code:")
    print("# await ctx.send(DETECTION_ADDRESS, detection_result)")
    print()

def generate_agentverse_config(addresses):
    """Generate Agentverse configuration"""
    print("🌐 Agentverse Configuration:")
    print("=" * 50)

    config = {
        "agents": {}
    }

    for name, address in addresses.items():
        agent_key = name.lower().replace(" ", "_")
        config["agents"][agent_key] = {
            "name": name,
            "address": address,
            "type": "mailbox",
            "status": "active"
        }

    import json
    print(json.dumps(config, indent=2))
    print()

def main():
    print("🚀 Getting agent addresses...")
    print()

    # Get addresses
    addresses = get_agent_addresses()

    if not addresses:
        print("❌ No agent addresses found.")
        print("Make sure agents are properly configured.")
        return

    # Generate configurations
    generate_address_config(addresses)
    generate_agentverse_config(addresses)

    # Save to file
    with open("agent_addresses.json", "w") as f:
        import json
        json.dump(addresses, f, indent=2)

    print("💾 Addresses saved to: agent_addresses.json")
    print()
    print("🎉 Done! Use these addresses for inter-agent communication.")

if __name__ == "__main__":
    main()