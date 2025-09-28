"""
Web API Agent for Decluttered.ai
Handles web interface communication and file uploads
Bridges frontend with multi-agent backend system
"""

from uagents import Agent, Context, Model
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import os
import time
import asyncio
import aiofiles
import shutil
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_PORT = int(os.getenv("WEB_API_PORT", "8006"))
UPLOAD_FOLDER = "web_uploads"
CAPTURE_FOLDER = os.getenv("CAPTURE_FOLDER", "captures")
CROPPED_FOLDER = os.getenv("CROPPED_FOLDER", "cropped_resellables")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.mp4', '.mov', '.avi', '.webm'}

# Create the Web API Agent (Mailbox enabled)
web_api_agent = Agent(
    name="web_api_agent",
    seed="web_api_agent_seed_decluttered_ai",
    port=API_PORT,
    mailbox=True
)

# FastAPI app
app = FastAPI(
    title="Decluttered.ai Web API",
    description="Multi-agent decluttering system web interface",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for processing sessions
class ProcessingSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.status = "pending"  # pending, processing, completed, failed
        self.uploaded_files = []
        self.processed_files = []
        self.detected_objects = []
        self.cropped_objects = []
        self.analysis_report = ""
        self.created_at = time.time()
        self.completed_at = None
        self.error_message = ""

# Session storage
processing_sessions: Dict[str, ProcessingSession] = {}

# Message Models for agent communication
class ProcessingRequest(Model):
    session_id: str
    file_paths: List[str]
    processing_type: str  # "image" or "video"

class ProcessingStatus(Model):
    session_id: str
    status: str
    progress: float
    message: str

# Import CapturedImage model for pipeline triggering
class CapturedImage(Model):
    filename: str
    timestamp: int
    file_path: str
    capture_index: int
    session_id: str

def setup_directories():
    """Create necessary directories"""
    for folder in [UPLOAD_FOLDER, CAPTURE_FOLDER, CROPPED_FOLDER]:
        os.makedirs(folder, exist_ok=True)

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

def generate_session_id() -> str:
    """Generate unique session ID"""
    return f"web_session_{int(time.time() * 1000)}"

async def extract_frames_from_video(video_path: str, output_folder: str, max_frames: int = 10) -> List[str]:
    """Extract frames from video for processing"""
    import cv2

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"Could not open video: {video_path}")

    frame_paths = []
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = max(1, total_frames // max_frames)

    current_frame = 0
    while frame_count < max_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = cap.read()

        if not ret:
            break

        frame_filename = f"frame_{int(time.time())}_{frame_count}.jpg"
        frame_path = os.path.join(output_folder, frame_filename)
        cv2.imwrite(frame_path, frame)
        frame_paths.append(frame_path)

        frame_count += 1
        current_frame += frame_interval

    cap.release()
    return frame_paths

async def trigger_detection_pipeline(file_path: str, session_id: str, capture_index: int):
    """Trigger the detection pipeline by sending CapturedImage message"""
    try:
        # Create CapturedImage message
        captured_image = CapturedImage(
            filename=os.path.basename(file_path),
            timestamp=int(time.time()),
            file_path=file_path,
            capture_index=capture_index,
            session_id=session_id
        )

        # Send to Detection Agent to start the pipeline
        await send_to_detection_agent(captured_image)
        print(f"[WEB_API] Triggered pipeline for {os.path.basename(file_path)}")
        return captured_image

    except Exception as e:
        print(f"[WEB_API ERROR] Failed to trigger pipeline: {e}")
        return None

async def process_uploaded_files(session_id: str):
    """Process uploaded files through the agent pipeline"""
    session = processing_sessions[session_id]

    try:
        session.status = "processing"

        # Move uploaded files to captures folder for agent processing
        processed_files = []
        capture_index = 0

        for upload_path in session.uploaded_files:
            file_path = Path(upload_path)

            if file_path.suffix.lower() in ['.mp4', '.mov', '.avi', '.webm']:
                # Extract frames from video
                frames = await extract_frames_from_video(str(file_path), CAPTURE_FOLDER)
                for frame_path in frames:
                    capture_index += 1
                    await trigger_detection_pipeline(frame_path, session_id, capture_index)
                processed_files.extend(frames)
            else:
                # Copy image directly
                dest_path = os.path.join(CAPTURE_FOLDER, f"web_{session_id}_{file_path.name}")
                shutil.copy2(str(file_path), dest_path)
                processed_files.append(dest_path)

                # Trigger pipeline for this image
                capture_index += 1
                await trigger_detection_pipeline(dest_path, session_id, capture_index)

        session.processed_files = processed_files

        # Wait for processing to complete (agents will process via message pipeline)
        await asyncio.sleep(30)  # Give pipeline time to complete

        # Check for results
        session.cropped_objects = [
            f for f in os.listdir(CROPPED_FOLDER)
            if f.endswith('.jpg') and session_id in f
        ]

        # Look for analysis reports
        report_files = [f for f in os.listdir('.') if f.endswith('_analysis_report_resellables.txt')]
        if report_files:
            latest_report = max(report_files, key=os.path.getctime)
            with open(latest_report, 'r') as f:
                session.analysis_report = f.read()

        session.status = "completed"
        session.completed_at = time.time()

    except Exception as e:
        session.status = "failed"
        session.error_message = str(e)

# API Routes
@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "Decluttered.ai Web API",
        "status": "healthy",
        "version": "1.0.0",
        "agents_available": True
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "api_status": "healthy",
        "upload_folder": os.path.exists(UPLOAD_FOLDER),
        "capture_folder": os.path.exists(CAPTURE_FOLDER),
        "cropped_folder": os.path.exists(CROPPED_FOLDER),
        "active_sessions": len(processing_sessions),
        "supported_formats": list(ALLOWED_EXTENSIONS)
    }

@app.get("/agent/address")
async def get_agent_address():
    """Get this agent's address"""
    return {
        "agent_name": "web_api_agent",
        "address": str(web_api_agent.address),
        "port": API_PORT,
        "mailbox_enabled": True
    }

@app.post("/test-pipeline")
async def test_pipeline(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Test the agent pipeline with a single image"""

    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed: {file.filename}"
        )

    session_id = generate_session_id()

    try:
        # Save the test file
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {file.filename} (max {MAX_FILE_SIZE//1024//1024}MB)"
            )

        file_path = os.path.join(CAPTURE_FOLDER, f"test_{session_id}_{file.filename}")
        with open(file_path, 'wb') as f:
            f.write(content)

        # Trigger the pipeline immediately
        await trigger_detection_pipeline(file_path, session_id, 1)

        return {
            "message": "Pipeline triggered successfully",
            "session_id": session_id,
            "file_path": file_path,
            "status": "processing",
            "note": "Check logs for pipeline progress. Results will be in cropped_resellables/ folder."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """Upload images or videos for processing"""

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    session_id = generate_session_id()
    session = ProcessingSession(session_id)
    processing_sessions[session_id] = session

    try:
        uploaded_files = []

        for file in files:
            # Validate file
            if not is_allowed_file(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed: {file.filename}"
                )

            # Check file size
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large: {file.filename} (max {MAX_FILE_SIZE//1024//1024}MB)"
                )

            # Save file
            file_path = os.path.join(UPLOAD_FOLDER, f"{session_id}_{file.filename}")
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)

            uploaded_files.append(file_path)

        session.uploaded_files = uploaded_files

        # Start background processing
        background_tasks.add_task(process_uploaded_files, session_id)

        return {
            "session_id": session_id,
            "status": "uploaded",
            "files_count": len(uploaded_files),
            "message": "Files uploaded successfully, processing started"
        }

    except Exception as e:
        session.status = "failed"
        session.error_message = str(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}")
async def get_session_status(session_id: str):
    """Get processing session status"""

    if session_id not in processing_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = processing_sessions[session_id]

    return {
        "session_id": session_id,
        "status": session.status,
        "uploaded_files_count": len(session.uploaded_files),
        "processed_files_count": len(session.processed_files),
        "detected_objects": session.detected_objects,
        "cropped_objects_count": len(session.cropped_objects),
        "has_analysis_report": bool(session.analysis_report),
        "created_at": session.created_at,
        "completed_at": session.completed_at,
        "error_message": session.error_message
    }

@app.get("/session/{session_id}/results")
async def get_session_results(session_id: str):
    """Get detailed processing results"""

    if session_id not in processing_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = processing_sessions[session_id]

    if session.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Session not completed (status: {session.status})"
        )

    # Get cropped object details
    cropped_objects_details = []
    for obj_file in session.cropped_objects:
        obj_path = os.path.join(CROPPED_FOLDER, obj_file)
        if os.path.exists(obj_path):
            file_size = os.path.getsize(obj_path)
            cropped_objects_details.append({
                "filename": obj_file,
                "size": file_size,
                "download_url": f"/download/cropped/{obj_file}"
            })

    return {
        "session_id": session_id,
        "status": session.status,
        "analysis_report": session.analysis_report,
        "cropped_objects": cropped_objects_details,
        "processing_duration": session.completed_at - session.created_at if session.completed_at else None
    }

@app.get("/download/cropped/{filename}")
async def download_cropped_object(filename: str):
    """Download a cropped object image"""

    file_path = os.path.join(CROPPED_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, filename=filename)

@app.get("/sessions")
async def list_sessions():
    """List all processing sessions"""

    sessions_summary = []
    for session_id, session in processing_sessions.items():
        sessions_summary.append({
            "session_id": session_id,
            "status": session.status,
            "files_count": len(session.uploaded_files),
            "cropped_objects_count": len(session.cropped_objects),
            "created_at": session.created_at,
            "completed_at": session.completed_at
        })

    return {
        "total_sessions": len(sessions_summary),
        "sessions": sorted(sessions_summary, key=lambda x: x["created_at"], reverse=True)
    }

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a processing session and its files"""

    if session_id not in processing_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = processing_sessions[session_id]

    # Delete uploaded files
    for file_path in session.uploaded_files:
        if os.path.exists(file_path):
            os.remove(file_path)

    # Delete processed files
    for file_path in session.processed_files:
        if os.path.exists(file_path):
            os.remove(file_path)

    # Remove from memory
    del processing_sessions[session_id]

    return {"message": f"Session {session_id} deleted successfully"}

@app.on_event("startup")
async def startup_event():
    """Initialize API on startup"""
    setup_directories()
    print(f"[WEB_API] Web API Agent starting on port {API_PORT}")
    print(f"[WEB_API] Upload folder: {UPLOAD_FOLDER}")
    print(f"[WEB_API] Max file size: {MAX_FILE_SIZE//1024//1024}MB")
    print(f"[WEB_API] Supported formats: {ALLOWED_EXTENSIONS}")

# Global variable to store agent context for pipeline triggering
web_api_context = None

# Agent event handlers
@web_api_agent.on_event("startup")
async def setup_web_api(ctx: Context):
    """Initialize web API agent"""
    global web_api_context
    web_api_context = ctx
    ctx.logger.info("[WEB_API] Web API Agent starting up...")
    setup_directories()
    ctx.logger.info("[WEB_API] Directories created successfully")

async def send_to_detection_agent(captured_image: CapturedImage):
    """Send CapturedImage message to detection agent"""
    if web_api_context:
        DETECTION_ADDRESS = "agent1qte25te5k79ygajeapzelgyle8ape8pvzdxdw9zndp4kph53qeq5unc8n6j"
        await web_api_context.send(DETECTION_ADDRESS, captured_image)
        web_api_context.logger.info(f"[WEB_API] Sent {captured_image.filename} to detection pipeline")
    else:
        print("[WEB_API ERROR] Agent context not available for sending messages")

# Run the FastAPI app with the agent
if __name__ == "__main__":
    print("[WEB_API] Starting Decluttered.ai Web API Agent...")

    # Start the FastAPI server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=API_PORT,
        reload=False,
        access_log=True
    )