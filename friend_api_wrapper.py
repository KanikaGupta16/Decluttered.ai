"""
FastAPI Wrapper for Your Friend's App
Simple HTTP API to use your deployed Decluttered.ai agents
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
import uuid
import asyncio
import os
from typing import Dict, Any
from uagents import Agent, Context, Model
from pydantic import BaseModel

# Response models for your friend's API
class ProcessingResponse(BaseModel):
    success: bool
    session_id: str
    message: str
    estimated_time: str = "30-60 seconds"

class StatusResponse(BaseModel):
    session_id: str
    status: str  # "processing", "detection_complete", "evaluation_complete", "processing_complete", "failed"
    progress: float  # 0.0 to 1.0
    results: Dict[str, Any] = {}

class ResultResponse(BaseModel):
    session_id: str
    success: bool
    detected_objects: list = []
    resellable_items: list = []
    cropped_files: list = []
    processing_time: float = 0.0
    error_message: str = None

# Your agent addresses (replace with actual deployed addresses)
AGENT_ADDRESSES = {
    "detection": "agent1qte25te5k79ygajeapzelgyle8ape8pvzdxdw9zndp4kph53qeq5unc8n6j",
    "ai_evaluator": "agent1q0vgqkwxlz7lfve6tqyse6z7m3zccv4uv7kt484jlc77dutxngzy62ea92p",
    "image_processor": "agent1qwgxuc8z9nsafsl30creg2hhykclaw4pnwm7ge9e5l3qakrx4r6nu67p2au",
    "report_coordinator": "agent1qvf8rwqhnuj85w9fl7kap6uszlk00gpjed0pq6vh289thwqys0zeq9w9g4y"
}

# FastAPI app
app = FastAPI(title="Decluttered.ai API", description="Connect to deployed agents")

# Enable CORS for web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for session tracking
sessions: Dict[str, Dict[str, Any]] = {}

# Message models (copy from your agents)
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
    unique_classes: list
    detection_count: int
    largest_instances: Dict[str, str]

class EvaluationResult(Model):
    image_path: str
    timestamp: int
    session_id: str
    original_objects: list
    resellable_items: list
    evaluation_confidence: str
    gemini_raw_response: str
    filtered_detections: Dict[str, str]

class ProcessingResult(Model):
    original_image_path: str
    timestamp: int
    session_id: str
    resellable_objects: list
    cropped_files: list
    processing_summary: Dict[str, Any]
    total_objects_processed: int

# Agent for communicating with your deployed agents
api_agent = Agent(
    name="friend_api_wrapper",
    seed="friend_api_wrapper_seed",
    port=9001,
    mailbox=True
)

# Agent message handlers
@api_agent.on_message(model=DetectionResult)
async def handle_detection_result(ctx: Context, sender: str, msg: DetectionResult):
    if msg.session_id in sessions:
        sessions[msg.session_id].update({
            'status': 'detection_complete',
            'progress': 0.25,
            'detection_result': {
                'detected_objects': msg.unique_classes,
                'detection_count': msg.detection_count
            }
        })

@api_agent.on_message(model=EvaluationResult)
async def handle_evaluation_result(ctx: Context, sender: str, msg: EvaluationResult):
    if msg.session_id in sessions:
        sessions[msg.session_id].update({
            'status': 'evaluation_complete',
            'progress': 0.5,
            'evaluation_result': {
                'resellable_items': msg.resellable_items,
                'confidence': msg.evaluation_confidence
            }
        })

@api_agent.on_message(model=ProcessingResult)
async def handle_processing_result(ctx: Context, sender: str, msg: ProcessingResult):
    if msg.session_id in sessions:
        end_time = time.time()
        start_time = sessions[msg.session_id]['start_time']

        sessions[msg.session_id].update({
            'status': 'processing_complete',
            'progress': 1.0,
            'processing_result': {
                'cropped_files': msg.cropped_files,
                'total_objects': msg.total_objects_processed,
                'processing_time': end_time - start_time
            },
            'completed': True
        })

# Store agent context globally for API endpoints
agent_context = None

@api_agent.on_event("startup")
async def store_context(ctx: Context):
    global agent_context
    agent_context = ctx
    ctx.logger.info("🚀 Friend API wrapper ready!")

# API Endpoints for your friend
@app.post("/api/process-image", response_model=ProcessingResponse)
async def process_image(file: UploadFile = File(...)):
    """Upload an image for processing by your deployed agents"""

    # Validate file
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise HTTPException(status_code=400, detail="Only JPG/PNG files allowed")

    # Generate session ID
    session_id = f"api_session_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    # Save uploaded file
    upload_dir = "api_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{session_id}_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Initialize session tracking
    sessions[session_id] = {
        'start_time': time.time(),
        'status': 'processing',
        'progress': 0.0,
        'file_path': file_path,
        'original_filename': file.filename
    }

    # Send to your detection agent
    if agent_context:
        captured_image = CapturedImage(
            filename=file.filename,
            timestamp=int(time.time()),
            file_path=file_path,
            capture_index=1,
            session_id=session_id
        )

        await agent_context.send(AGENT_ADDRESSES["detection"], captured_image)

    return ProcessingResponse(
        success=True,
        session_id=session_id,
        message="Image uploaded and sent for processing"
    )

@app.get("/api/status/{session_id}", response_model=StatusResponse)
async def get_status(session_id: str):
    """Get processing status for a session"""

    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]

    # Build results
    results = {}
    if 'detection_result' in session:
        results['detection'] = session['detection_result']
    if 'evaluation_result' in session:
        results['evaluation'] = session['evaluation_result']
    if 'processing_result' in session:
        results['processing'] = session['processing_result']

    return StatusResponse(
        session_id=session_id,
        status=session['status'],
        progress=session['progress'],
        results=results
    )

@app.get("/api/result/{session_id}", response_model=ResultResponse)
async def get_result(session_id: str):
    """Get final results for a completed session"""

    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]

    if not session.get('completed', False):
        raise HTTPException(status_code=202, detail="Processing not complete")

    # Extract final results
    detected_objects = session.get('detection_result', {}).get('detected_objects', [])
    resellable_items = session.get('evaluation_result', {}).get('resellable_items', [])
    cropped_files = session.get('processing_result', {}).get('cropped_files', [])
    processing_time = session.get('processing_result', {}).get('processing_time', 0.0)

    return ResultResponse(
        session_id=session_id,
        success=True,
        detected_objects=detected_objects,
        resellable_items=resellable_items,
        cropped_files=cropped_files,
        processing_time=processing_time
    )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "OK",
        "service": "Decluttered.ai API Wrapper",
        "connected_agents": len(AGENT_ADDRESSES),
        "active_sessions": len(sessions)
    }

@app.get("/")
async def root():
    """API documentation"""
    return {
        "message": "Decluttered.ai API Wrapper",
        "documentation": "/docs",
        "endpoints": {
            "POST /api/process-image": "Upload image for processing",
            "GET /api/status/{session_id}": "Check processing status",
            "GET /api/result/{session_id}": "Get final results",
            "GET /api/health": "Health check"
        },
        "example_curl": {
            "upload": "curl -X POST -F 'file=@image.jpg' http://localhost:8080/api/process-image",
            "status": "curl http://localhost:8080/api/status/{session_id}",
            "result": "curl http://localhost:8080/api/result/{session_id}"
        }
    }

# Run both the agent and FastAPI server
async def run_both():
    """Run the agent and FastAPI server together"""

    # Start the agent in the background
    import threading
    agent_thread = threading.Thread(target=lambda: api_agent.run(), daemon=True)
    agent_thread.start()

    # Give agent time to start
    await asyncio.sleep(2)

    # Run FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    print("🚀 Starting Friend API Wrapper for Decluttered.ai")
    print("📡 Connecting to your deployed agents...")
    print("🌐 API will be available at: http://localhost:8080")
    print("📖 Documentation at: http://localhost:8080/docs")

    # Run everything
    asyncio.run(run_both())