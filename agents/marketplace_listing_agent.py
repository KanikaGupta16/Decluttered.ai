"""
Marketplace Listing Agent for Decluttered.ai
Integrates with listing.py API (Port 3003) for Facebook/eBay marketplace listing creation
"""

from uagents import Agent, Context
import requests
import time
import sys
import os
sys.path.append(os.path.dirname(__file__))
from typing import Optional, List, Dict, Any
from api_message_models import (
    ListingRequest,
    ListingCreationResult,
    ListingResult,
    FacebookLoginRequest,
    FacebookLoginResult
)

# Marketplace Listing Agent Configuration
MARKETPLACE_LISTING_API_URL = "http://localhost:3003"
EBAY_IMPROVED_ADDRESS = "agent1qz5c8v7n2m4w1r9k6t3y8x4p2j7h5u9s1e6q0o4i8a3d5f2g7n4j6b9l3m5k"

# Create the Marketplace Listing Agent (Mailbox enabled)
marketplace_listing_agent = Agent(
    name="marketplace_listing_agent",
    seed="marketplace_listing_agent_seed_decluttered_api",
    port=8012,
    mailbox=True
)

class MarketplaceListingState:
    def __init__(self):
        self.api_healthy = False
        self.facebook_logged_in = False
        self.ebay_configured = False
        self.gemini_available = False
        self.requests_processed = 0
        self.last_health_check = 0

listing_state = MarketplaceListingState()


async def check_api_health() -> Dict[str, Any]:
    """Check if the Marketplace Listing API is healthy and ready."""
    try:
        response = requests.get(f"{MARKETPLACE_LISTING_API_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            return {
                "healthy": health_data.get("status") == "OK",
                "browser_ready": health_data.get("browser_ready", False),
                "facebook_logged_in": health_data.get("facebook_logged_in", False),
                "ebay_configured": health_data.get("ebay_configured", False),
                "gemini_available": health_data.get("gemini_available", False)
            }
        return {"healthy": False}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def initiate_facebook_login() -> bool:
    """Attempt to log into Facebook for marketplace access."""
    try:
        response = requests.post(f"{MARKETPLACE_LISTING_API_URL}/api/facebook/login", json={}, timeout=30)
        if response.status_code == 200:
            login_data = response.json()
            return login_data.get("ok", False) and login_data.get("logged_in", False)
        return False
    except Exception as e:
        return False


@marketplace_listing_agent.on_event("startup")
async def setup_marketplace_listing(ctx: Context):
    """Initialize and check Marketplace Listing API connection."""
    ctx.logger.info("[MARKETPLACE_LISTING] Marketplace Listing Agent starting up...")

    # Check API health
    health_status = await check_api_health()
    listing_state.api_healthy = health_status.get("healthy", False)
    listing_state.facebook_logged_in = health_status.get("facebook_logged_in", False)
    listing_state.ebay_configured = health_status.get("ebay_configured", False)
    listing_state.gemini_available = health_status.get("gemini_available", False)
    listing_state.last_health_check = time.time()

    if listing_state.api_healthy:
        ctx.logger.info("[MARKETPLACE_LISTING] Successfully connected to Marketplace Listing API")
        ctx.logger.info(f"[MARKETPLACE_LISTING] Facebook logged in: {listing_state.facebook_logged_in}")
        ctx.logger.info(f"[MARKETPLACE_LISTING] eBay configured: {listing_state.ebay_configured}")
        ctx.logger.info(f"[MARKETPLACE_LISTING] Gemini available: {listing_state.gemini_available}")
    else:
        ctx.logger.warning("[MARKETPLACE_LISTING] Could not connect to Marketplace Listing API - will retry")


@marketplace_listing_agent.on_message(model=FacebookLoginRequest)
async def handle_facebook_login_request(ctx: Context, sender: str, msg: FacebookLoginRequest):
    """Handle Facebook login requests from other agents."""
    ctx.logger.info(f"[MARKETPLACE_LISTING] Facebook login requested by {msg.agent_id}")

    success = await initiate_facebook_login()

    if success:
        listing_state.facebook_logged_in = True
        ctx.logger.info("[MARKETPLACE_LISTING] Facebook login successful")
    else:
        ctx.logger.error("[MARKETPLACE_LISTING] Facebook login failed")

    # Send response back
    login_result = FacebookLoginResult(
        success=success,
        logged_in=success,
        message="Facebook login successful" if success else "Facebook login failed",
        agent_id=msg.agent_id,
        session_id=msg.session_id
    )

    await ctx.send(sender, login_result)


@marketplace_listing_agent.on_message(model=ListingRequest)
async def process_listing_creation(ctx: Context, sender: str, msg: ListingRequest):
    """Process listing creation request using the external API."""
    ctx.logger.info(f"[MARKETPLACE_LISTING] Creating listings for '{msg.product.name}' on platforms {msg.platforms}")

    # Check API health if it's been a while
    current_time = time.time()
    if current_time - listing_state.last_health_check > 300:  # 5 minutes
        health_status = await check_api_health()
        listing_state.api_healthy = health_status.get("healthy", False)
        listing_state.facebook_logged_in = health_status.get("facebook_logged_in", False)
        listing_state.ebay_configured = health_status.get("ebay_configured", False)
        listing_state.last_health_check = current_time

    if not listing_state.api_healthy:
        ctx.logger.error("[MARKETPLACE_LISTING] API not healthy, checking status...")
        health_status = await check_api_health()
        listing_state.api_healthy = health_status.get("healthy", False)

        if not listing_state.api_healthy:
            # Send error response
            error_result = ListingCreationResult(
                session_id=msg.session_id,
                request_id=msg.request_id,
                success=False,
                error_message="Marketplace Listing API is not available"
            )
            await ctx.send(sender, error_result)
            return

    # Check platform availability and login status
    available_platforms = []

    for platform in msg.platforms:
        if platform == "facebook":
            if not listing_state.facebook_logged_in:
                ctx.logger.info("[MARKETPLACE_LISTING] Facebook login required, attempting login...")
                login_success = await initiate_facebook_login()
                listing_state.facebook_logged_in = login_success

                if login_success:
                    available_platforms.append(platform)
                else:
                    ctx.logger.warning("[MARKETPLACE_LISTING] Facebook login failed, skipping Facebook listings")
            else:
                available_platforms.append(platform)

        elif platform == "ebay":
            if listing_state.ebay_configured:
                # For eBay, we'll use the improved API instead of this one
                ctx.logger.info("[MARKETPLACE_LISTING] eBay detected, will delegate to eBay Improved Agent")
                # Still add to available_platforms to create the basic listing first
                available_platforms.append(platform)
            else:
                ctx.logger.warning("[MARKETPLACE_LISTING] eBay not configured, skipping eBay listings")
        else:
            ctx.logger.warning(f"[MARKETPLACE_LISTING] Unknown platform '{platform}', skipping")

    if not available_platforms:
        error_result = ListingCreationResult(
            session_id=msg.session_id,
            request_id=msg.request_id,
            success=False,
            error_message="No available platforms for listing (login/configuration issues)"
        )
        await ctx.send(sender, error_result)
        return

    try:
        # Prepare API request
        api_payload = {
            "product": {
                "name": msg.product.name,
                "condition": msg.product.condition,
                "category": msg.product.category
            },
            "pricing_data": msg.pricing_data,
            "platforms": available_platforms,
            "images": msg.images
        }

        ctx.logger.info(f"[MARKETPLACE_LISTING] Creating listings on platforms: {available_platforms}")

        # Make API call with timeout
        response = requests.post(
            f"{MARKETPLACE_LISTING_API_URL}/api/listings/create",
            json=api_payload,
            timeout=180,  # Allow up to 3 minutes for listing creation
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            api_data = response.json()

            if api_data.get("ok", False):
                data = api_data.get("data", {})

                # Convert listings to our model
                listings = []
                listings_data = data.get("listings", {})

                for platform, listing_info in listings_data.items():
                    listing_result = ListingResult(
                        platform=listing_info.get("platform", platform),
                        success=listing_info.get("success", False),
                        status=listing_info.get("status"),
                        listing_url=listing_info.get("listing_url"),
                        listing_id=listing_info.get("listing_id"),
                        message=listing_info.get("message"),
                        error_message=listing_info.get("error_message")
                    )
                    listings.append(listing_result)

                ctx.logger.info(f"[MARKETPLACE_LISTING] Created {len(listings)} listings")

                # Create successful result
                result = ListingCreationResult(
                    session_id=msg.session_id,
                    request_id=msg.request_id,
                    success=True,
                    listings=listings,
                    listing_data=data.get("listing_data"),
                    summary=data.get("summary")
                )

                # Send result back to sender
                await ctx.send(sender, result)

                # If eBay was requested and we have pricing data, delegate to eBay Improved Agent
                if "ebay" in msg.platforms and msg.pricing_data:
                    ctx.logger.info("[MARKETPLACE_LISTING] Delegating eBay listing to eBay Improved Agent")

                    # Create a new request for the eBay Improved Agent
                    ebay_request = ListingRequest(
                        product=msg.product,
                        pricing_data=msg.pricing_data,
                        platforms=["ebay"],  # Only eBay
                        images=msg.images,
                        session_id=msg.session_id,
                        request_id=f"{msg.request_id}_ebay_improved"
                    )

                    # Send to eBay Improved Agent
                    await ctx.send(EBAY_IMPROVED_ADDRESS, ebay_request)

                listing_state.requests_processed += 1

            else:
                # API returned ok: false
                error_msg = api_data.get("message", "Unknown API error")
                ctx.logger.error(f"[MARKETPLACE_LISTING] API error: {error_msg}")

                error_result = ListingCreationResult(
                    session_id=msg.session_id,
                    request_id=msg.request_id,
                    success=False,
                    error_message=f"Listing creation failed: {error_msg}"
                )
                await ctx.send(sender, error_result)

        else:
            # HTTP error
            ctx.logger.error(f"[MARKETPLACE_LISTING] API HTTP error: {response.status_code}")

            error_result = ListingCreationResult(
                session_id=msg.session_id,
                request_id=msg.request_id,
                success=False,
                error_message=f"API HTTP error: {response.status_code}"
            )
            await ctx.send(sender, error_result)

    except requests.exceptions.Timeout:
        ctx.logger.error("[MARKETPLACE_LISTING] API request timed out")

        error_result = ListingCreationResult(
            session_id=msg.session_id,
            request_id=msg.request_id,
            success=False,
            error_message="Listing creation request timed out"
        )
        await ctx.send(sender, error_result)

    except Exception as e:
        ctx.logger.error(f"[MARKETPLACE_LISTING] Error processing request: {e}")

        error_result = ListingCreationResult(
            session_id=msg.session_id,
            request_id=msg.request_id,
            success=False,
            error_message=f"Processing error: {str(e)}"
        )
        await ctx.send(sender, error_result)


@marketplace_listing_agent.on_interval(period=600.0)  # Every 10 minutes
async def health_check_interval(ctx: Context):
    """Periodic health check of the Marketplace Listing API."""
    health_status = await check_api_health()
    listing_state.api_healthy = health_status.get("healthy", False)
    listing_state.facebook_logged_in = health_status.get("facebook_logged_in", False)
    listing_state.ebay_configured = health_status.get("ebay_configured", False)
    listing_state.gemini_available = health_status.get("gemini_available", False)
    listing_state.last_health_check = time.time()

    if listing_state.api_healthy:
        ctx.logger.info(f"[MARKETPLACE_LISTING] Health check passed - Processed {listing_state.requests_processed} requests")
        ctx.logger.info(f"[MARKETPLACE_LISTING] Facebook: {listing_state.facebook_logged_in}, eBay: {listing_state.ebay_configured}, Gemini: {listing_state.gemini_available}")
    else:
        ctx.logger.warning("[MARKETPLACE_LISTING] Health check failed - API not available")


@marketplace_listing_agent.on_event("shutdown")
async def cleanup_marketplace_listing(ctx: Context):
    """Cleanup on shutdown."""
    ctx.logger.info("[MARKETPLACE_LISTING] Marketplace Listing Agent shutting down")


if __name__ == "__main__":
    print("[MARKETPLACE_LISTING] Starting Marketplace Listing Agent...")
    print("[MARKETPLACE_LISTING] Connecting to API at http://localhost:3003")
    print("[MARKETPLACE_LISTING] Waiting for ListingRequest messages...")
    marketplace_listing_agent.run()