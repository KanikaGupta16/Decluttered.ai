"""
Image Recognition Agent for Decluttered.ai
Integrates with main.py API (Port 3001) for Google reverse image search and product identification
"""

from uagents import Agent, Context
import requests
import json
import time
import sys
import os
sys.path.append(os.path.dirname(__file__))
from typing import Optional
from api_message_models import (
    ImageRecognitionRequest,
    ImageRecognitionResult,
    PriceResearchRequest
)

# Image Recognition Agent Configuration
IMAGE_RECOGNITION_API_URL = "http://localhost:3001"
PRICE_SCRAPER_ADDRESS = "agent1qw8k9gxs3rx8f8hw6z7v2d3j5j9e9s8h3n4g7p2k8x3m2z5c7v9r4q1w2e3"

# Create the Image Recognition Agent (Mailbox enabled)
image_recognition_agent = Agent(
    name="image_recognition_agent",
    seed="image_recognition_agent_seed_decluttered_api",
    port=8010,
    mailbox=True
)

class ImageRecognitionState:
    def __init__(self):
        self.api_healthy = False
        self.requests_processed = 0
        self.last_health_check = 0

recognition_state = ImageRecognitionState()


async def check_api_health() -> bool:
    """Check if the Image Recognition API is healthy and ready."""
    try:
        response = requests.get(f"{IMAGE_RECOGNITION_API_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            return health_data.get("status") == "OK" and health_data.get("browser_ready", False)
        return False
    except Exception as e:
        return False


@image_recognition_agent.on_event("startup")
async def setup_image_recognition(ctx: Context):
    """Initialize and check Image Recognition API connection."""
    ctx.logger.info("[IMAGE_RECOGNITION] Image Recognition Agent starting up...")

    # Check API health
    recognition_state.api_healthy = await check_api_health()
    recognition_state.last_health_check = time.time()

    if recognition_state.api_healthy:
        ctx.logger.info("[IMAGE_RECOGNITION] Successfully connected to Image Recognition API")
    else:
        ctx.logger.warning("[IMAGE_RECOGNITION] Could not connect to Image Recognition API - will retry")


@image_recognition_agent.on_message(model=ImageRecognitionRequest)
async def process_image_recognition(ctx: Context, sender: str, msg: ImageRecognitionRequest):
    """Process image recognition request using the external API."""
    ctx.logger.info(f"[IMAGE_RECOGNITION] Processing request {msg.request_id} from session {msg.session_id}")

    # Check API health if it's been a while
    current_time = time.time()
    if current_time - recognition_state.last_health_check > 300:  # 5 minutes
        recognition_state.api_healthy = await check_api_health()
        recognition_state.last_health_check = current_time

    if not recognition_state.api_healthy:
        ctx.logger.error("[IMAGE_RECOGNITION] API not healthy, checking status...")
        recognition_state.api_healthy = await check_api_health()

        if not recognition_state.api_healthy:
            # Send error response
            error_result = ImageRecognitionResult(
                session_id=msg.session_id,
                request_id=msg.request_id,
                success=False,
                error_message="Image Recognition API is not available"
            )
            await ctx.send(sender, error_result)
            return

    try:
        # Prepare API request
        api_payload = {
            "image_base64": msg.image_base64
        }

        ctx.logger.info("[IMAGE_RECOGNITION] Sending request to external API...")

        # Make API call with timeout
        response = requests.post(
            f"{IMAGE_RECOGNITION_API_URL}/api/recognition/basic",
            json=api_payload,
            timeout=60,  # Allow up to 60 seconds for image processing
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            api_data = response.json()

            if api_data.get("ok", False):
                data = api_data.get("data", {})

                # Extract product information
                product_name = data.get("product_name")
                source_url = data.get("source_url")
                host = data.get("host")
                pricing = data.get("pricing")
                rating = data.get("rating")

                ctx.logger.info(f"[IMAGE_RECOGNITION] Successfully identified product: {product_name}")

                # Create successful result
                result = ImageRecognitionResult(
                    session_id=msg.session_id,
                    request_id=msg.request_id,
                    success=True,
                    product_name=product_name,
                    source_url=source_url,
                    host=host,
                    pricing=pricing,
                    rating=rating
                )

                # Send result back to sender
                await ctx.send(sender, result)

                # If we successfully identified a product, trigger price research
                if product_name:
                    ctx.logger.info(f"[IMAGE_RECOGNITION] Triggering price research for: {product_name}")

                    price_request = PriceResearchRequest(
                        product_name=product_name,
                        platforms=["facebook", "ebay"],
                        condition_filter="all",
                        session_id=msg.session_id,
                        request_id=msg.request_id
                    )

                    # Send to Price Scraper Agent
                    await ctx.send(PRICE_SCRAPER_ADDRESS, price_request)

                recognition_state.requests_processed += 1

            else:
                # API returned ok: false
                error_msg = api_data.get("message", "Unknown API error")
                ctx.logger.error(f"[IMAGE_RECOGNITION] API error: {error_msg}")

                error_result = ImageRecognitionResult(
                    session_id=msg.session_id,
                    request_id=msg.request_id,
                    success=False,
                    error_message=f"Recognition failed: {error_msg}"
                )
                await ctx.send(sender, error_result)

        else:
            # HTTP error
            ctx.logger.error(f"[IMAGE_RECOGNITION] API HTTP error: {response.status_code}")

            error_result = ImageRecognitionResult(
                session_id=msg.session_id,
                request_id=msg.request_id,
                success=False,
                error_message=f"API HTTP error: {response.status_code}"
            )
            await ctx.send(sender, error_result)

    except requests.exceptions.Timeout:
        ctx.logger.error("[IMAGE_RECOGNITION] API request timed out")

        error_result = ImageRecognitionResult(
            session_id=msg.session_id,
            request_id=msg.request_id,
            success=False,
            error_message="Recognition request timed out"
        )
        await ctx.send(sender, error_result)

    except Exception as e:
        ctx.logger.error(f"[IMAGE_RECOGNITION] Error processing request: {e}")

        error_result = ImageRecognitionResult(
            session_id=msg.session_id,
            request_id=msg.request_id,
            success=False,
            error_message=f"Processing error: {str(e)}"
        )
        await ctx.send(sender, error_result)


@image_recognition_agent.on_interval(period=300.0)  # Every 5 minutes
async def health_check_interval(ctx: Context):
    """Periodic health check of the Image Recognition API."""
    recognition_state.api_healthy = await check_api_health()
    recognition_state.last_health_check = time.time()

    if recognition_state.api_healthy:
        ctx.logger.info(f"[IMAGE_RECOGNITION] Health check passed - Processed {recognition_state.requests_processed} requests")
    else:
        ctx.logger.warning("[IMAGE_RECOGNITION] Health check failed - API not available")


@image_recognition_agent.on_event("shutdown")
async def cleanup_image_recognition(ctx: Context):
    """Cleanup on shutdown."""
    ctx.logger.info("[IMAGE_RECOGNITION] Image Recognition Agent shutting down")


if __name__ == "__main__":
    print("[IMAGE_RECOGNITION] Starting Image Recognition Agent...")
    print("[IMAGE_RECOGNITION] Connecting to API at http://localhost:3001")
    print("[IMAGE_RECOGNITION] Waiting for ImageRecognitionRequest messages...")
    image_recognition_agent.run()