"""
Report Coordinator Agent for Decluttered.ai
Central coordination, reporting, and state management
Extracted from OD.py reporting and coordination logic
"""

from uagents import Agent, Context, Model
import os
import time
from typing import Dict, List, Optional, Any


# Message Models for inter-agent communication
class ProcessingResult(Model):
    original_image_path: str
    timestamp: int
    session_id: str
    resellable_objects: List[str]
    cropped_files: List[str]
    processing_summary: Dict[str, Any]
    total_objects_processed: int


class SystemStatus(Model):
    active_agents: int
    processing_queue_size: int
    system_health: str
    total_sessions: int
    current_session: str


class ReportData(Model):
    session_id: str
    total_images_processed: int
    total_unique_objects: int
    total_cropped_files: int
    final_report_path: str
    session_summary: Dict[str, Any]


class StartSystem(Model):
    duration_seconds: int = 10
    max_captures: int = 6
    cooldown_seconds: float = 1.0


# Report Coordinator Agent Configuration
REPORT_FILENAME = "analysis_report_resellables.txt"

# Create the Report Coordinator Agent (Mailbox enabled)
report_coordinator_agent = Agent(
    name="report_coordinator_agent",
    seed="report_coordinator_seed_decluttered_ai",
    port=8005,
    mailbox=True
)

# Global state management
class CoordinatorState:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}  # session_id -> session_data
        self.current_session = ""
        self.total_sessions = 0
        self.global_seen_objects = set()  # Track unique objects across all sessions
        self.system_start_time = 0
        self.processing_results: List[ProcessingResult] = []

coordinator_state = CoordinatorState()


def write_analysis_report(session_id: str, results: List[Dict]) -> str:
    """
    Writes the final analysis results to the report file.
    Returns the path to the generated report.
    """
    report_path = f"{session_id}_{REPORT_FILENAME}"

    print(f"[COORDINATOR] Writing final analysis report to {report_path}...")

    try:
        with open(report_path, "w") as f:
            if not results:
                f.write("No resellable objects were detected across all captures.\n")
            else:
                f.write("--- Declutter Detector Analysis Report ---\n\n")
                f.write(f"Session ID: {session_id}\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                for result in results:
                    f.write(result + "\n")

                # Add summary statistics
                f.write("\n--- Session Summary ---\n")
                f.write(f"Total Images Processed: {len(results)}\n")
                f.write(f"Total Unique Object Types: {len(coordinator_state.global_seen_objects)}\n")
                f.write(f"Session Duration: {time.time() - coordinator_state.system_start_time:.1f} seconds\n")

        print(f"[COORDINATOR] Report saved successfully to {report_path}")
        return report_path

    except IOError as e:
        print(f"[COORDINATOR ERROR] Could not write report file: {e}")
        return ""


@report_coordinator_agent.on_event("startup")
async def setup_coordinator(ctx: Context):
    """Initialize report coordinator on agent startup."""
    ctx.logger.info("[COORDINATOR] Report Coordinator Agent starting up...")
    coordinator_state.system_start_time = time.time()
    ctx.logger.info("[COORDINATOR] Coordinator initialized successfully")


@report_coordinator_agent.on_message(model=StartSystem)
async def start_system_coordination(ctx: Context, sender: str, msg: StartSystem):
    """Coordinate the start of the entire system."""
    session_id = f"session_{int(time.time())}"
    coordinator_state.current_session = session_id
    coordinator_state.total_sessions += 1
    coordinator_state.global_seen_objects.clear()
    coordinator_state.processing_results.clear()

    # Initialize session data
    coordinator_state.sessions[session_id] = {
        "start_time": time.time(),
        "duration_seconds": msg.duration_seconds,
        "max_captures": msg.max_captures,
        "cooldown_seconds": msg.cooldown_seconds,
        "images_processed": 0,
        "total_objects_found": 0,
        "unique_objects": set(),
        "cropped_files": [],
        "status": "active"
    }

    ctx.logger.info(f"[COORDINATOR] Starting new system session: {session_id}")
    ctx.logger.info(f"[COORDINATOR] Configuration - Duration: {msg.duration_seconds}s, Max captures: {msg.max_captures}")

    # TODO: Send StartCapture message to Camera Agent
    # from agents.camera_agent import StartCapture
    # start_capture_msg = StartCapture(
    #     duration_seconds=msg.duration_seconds,
    #     max_captures=msg.max_captures,
    #     cooldown_seconds=msg.cooldown_seconds
    # )
    # await ctx.send("camera_agent_address", start_capture_msg)


@report_coordinator_agent.on_message(model=ProcessingResult)
async def coordinate_processing_result(ctx: Context, sender: str, msg: ProcessingResult):
    """Coordinate and aggregate processing results from Image Processor Agent."""
    ctx.logger.info(f"[COORDINATOR] Received processing result for: {os.path.basename(msg.original_image_path)}")

    # Update session tracking
    if coordinator_state.current_session != msg.session_id:
        ctx.logger.warning(f"[COORDINATOR] Session mismatch: current={coordinator_state.current_session}, received={msg.session_id}")
        return

    if msg.session_id not in coordinator_state.sessions:
        ctx.logger.warning(f"[COORDINATOR] Unknown session: {msg.session_id}")
        return

    # Store processing result
    coordinator_state.processing_results.append(msg)

    # Update session data
    session_data = coordinator_state.sessions[msg.session_id]
    session_data["images_processed"] += 1
    session_data["total_objects_found"] += msg.total_objects_processed
    session_data["cropped_files"].extend(msg.cropped_files)

    # Update global unique objects tracking
    for obj_name in msg.resellable_objects:
        coordinator_state.global_seen_objects.add(obj_name.lower())
        session_data["unique_objects"].add(obj_name.lower())

    ctx.logger.info(
        f"[COORDINATOR] Session {msg.session_id} update - "
        f"Images: {session_data['images_processed']}, "
        f"Objects: {session_data['total_objects_found']}, "
        f"Unique types: {len(session_data['unique_objects'])}"
    )

    # Generate report entry for this processing result
    report_entry = generate_report_entry(msg)

    # Check if session should be completed (could be based on time, image count, etc.)
    # For now, we'll generate reports periodically
    ctx.logger.info(f"[COORDINATOR] Processed result from {os.path.basename(msg.original_image_path)}")


def generate_report_entry(result: ProcessingResult) -> str:
    """Generate a report entry for a processing result."""
    filename = os.path.basename(result.original_image_path)

    if not result.resellable_objects:
        return f"Capture: {filename}\n  - No resellable objects found\n{'-'*40}"

    # Get coordinates of first item for location reference
    first_coords = "(0, 0, 0, 0)"
    if result.processing_summary:
        first_item = list(result.processing_summary.values())[0]
        if "coordinates" in first_item:
            first_coords = str(first_item["coordinates"])

    report_entry = (
        f"Capture: {filename}\n"
        f"  - Resellable Objects: {', '.join(result.resellable_objects)}\n"
        f"  - Cropped Files: {', '.join(result.cropped_files)}\n"
        f"  - Location (First Item): XYXY {first_coords}\n"
        f"  - Processing Summary: {len(result.resellable_objects)} items processed\n"
        f"{'-'*40}"
    )

    return report_entry


@report_coordinator_agent.on_interval(period=30.0)
async def generate_interim_report(ctx: Context):
    """Generate interim reports and check session status."""
    if not coordinator_state.current_session:
        return

    session_id = coordinator_state.current_session
    if session_id not in coordinator_state.sessions:
        return

    session_data = coordinator_state.sessions[session_id]

    # Check if session has been active long enough to generate a report
    if session_data["images_processed"] > 0:
        ctx.logger.info(
            f"[COORDINATOR] Session {session_id} interim status - "
            f"Images: {session_data['images_processed']}, "
            f"Unique objects: {len(session_data['unique_objects'])}, "
            f"Cropped files: {len(session_data['cropped_files'])}"
        )

        # Generate interim report if we have results
        if coordinator_state.processing_results:
            report_entries = []
            for result in coordinator_state.processing_results:
                report_entries.append(generate_report_entry(result))

            # Write interim report
            report_path = write_analysis_report(session_id, report_entries)

            if report_path:
                ctx.logger.info(f"[COORDINATOR] Interim report generated: {report_path}")


@report_coordinator_agent.on_interval(period=60.0)
async def session_timeout_check(ctx: Context):
    """Check for session timeouts and finalize completed sessions."""
    current_time = time.time()

    for session_id, session_data in coordinator_state.sessions.items():
        if session_data["status"] == "active":
            session_duration = current_time - session_data["start_time"]
            configured_duration = session_data["duration_seconds"]

            # Check if session should be finalized (exceeded duration + buffer)
            if session_duration > (configured_duration + 30):  # 30 second buffer
                ctx.logger.info(f"[COORDINATOR] Finalizing session {session_id} due to timeout")
                await finalize_session(ctx, session_id)


async def finalize_session(ctx: Context, session_id: str):
    """Finalize a session and generate final report."""
    if session_id not in coordinator_state.sessions:
        return

    session_data = coordinator_state.sessions[session_id]
    session_data["status"] = "completed"
    session_data["end_time"] = time.time()

    # Generate final report
    report_entries = []
    session_results = [r for r in coordinator_state.processing_results if r.session_id == session_id]

    for result in session_results:
        report_entries.append(generate_report_entry(result))

    final_report_path = write_analysis_report(session_id, report_entries)

    # Create final report data
    report_data = ReportData(
        session_id=session_id,
        total_images_processed=session_data["images_processed"],
        total_unique_objects=len(session_data["unique_objects"]),
        total_cropped_files=len(session_data["cropped_files"]),
        final_report_path=final_report_path,
        session_summary=session_data
    )

    ctx.logger.info(
        f"[COORDINATOR] Session {session_id} finalized - "
        f"Images: {report_data.total_images_processed}, "
        f"Unique objects: {report_data.total_unique_objects}, "
        f"Report: {final_report_path}"
    )


@report_coordinator_agent.on_interval(period=15.0)
async def system_status_report(ctx: Context):
    """Send periodic system status updates."""
    if coordinator_state.current_session:
        status = SystemStatus(
            active_agents=5,  # Camera, Detection, AI Evaluator, Image Processor, Coordinator
            processing_queue_size=len(coordinator_state.processing_results),
            system_health="healthy" if coordinator_state.processing_results else "idle",
            total_sessions=coordinator_state.total_sessions,
            current_session=coordinator_state.current_session
        )

        ctx.logger.info(
            f"[COORDINATOR STATUS] Agents: {status.active_agents}, "
            f"Queue: {status.processing_queue_size}, "
            f"Health: {status.system_health}, "
            f"Sessions: {status.total_sessions}"
        )


@report_coordinator_agent.on_event("shutdown")
async def cleanup_coordinator(ctx: Context):
    """Cleanup coordinator resources and finalize any active sessions on shutdown."""
    ctx.logger.info("[COORDINATOR] Report Coordinator Agent shutting down")

    # Finalize any active sessions
    for session_id, session_data in coordinator_state.sessions.items():
        if session_data["status"] == "active":
            ctx.logger.info(f"[COORDINATOR] Finalizing active session {session_id} on shutdown")
            await finalize_session(ctx, session_id)

    ctx.logger.info(f"[COORDINATOR] Final stats - Sessions: {coordinator_state.total_sessions}, Global unique objects: {len(coordinator_state.global_seen_objects)}")


if __name__ == "__main__":
    print("[COORDINATOR] Starting Report Coordinator Agent...")
    print("[COORDINATOR] Send StartSystem message to begin system coordination")
    report_coordinator_agent.run()