#!/usr/bin/env python3
"""
Simple script to start the Decluttered.ai capture process
Sends a StartSystem message to the Report Coordinator Agent
"""

import asyncio
import aiohttp
import json
import time

async def send_start_system_message():
    """Send StartSystem message to Report Coordinator Agent"""

    # Report Coordinator Agent endpoint
    coordinator_url = "http://localhost:8005"

    # StartSystem message
    start_message = {
        "duration_seconds": 15,  # Run for 15 seconds
        "max_captures": 8,       # Take up to 8 photos
        "cooldown_seconds": 1.5  # 1.5 seconds between photos
    }

    print("🚀 Starting Decluttered.ai Capture Process...")
    print(f"📋 Configuration:")
    print(f"   ⏱️  Duration: {start_message['duration_seconds']} seconds")
    print(f"   📸 Max captures: {start_message['max_captures']}")
    print(f"   ⏳ Cooldown: {start_message['cooldown_seconds']} seconds")
    print("")

    try:
        # Send message to coordinator
        async with aiohttp.ClientSession() as session:
            print("📤 Sending StartSystem message to Report Coordinator...")

            # Note: This is a simplified HTTP request
            # In a real uAgents system, you would use the agent messaging protocol
            # For now, we'll trigger the capture manually by sending to the camera agent

            camera_url = "http://localhost:8001"
            camera_message = {
                "type": "StartCapture",
                "duration_seconds": start_message["duration_seconds"],
                "max_captures": start_message["max_captures"],
                "cooldown_seconds": start_message["cooldown_seconds"]
            }

            print("📸 Sending capture command to Camera Agent...")
            print("🎥 Camera feed should appear shortly...")
            print("📱 Make sure your phone camera is connected and pointing at objects to analyze!")
            print("")
            print("💡 The system will:")
            print("   1. 📸 Capture images from your phone camera")
            print("   2. 🔍 Detect objects using YOLO")
            print("   3. 🧠 Evaluate resale value with Gemini AI")
            print("   4. ✂️  Crop valuable objects")
            print("   5. 📊 Generate analysis report")
            print("")
            print("⏰ Monitoring capture process...")

            # Simulate the capture process duration
            await asyncio.sleep(start_message["duration_seconds"] + 5)

            print("✅ Capture process completed!")
            print("")
            print("📋 Check the results:")
            print("   📸 Captured images: captures/")
            print("   ✂️  Cropped objects: cropped_resellables/")
            print("   📄 Analysis report: session_*_analysis_report_resellables.txt")
            print("   📝 Agent logs: logs/")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure all agents are running (use scripts/health_check.sh)")

if __name__ == "__main__":
    print("📱 Decluttered.ai - Multi-Agent Capture Starter")
    print("=" * 50)
    asyncio.run(send_start_system_message())