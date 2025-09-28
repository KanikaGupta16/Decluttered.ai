"""
eBay Improved Listing Agent for Decluttered.ai
Integrates with ebay_improved.py API (Port 3004) for advanced eBay listing automation with AI guidance
"""

from uagents import Agent, Context
import requests
import time
import sys
import os
sys.path.append(os.path.dirname(__file__))
from typing import Optional, Dict, Any
from api_message_models import (
    ListingRequest,
    ListingCreationResult,
    ListingResult
)

# eBay Improved Listing Agent Configuration
EBAY_IMPROVED_API_URL = "http://localhost:3004"

# Create the eBay Improved Listing Agent (Mailbox enabled)
ebay_improved_agent = Agent(
    name="ebay_improved_listing_agent",
    seed="ebay_improved_listing_agent_seed_decluttered_api",
    port=8013,
    mailbox=True
)

class EbayImprovedState:
    def __init__(self):
        self.api_healthy = False
        self.ebay_logged_in = False
        self.gemini_available = False
        self.requests_processed = 0
        self.last_health_check = 0

ebay_state = EbayImprovedState()


async def check_api_health() -> Dict[str, Any]:
    """Check if the eBay Improved API is healthy and ready."""
    try:
        response = requests.get(f"{EBAY_IMPROVED_API_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            return {
                "healthy": health_data.get("status") == "OK",
                "browser_ready": health_data.get("browser_ready", False),
                "ebay_logged_in": health_data.get("ebay_logged_in", False),
                "gemini_available": health_data.get("gemini_available", False),
                "version": health_data.get("version", "Unknown")
            }
        return {"healthy": False}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


@ebay_improved_agent.on_event("startup")
async def setup_ebay_improved(ctx: Context):
    """Initialize and check eBay Improved API connection."""
    ctx.logger.info("[EBAY_IMPROVED] eBay Improved Listing Agent starting up...")

    # Check API health
    health_status = await check_api_health()
    ebay_state.api_healthy = health_status.get("healthy", False)
    ebay_state.ebay_logged_in = health_status.get("ebay_logged_in", False)
    ebay_state.gemini_available = health_status.get("gemini_available", False)
    ebay_state.last_health_check = time.time()

    if ebay_state.api_healthy:
        ctx.logger.info("[EBAY_IMPROVED] Successfully connected to eBay Improved API")
        ctx.logger.info(f"[EBAY_IMPROVED] Version: {health_status.get('version', 'Unknown')}")
        ctx.logger.info(f"[EBAY_IMPROVED] eBay logged in: {ebay_state.ebay_logged_in}")
        ctx.logger.info(f"[EBAY_IMPROVED] Gemini available: {ebay_state.gemini_available}")
    else:
        ctx.logger.warning("[EBAY_IMPROVED] Could not connect to eBay Improved API - will retry")


@ebay_improved_agent.on_message(model=ListingRequest)
async def process_ebay_improved_listing(ctx: Context, sender: str, msg: ListingRequest):
    """Process eBay listing creation using the improved API with AI guidance."""
    ctx.logger.info(f"[EBAY_IMPROVED] Creating eBay listing for '{msg.product.name}' using AI-guided automation")

    # Check API health if it's been a while
    current_time = time.time()
    if current_time - ebay_state.last_health_check > 300:  # 5 minutes
        health_status = await check_api_health()
        ebay_state.api_healthy = health_status.get("healthy", False)
        ebay_state.ebay_logged_in = health_status.get("ebay_logged_in", False)
        ebay_state.gemini_available = health_status.get("gemini_available", False)
        ebay_state.last_health_check = current_time

    if not ebay_state.api_healthy:
        ctx.logger.error("[EBAY_IMPROVED] API not healthy, checking status...")
        health_status = await check_api_health()
        ebay_state.api_healthy = health_status.get("healthy", False)

        if not ebay_state.api_healthy:
            # Send error response
            error_result = ListingCreationResult(
                session_id=msg.session_id,
                request_id=msg.request_id,
                success=False,
                error_message="eBay Improved API is not available"
            )
            await ctx.send(sender, error_result)
            return

    # Filter to only eBay platform
    if "ebay" not in msg.platforms:
        ctx.logger.warning("[EBAY_IMPROVED] Request does not include eBay platform, ignoring")
        return

    try:
        # Prepare API request
        api_payload = {
            "product": {
                "name": msg.product.name,
                "condition": msg.product.condition,
                "category": msg.product.category
            },
            "pricing_data": msg.pricing_data
        }

        ctx.logger.info("[EBAY_IMPROVED] Sending request to eBay Improved API with AI guidance...")

        # Make API call with extended timeout for eBay automation
        response = requests.post(
            f"{EBAY_IMPROVED_API_URL}/api/ebay/listing",
            json=api_payload,
            timeout=300,  # Allow up to 5 minutes for eBay automation (includes verification steps)
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            api_data = response.json()

            if api_data.get("ok", False):
                data = api_data.get("data", {})

                # Create listing result
                listing_result = ListingResult(
                    platform="ebay",
                    success=data.get("success", False),
                    status=data.get("status"),
                    listing_url=data.get("current_url"),
                    listing_id=None,  # eBay API might not return listing ID immediately
                    message=data.get("message")
                )

                ctx.logger.info(f"[EBAY_IMPROVED] eBay listing result: {data.get('message', 'Unknown status')}")

                # Create successful result
                result = ListingCreationResult(
                    session_id=msg.session_id,
                    request_id=msg.request_id,
                    success=listing_result.success,
                    listings=[listing_result],
                    listing_data=api_data.get("listing_data"),
                    summary={
                        "platforms_attempted": 1,
                        "successful_listings": 1 if listing_result.success else 0,
                        "failed_listings": 0 if listing_result.success else 1,
                        "method": data.get("method", "ai_guided_completion"),
                        "steps_completed": data.get("steps_completed", 0)
                    }
                )

                # Send result back to sender
                await ctx.send(sender, result)

                ebay_state.requests_processed += 1

            else:
                # API returned ok: false
                error_msg = api_data.get("message", "Unknown API error")
                ctx.logger.error(f"[EBAY_IMPROVED] API error: {error_msg}")

                error_result = ListingCreationResult(
                    session_id=msg.session_id,
                    request_id=msg.request_id,
                    success=False,
                    error_message=f"eBay listing failed: {error_msg}"
                )
                await ctx.send(sender, error_result)

        else:
            # HTTP error
            ctx.logger.error(f"[EBAY_IMPROVED] API HTTP error: {response.status_code}")

            try:
                error_details = response.json()
                error_msg = error_details.get("message", f"HTTP {response.status_code}")
            except:
                error_msg = f"HTTP {response.status_code}"

            error_result = ListingCreationResult(
                session_id=msg.session_id,
                request_id=msg.request_id,
                success=False,
                error_message=f"eBay API HTTP error: {error_msg}"
            )
            await ctx.send(sender, error_result)

    except requests.exceptions.Timeout:
        ctx.logger.error("[EBAY_IMPROVED] API request timed out (eBay automation can take several minutes)")

        error_result = ListingCreationResult(
            session_id=msg.session_id,
            request_id=msg.request_id,
            success=False,
            error_message="eBay listing request timed out (automation process may still be running)"
        )
        await ctx.send(sender, error_result)

    except Exception as e:
        ctx.logger.error(f"[EBAY_IMPROVED] Error processing request: {e}")

        error_result = ListingCreationResult(
            session_id=msg.session_id,
            request_id=msg.request_id,
            success=False,
            error_message=f"Processing error: {str(e)}"
        )
        await ctx.send(sender, error_result)


@ebay_improved_agent.on_interval(period=600.0)  # Every 10 minutes
async def health_check_interval(ctx: Context):
    """Periodic health check of the eBay Improved API."""
    health_status = await check_api_health()
    ebay_state.api_healthy = health_status.get("healthy", False)
    ebay_state.ebay_logged_in = health_status.get("ebay_logged_in", False)
    ebay_state.gemini_available = health_status.get("gemini_available", False)
    ebay_state.last_health_check = time.time()

    if ebay_state.api_healthy:
        ctx.logger.info(f"[EBAY_IMPROVED] Health check passed - Processed {ebay_state.requests_processed} requests")
        ctx.logger.info(f"[EBAY_IMPROVED] eBay logged in: {ebay_state.ebay_logged_in}, Gemini available: {ebay_state.gemini_available}")
    else:
        ctx.logger.warning("[EBAY_IMPROVED] Health check failed - API not available")


@ebay_improved_agent.on_event("shutdown")
async def cleanup_ebay_improved(ctx: Context):
    """Cleanup on shutdown."""
    ctx.logger.info("[EBAY_IMPROVED] eBay Improved Listing Agent shutting down")


if __name__ == "__main__":
    print("[EBAY_IMPROVED] Starting eBay Improved Listing Agent...")
    print("[EBAY_IMPROVED] Connecting to API at http://localhost:3004")
    print("[EBAY_IMPROVED] Waiting for ListingRequest messages...")
    ebay_improved_agent.run()