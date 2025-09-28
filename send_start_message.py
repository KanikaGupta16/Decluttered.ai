#!/usr/bin/env python3
"""
Send StartCapture message to Camera Agent
Uses uAgents framework to properly communicate with running agents
"""

from uagents import Agent, Context, Model
import asyncio
import time
from typing import Optional

# Message model matching the camera agent
class StartCapture(Model):
    duration_seconds: int = 15
    max_captures: int = 8
    cooldown_seconds: float = 1.5

# Create a temporary sender agent
sender_agent = Agent(
    name="capture_sender",
    seed="capture_sender_seed",
    port=8010,
    endpoint=["http://localhost:8010/submit"]
)

# Camera agent address (you'll need to get this from the camera agent log)
CAMERA_AGENT_ADDRESS = "agent1qg3237z09jekvcdcfpsu9v0882texw7tlcpvz4dra02cjsyh2srkwdf2yya"

@sender_agent.on_event("startup")
async def send_start_capture(ctx: Context):
    """Send StartCapture message to camera agent"""

    print("📤 Sending StartCapture message to Camera Agent...")
    print("🎥 This should trigger the camera capture process")
    print("")

    # Create start capture message
    start_msg = StartCapture(
        duration_seconds=15,
        max_captures=8,
        cooldown_seconds=1.5
    )

    try:
        # Send message to camera agent
        await ctx.send(CAMERA_AGENT_ADDRESS, start_msg)

        print("✅ StartCapture message sent successfully!")
        print("📱 Camera should start capturing in a few seconds...")
        print("🎥 Look for camera window to appear")
        print("")
        print("📋 Monitor progress:")
        print("   📝 Camera logs: tail -f logs/camera_agent.log")
        print("   📁 Captured images: ls captures/")
        print("   🔍 Detection logs: tail -f logs/detection_agent.log")

    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        print("💡 Make sure camera agent is running on port 8001")

if __name__ == "__main__":
    print("📨 Decluttered.ai - Message Sender")
    print("=" * 35)
    print("🎯 Target: Camera Agent")
    print(f"📍 Address: {CAMERA_AGENT_ADDRESS}")
    print("")

    # Run the sender agent briefly to send the message
    try:
        sender_agent.run()
    except KeyboardInterrupt:
        print("\n🛑 Sender stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure no other service is using port 8010")