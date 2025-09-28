"""
Pipeline Coordinator Agent for Decluttered.ai
Orchestrates the complete pipeline from image recognition to marketplace listing
"""

from uagents import Agent, Context
import time
import uuid
import sys
import os
sys.path.append(os.path.dirname(__file__))
from typing import Dict, Optional
from api_message_models import (
    CompletePipelineRequest,
    CompletePipelineResult,
    ImageRecognitionRequest,
    ImageRecognitionResult,
    PriceResearchResult,
    ListingCreationResult
)

# Pipeline Coordinator Agent Configuration
IMAGE_RECOGNITION_ADDRESS = "agent1qw8k9gxs3rx8f8hw6z7v2d3j5j9e9s8h3n4g7p2k8x3m2z5c7v9r4q1w2e3"

# Create the Pipeline Coordinator Agent (Mailbox enabled)
pipeline_coordinator_agent = Agent(
    name="pipeline_coordinator_agent",
    seed="pipeline_coordinator_agent_seed_decluttered_api",
    port=8015,
    mailbox=True
)

class PipelineSession:
    def __init__(self, request: CompletePipelineRequest):
        self.request = request
        self.start_time = time.time()
        self.steps_completed = []
        self.image_recognition_result: Optional[ImageRecognitionResult] = None
        self.price_research_result: Optional[PriceResearchResult] = None
        self.listing_creation_result: Optional[ListingCreationResult] = None
        self.error_message: Optional[str] = None
        self.completed = False

class PipelineState:
    def __init__(self):
        self.active_sessions: Dict[str, PipelineSession] = {}
        self.completed_sessions = 0
        self.failed_sessions = 0

pipeline_state = PipelineState()


@pipeline_coordinator_agent.on_event("startup")
async def setup_pipeline_coordinator(ctx: Context):
    """Initialize Pipeline Coordinator Agent."""
    ctx.logger.info("[PIPELINE_COORDINATOR] Pipeline Coordinator Agent starting up...")
    ctx.logger.info("[PIPELINE_COORDINATOR] Ready to orchestrate complete marketplace pipelines")


@pipeline_coordinator_agent.on_message(model=CompletePipelineRequest)
async def handle_complete_pipeline_request(ctx: Context, sender: str, msg: CompletePipelineRequest):
    """Handle complete pipeline execution requests."""
    ctx.logger.info(f"[PIPELINE_COORDINATOR] Starting complete pipeline for session {msg.session_id}")

    # Create session tracking
    session = PipelineSession(msg)
    pipeline_state.active_sessions[msg.session_id] = session

    # Generate unique request ID for this pipeline
    request_id = f"pipeline_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    try:
        # Step 1: Image Recognition
        ctx.logger.info("[PIPELINE_COORDINATOR] Step 1: Starting image recognition...")

        image_recognition_request = ImageRecognitionRequest(
            image_base64=msg.image_base64,
            session_id=msg.session_id,
            request_id=request_id
        )

        # Send to Image Recognition Agent
        await ctx.send(IMAGE_RECOGNITION_ADDRESS, image_recognition_request)

        session.steps_completed.append("image_recognition_initiated")
        ctx.logger.info("[PIPELINE_COORDINATOR] Image recognition request sent, waiting for response...")

    except Exception as e:
        ctx.logger.error(f"[PIPELINE_COORDINATOR] Error starting pipeline: {e}")

        # Send error response
        error_result = CompletePipelineResult(
            session_id=msg.session_id,
            success=False,
            error_message=f"Pipeline initiation failed: {str(e)}"
        )

        await ctx.send(sender, error_result)

        # Clean up session
        pipeline_state.active_sessions.pop(msg.session_id, None)
        pipeline_state.failed_sessions += 1


@pipeline_coordinator_agent.on_message(model=ImageRecognitionResult)
async def handle_image_recognition_result(ctx: Context, sender: str, msg: ImageRecognitionResult):
    """Handle image recognition results and continue pipeline."""
    session = pipeline_state.active_sessions.get(msg.session_id)
    if not session:
        ctx.logger.warning(f"[PIPELINE_COORDINATOR] Received image recognition result for unknown session: {msg.session_id}")
        return

    ctx.logger.info(f"[PIPELINE_COORDINATOR] Step 1 completed for session {msg.session_id}")

    session.image_recognition_result = msg
    session.steps_completed.append("image_recognition_completed")

    if not msg.success:
        ctx.logger.error(f"[PIPELINE_COORDINATOR] Image recognition failed: {msg.error_message}")
        await finalize_pipeline_session(ctx, session, success=False, error_message=f"Image recognition failed: {msg.error_message}")
        return

    if not msg.product_name:
        ctx.logger.error("[PIPELINE_COORDINATOR] Image recognition succeeded but no product name found")
        await finalize_pipeline_session(ctx, session, success=False, error_message="No product identified in image")
        return

    ctx.logger.info(f"[PIPELINE_COORDINATOR] Product identified: {msg.product_name}")
    # Price research is automatically triggered by the Image Recognition Agent
    # We just wait for the price research result


@pipeline_coordinator_agent.on_message(model=PriceResearchResult)
async def handle_price_research_result(ctx: Context, sender: str, msg: PriceResearchResult):
    """Handle price research results and continue pipeline."""
    session = pipeline_state.active_sessions.get(msg.session_id)
    if not session:
        ctx.logger.warning(f"[PIPELINE_COORDINATOR] Received price research result for unknown session: {msg.session_id}")
        return

    ctx.logger.info(f"[PIPELINE_COORDINATOR] Step 2 completed for session {msg.session_id}")

    session.price_research_result = msg
    session.steps_completed.append("price_research_completed")

    if not msg.success:
        ctx.logger.error(f"[PIPELINE_COORDINATOR] Price research failed: {msg.error_message}")
        await finalize_pipeline_session(ctx, session, success=False, error_message=f"Price research failed: {msg.error_message}")
        return

    ctx.logger.info(f"[PIPELINE_COORDINATOR] Found {len(msg.comps)} price comparisons")
    # Listing creation is automatically triggered by the Price Scraper Agent
    # We just wait for the listing creation result


@pipeline_coordinator_agent.on_message(model=ListingCreationResult)
async def handle_listing_creation_result(ctx: Context, sender: str, msg: ListingCreationResult):
    """Handle listing creation results and complete pipeline."""
    session = pipeline_state.active_sessions.get(msg.session_id)
    if not session:
        ctx.logger.warning(f"[PIPELINE_COORDINATOR] Received listing creation result for unknown session: {msg.session_id}")
        return

    ctx.logger.info(f"[PIPELINE_COORDINATOR] Step 3 completed for session {msg.session_id}")

    session.listing_creation_result = msg
    session.steps_completed.append("listing_creation_completed")

    if not msg.success:
        ctx.logger.error(f"[PIPELINE_COORDINATOR] Listing creation failed: {msg.error_message}")
        await finalize_pipeline_session(ctx, session, success=False, error_message=f"Listing creation failed: {msg.error_message}")
        return

    successful_listings = [listing for listing in msg.listings if listing.success]
    ctx.logger.info(f"[PIPELINE_COORDINATOR] Created {len(successful_listings)} successful listings")

    # Pipeline completed successfully
    await finalize_pipeline_session(ctx, session, success=True)


async def finalize_pipeline_session(ctx: Context, session: PipelineSession, success: bool, error_message: Optional[str] = None):
    """Finalize and send results for a pipeline session."""
    if session.completed:
        return  # Already finalized

    execution_time = int((time.time() - session.start_time) * 1000)

    # Create final result
    result = CompletePipelineResult(
        session_id=session.request.session_id,
        success=success,
        steps_completed=session.steps_completed,
        image_recognition=session.image_recognition_result,
        price_research=session.price_research_result,
        listing_creation=session.listing_creation_result,
        error_message=error_message,
        total_execution_time_ms=execution_time
    )

    # Send result to whoever initiated the pipeline (typically the web API agent)
    # We'll send to all connected agents since we don't track the original sender
    # In a real implementation, you'd track the original sender
    ctx.logger.info(f"[PIPELINE_COORDINATOR] Pipeline {'completed' if success else 'failed'} for session {session.request.session_id} in {execution_time}ms")

    # Mark session as completed
    session.completed = True

    # Update stats
    if success:
        pipeline_state.completed_sessions += 1
    else:
        pipeline_state.failed_sessions += 1

    # Clean up session after a delay (to allow for any late responses)
    # In a real implementation, you'd implement proper cleanup


@pipeline_coordinator_agent.on_interval(period=300.0)  # Every 5 minutes
async def cleanup_old_sessions(ctx: Context):
    """Clean up old completed or stalled sessions."""
    current_time = time.time()
    sessions_to_remove = []

    for session_id, session in pipeline_state.active_sessions.items():
        session_age = current_time - session.start_time

        # Remove completed sessions older than 5 minutes
        if session.completed and session_age > 300:
            sessions_to_remove.append(session_id)

        # Remove stalled sessions older than 15 minutes
        elif not session.completed and session_age > 900:
            ctx.logger.warning(f"[PIPELINE_COORDINATOR] Removing stalled session: {session_id}")
            sessions_to_remove.append(session_id)
            pipeline_state.failed_sessions += 1

    for session_id in sessions_to_remove:
        pipeline_state.active_sessions.pop(session_id, None)

    if sessions_to_remove:
        ctx.logger.info(f"[PIPELINE_COORDINATOR] Cleaned up {len(sessions_to_remove)} old sessions")

    # Log stats
    active_count = len(pipeline_state.active_sessions)
    if active_count > 0 or pipeline_state.completed_sessions > 0:
        ctx.logger.info(f"[PIPELINE_COORDINATOR] Stats - Active: {active_count}, Completed: {pipeline_state.completed_sessions}, Failed: {pipeline_state.failed_sessions}")


@pipeline_coordinator_agent.on_event("shutdown")
async def cleanup_pipeline_coordinator(ctx: Context):
    """Cleanup on shutdown."""
    ctx.logger.info("[PIPELINE_COORDINATOR] Pipeline Coordinator Agent shutting down")
    ctx.logger.info(f"[PIPELINE_COORDINATOR] Final stats - Completed: {pipeline_state.completed_sessions}, Failed: {pipeline_state.failed_sessions}")


if __name__ == "__main__":
    print("[PIPELINE_COORDINATOR] Starting Pipeline Coordinator Agent...")
    print("[PIPELINE_COORDINATOR] Ready to orchestrate complete marketplace pipelines")
    print("[PIPELINE_COORDINATOR] Waiting for CompletePipelineRequest messages...")
    pipeline_coordinator_agent.run()