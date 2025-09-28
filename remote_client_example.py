"""
Remote Client to Use Decluttered.ai Agents
Your friend can use this code to interact with your deployed agents from anywhere
"""

import base64
import time
import uuid
from uagents import Agent, Context, Model
from typing import Dict, List, Optional, Any

# Copy your message models (your friend will need these)
class CapturedImage(Model):
    filename: str
    timestamp: int
    file_path: str
    capture_index: int
    session_id: str

class DetectionResult(Model):
    image_path: str
    timestamp: int
    session_id: str
    detected_objects: Dict[str, str]
    unique_classes: List[str]
    detection_count: int
    largest_instances: Dict[str, str]

class EvaluationResult(Model):
    image_path: str
    timestamp: int
    session_id: str
    original_objects: List[str]
    resellable_items: List[str]
    evaluation_confidence: str
    gemini_raw_response: str
    filtered_detections: Dict[str, str]

class ProcessingResult(Model):
    original_image_path: str
    timestamp: int
    session_id: str
    resellable_objects: List[str]
    cropped_files: List[str]
    processing_summary: Dict[str, Any]
    total_objects_processed: int

# Your deployed agent addresses (replace with actual addresses from your deployment)
DETECTION_AGENT_ADDRESS = "agent1qte25te5k79ygajeapzelgyle8ape8pvzdxdw9zndp4kph53qeq5unc8n6j"
AI_EVALUATOR_ADDRESS = "agent1q0vgqkwxlz7lfve6tqyse6z7m3zccv4uv7kt484jlc77dutxngzy62ea92p"
IMAGE_PROCESSOR_ADDRESS = "agent1qwgxuc8z9nsafsl30creg2hhykclaw4pnwm7ge9e5l3qakrx4r6nu67p2au"
REPORT_COORDINATOR_ADDRESS = "agent1qvf8rwqhnuj85w9fl7kap6uszlk00gpjed0pq6vh289thwqys0zeq9w9g4y"

# Create remote client agent
remote_client = Agent(
    name="decluttered_remote_client",
    seed="remote_client_seed_12345",
    port=9000,  # Different port to avoid conflicts
    mailbox=True  # Enable mailbox for cloud communication
)

class ClientState:
    def __init__(self):
        self.active_sessions = {}
        self.results = {}

client_state = ClientState()

async def send_image_for_processing(ctx: Context, image_path: str, session_id: str = None):
    """Send an image to your deployed agents for processing"""

    if session_id is None:
        session_id = f"remote_session_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    ctx.logger.info(f"[CLIENT] Starting processing for session: {session_id}")

    # Read and encode image
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Create message for detection agent
        captured_image = CapturedImage(
            filename=image_path.split('/')[-1],
            timestamp=int(time.time()),
            file_path=image_path,
            capture_index=1,
            session_id=session_id
        )

        # Send to your detection agent
        ctx.logger.info(f"[CLIENT] Sending image to detection agent...")
        await ctx.send(DETECTION_AGENT_ADDRESS, captured_image)

        # Track session
        client_state.active_sessions[session_id] = {
            'start_time': time.time(),
            'image_path': image_path,
            'status': 'detection_sent'
        }

        return session_id

    except Exception as e:
        ctx.logger.error(f"[CLIENT] Error processing image: {e}")
        return None

# Handle responses from your agents
@remote_client.on_message(model=DetectionResult)
async def handle_detection_result(ctx: Context, sender: str, msg: DetectionResult):
    """Handle detection results from your detection agent"""
    ctx.logger.info(f"[CLIENT] Received detection result for session {msg.session_id}")
    ctx.logger.info(f"[CLIENT] Detected objects: {msg.unique_classes}")

    if msg.session_id in client_state.active_sessions:
        client_state.active_sessions[msg.session_id]['status'] = 'detection_complete'
        client_state.active_sessions[msg.session_id]['detection_result'] = msg

@remote_client.on_message(model=EvaluationResult)
async def handle_evaluation_result(ctx: Context, sender: str, msg: EvaluationResult):
    """Handle AI evaluation results"""
    ctx.logger.info(f"[CLIENT] Received AI evaluation for session {msg.session_id}")
    ctx.logger.info(f"[CLIENT] Resellable items: {msg.resellable_items}")

    if msg.session_id in client_state.active_sessions:
        client_state.active_sessions[msg.session_id]['status'] = 'evaluation_complete'
        client_state.active_sessions[msg.session_id]['evaluation_result'] = msg

@remote_client.on_message(model=ProcessingResult)
async def handle_processing_result(ctx: Context, sender: str, msg: ProcessingResult):
    """Handle final processing results"""
    ctx.logger.info(f"[CLIENT] Received processing result for session {msg.session_id}")
    ctx.logger.info(f"[CLIENT] Cropped files: {msg.cropped_files}")

    if msg.session_id in client_state.active_sessions:
        client_state.active_sessions[msg.session_id]['status'] = 'processing_complete'
        client_state.active_sessions[msg.session_id]['processing_result'] = msg

        # Final results
        session = client_state.active_sessions[msg.session_id]
        total_time = time.time() - session['start_time']

        ctx.logger.info(f"[CLIENT] ✅ SESSION COMPLETE!")
        ctx.logger.info(f"[CLIENT] Total processing time: {total_time:.2f}s")
        ctx.logger.info(f"[CLIENT] Resellable objects: {msg.total_objects_processed}")
        ctx.logger.info(f"[CLIENT] Cropped files: {len(msg.cropped_files)}")

@remote_client.on_event("startup")
async def startup_client(ctx: Context):
    """Client startup - ready to process images"""
    ctx.logger.info("[CLIENT] 🚀 Remote client ready!")
    ctx.logger.info("[CLIENT] Connected to your deployed Decluttered.ai agents")
    ctx.logger.info(f"[CLIENT] Detection Agent: {DETECTION_AGENT_ADDRESS}")

    # Example: Process a test image (your friend would replace this)
    # Uncomment the line below to automatically process an image on startup
    # await send_image_for_processing(ctx, "path/to/image.jpg")

@remote_client.on_interval(period=30.0)
async def status_check(ctx: Context):
    """Periodic status check"""
    active_count = len([s for s in client_state.active_sessions.values()
                       if s['status'] != 'processing_complete'])

    if active_count > 0:
        ctx.logger.info(f"[CLIENT] Active sessions: {active_count}")

# Example usage functions your friend can call
async def process_image_example(image_path: str):
    """Example function to process an image"""
    ctx = Context()  # This won't work outside the agent, just for example
    session_id = await send_image_for_processing(ctx, image_path)
    return session_id

def get_session_status(session_id: str):
    """Get status of a processing session"""
    return client_state.active_sessions.get(session_id, {})

if __name__ == "__main__":
    print("🌐 Starting Remote Client for Decluttered.ai Agents")
    print("📋 Your friend can use this to connect to your deployed agents")
    print("\n📝 Instructions for your friend:")
    print("1. Install: pip install uagents")
    print("2. Replace AGENT_ADDRESSES with your actual deployed addresses")
    print("3. Run this script")
    print("4. Use send_image_for_processing() to process images")
    print("\n🚀 Starting client...")

    remote_client.run()