"""
Price Scraper Agent for Decluttered.ai
Integrates with scraper.py API (Port 3002) for Facebook/eBay marketplace price research
"""

from uagents import Agent, Context
import requests
import time
import sys
import os
sys.path.append(os.path.dirname(__file__))
from typing import Optional, List, Dict, Any
from api_message_models import (
    PriceResearchRequest,
    PriceResearchResult,
    PriceComparison,
    PriceSummary,
    FacebookLoginRequest,
    FacebookLoginResult,
    ListingRequest,
    ProductInfo
)

# Price Scraper Agent Configuration
PRICE_SCRAPER_API_URL = "http://localhost:3002"
MARKETPLACE_LISTING_ADDRESS = "agent1qx7h5k2m9v8w3p4j6n8z2c5f9s7t1y4r6e8q0u2i5o7a3s9d1f2g4h6j8k0"

# Create the Price Scraper Agent (Mailbox enabled)
price_scraper_agent = Agent(
    name="price_scraper_agent",
    seed="price_scraper_agent_seed_decluttered_api",
    port=8011,
    mailbox=True
)

class PriceScraperState:
    def __init__(self):
        self.api_healthy = False
        self.facebook_logged_in = False
        self.requests_processed = 0
        self.last_health_check = 0
        self.login_agents = set()  # Track which agents need FB login

scraper_state = PriceScraperState()


async def check_api_health() -> Dict[str, Any]:
    """Check if the Price Scraper API is healthy and ready."""
    try:
        response = requests.get(f"{PRICE_SCRAPER_API_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            return {
                "healthy": health_data.get("status") == "OK",
                "browser_ready": health_data.get("browser_ready", False),
                "facebook_logged_in": health_data.get("facebook_logged_in", False),
                "semantic_matching": health_data.get("semantic_matching", False)
            }
        return {"healthy": False}
    except Exception as e:
        return {"healthy": False, "error": str(e)}


async def initiate_facebook_login() -> bool:
    """Attempt to log into Facebook for marketplace access."""
    try:
        response = requests.post(f"{PRICE_SCRAPER_API_URL}/api/facebook/login", json={}, timeout=30)
        if response.status_code == 200:
            login_data = response.json()
            return login_data.get("ok", False) and login_data.get("logged_in", False)
        return False
    except Exception as e:
        return False


@price_scraper_agent.on_event("startup")
async def setup_price_scraper(ctx: Context):
    """Initialize and check Price Scraper API connection."""
    ctx.logger.info("[PRICE_SCRAPER] Price Scraper Agent starting up...")

    # Check API health
    health_status = await check_api_health()
    scraper_state.api_healthy = health_status.get("healthy", False)
    scraper_state.facebook_logged_in = health_status.get("facebook_logged_in", False)
    scraper_state.last_health_check = time.time()

    if scraper_state.api_healthy:
        ctx.logger.info("[PRICE_SCRAPER] Successfully connected to Price Scraper API")
        if scraper_state.facebook_logged_in:
            ctx.logger.info("[PRICE_SCRAPER] Facebook already logged in")
        else:
            ctx.logger.info("[PRICE_SCRAPER] Facebook not logged in - will attempt login when needed")
    else:
        ctx.logger.warning("[PRICE_SCRAPER] Could not connect to Price Scraper API - will retry")


@price_scraper_agent.on_message(model=FacebookLoginRequest)
async def handle_facebook_login_request(ctx: Context, sender: str, msg: FacebookLoginRequest):
    """Handle Facebook login requests from other agents."""
    ctx.logger.info(f"[PRICE_SCRAPER] Facebook login requested by {msg.agent_id}")

    # Track which agent needs login
    scraper_state.login_agents.add(msg.agent_id)

    success = await initiate_facebook_login()

    if success:
        scraper_state.facebook_logged_in = True
        ctx.logger.info("[PRICE_SCRAPER] Facebook login successful")
    else:
        ctx.logger.error("[PRICE_SCRAPER] Facebook login failed")

    # Send response back
    login_result = FacebookLoginResult(
        success=success,
        logged_in=success,
        message="Facebook login successful" if success else "Facebook login failed",
        agent_id=msg.agent_id,
        session_id=msg.session_id
    )

    await ctx.send(sender, login_result)


@price_scraper_agent.on_message(model=PriceResearchRequest)
async def process_price_research(ctx: Context, sender: str, msg: PriceResearchRequest):
    """Process price research request using the external API."""
    ctx.logger.info(f"[PRICE_SCRAPER] Processing price research for '{msg.product_name}' from session {msg.session_id}")

    # Check API health if it's been a while
    current_time = time.time()
    if current_time - scraper_state.last_health_check > 300:  # 5 minutes
        health_status = await check_api_health()
        scraper_state.api_healthy = health_status.get("healthy", False)
        scraper_state.facebook_logged_in = health_status.get("facebook_logged_in", False)
        scraper_state.last_health_check = current_time

    if not scraper_state.api_healthy:
        ctx.logger.error("[PRICE_SCRAPER] API not healthy, checking status...")
        health_status = await check_api_health()
        scraper_state.api_healthy = health_status.get("healthy", False)

        if not scraper_state.api_healthy:
            # Send error response
            error_result = PriceResearchResult(
                session_id=msg.session_id,
                request_id=msg.request_id,
                success=False,
                error_message="Price Scraper API is not available"
            )
            await ctx.send(sender, error_result)
            return

    # Check if Facebook login is needed for Facebook platform
    if "facebook" in msg.platforms and not scraper_state.facebook_logged_in:
        ctx.logger.info("[PRICE_SCRAPER] Facebook login required, attempting login...")
        login_success = await initiate_facebook_login()
        scraper_state.facebook_logged_in = login_success

        if not login_success:
            ctx.logger.warning("[PRICE_SCRAPER] Facebook login failed, removing from platforms")
            # Remove facebook from platforms list
            platforms = [p for p in msg.platforms if p != "facebook"]
            if not platforms:
                error_result = PriceResearchResult(
                    session_id=msg.session_id,
                    request_id=msg.request_id,
                    success=False,
                    error_message="No available platforms (Facebook login failed, no other platforms specified)"
                )
                await ctx.send(sender, error_result)
                return
        else:
            platforms = msg.platforms
    else:
        platforms = msg.platforms

    try:
        # Prepare API request
        api_payload = {
            "name": msg.product_name,
            "platforms": platforms,
            "condition_filter": msg.condition_filter
        }

        ctx.logger.info(f"[PRICE_SCRAPER] Searching platforms {platforms} for '{msg.product_name}'...")

        # Make API call with timeout
        response = requests.post(
            f"{PRICE_SCRAPER_API_URL}/api/prices",
            json=api_payload,
            timeout=120,  # Allow up to 2 minutes for scraping
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            api_data = response.json()

            if api_data.get("ok", False):
                data = api_data.get("data", {})

                # Convert comparisons to our model
                comps = []
                for comp_data in data.get("comps", []):
                    comp = PriceComparison(
                        platform=comp_data.get("platform", ""),
                        title=comp_data.get("title", ""),
                        price=comp_data.get("price", 0.0),
                        condition=comp_data.get("condition", ""),
                        location=comp_data.get("location"),
                        url=comp_data.get("url"),
                        image_url=comp_data.get("image_url"),
                        posted_date=comp_data.get("posted_date"),
                        sold_date=comp_data.get("sold_date"),
                        shipping=comp_data.get("shipping"),
                        semantic_match_score=comp_data.get("semantic_match_score")
                    )
                    comps.append(comp)

                # Convert summary
                summary_data = data.get("summary", {})
                summary = PriceSummary(
                    total_listings=summary_data.get("total_listings", 0),
                    price_range=summary_data.get("price_range", {}),
                    condition_breakdown=summary_data.get("condition_breakdown", {}),
                    platform_breakdown=summary_data.get("platform_breakdown", {})
                )

                ctx.logger.info(f"[PRICE_SCRAPER] Found {len(comps)} price comparisons")

                # Create successful result
                result = PriceResearchResult(
                    session_id=msg.session_id,
                    request_id=msg.request_id,
                    success=True,
                    query=data.get("query", msg.product_name),
                    comps=comps,
                    summary=summary,
                    currency=data.get("currency", "USD"),
                    total_found=data.get("total_found", len(comps))
                )

                # Send result back to sender
                await ctx.send(sender, result)

                # If we have good price data, trigger listing creation
                if len(comps) > 0 and summary.total_listings > 0:
                    ctx.logger.info(f"[PRICE_SCRAPER] Triggering listing creation with {len(comps)} comparisons")

                    # Create listing request
                    product_info = ProductInfo(
                        name=msg.product_name,
                        condition="used",  # Default to used, could be made configurable
                        category="Electronics"
                    )

                    # Prepare pricing data in the format expected by listing API
                    pricing_data = {
                        "comps": [comp.dict() for comp in comps],
                        "summary": summary.dict()
                    }

                    listing_request = ListingRequest(
                        product=product_info,
                        pricing_data=pricing_data,
                        platforms=["facebook", "ebay"],  # Default to both platforms
                        images=[],  # No images for now
                        session_id=msg.session_id,
                        request_id=msg.request_id
                    )

                    # Send to Marketplace Listing Agent
                    await ctx.send(MARKETPLACE_LISTING_ADDRESS, listing_request)

                scraper_state.requests_processed += 1

            else:
                # API returned ok: false
                error_msg = api_data.get("message", "Unknown API error")
                ctx.logger.error(f"[PRICE_SCRAPER] API error: {error_msg}")

                error_result = PriceResearchResult(
                    session_id=msg.session_id,
                    request_id=msg.request_id,
                    success=False,
                    error_message=f"Price research failed: {error_msg}"
                )
                await ctx.send(sender, error_result)

        else:
            # HTTP error
            ctx.logger.error(f"[PRICE_SCRAPER] API HTTP error: {response.status_code}")

            error_result = PriceResearchResult(
                session_id=msg.session_id,
                request_id=msg.request_id,
                success=False,
                error_message=f"API HTTP error: {response.status_code}"
            )
            await ctx.send(sender, error_result)

    except requests.exceptions.Timeout:
        ctx.logger.error("[PRICE_SCRAPER] API request timed out")

        error_result = PriceResearchResult(
            session_id=msg.session_id,
            request_id=msg.request_id,
            success=False,
            error_message="Price research request timed out"
        )
        await ctx.send(sender, error_result)

    except Exception as e:
        ctx.logger.error(f"[PRICE_SCRAPER] Error processing request: {e}")

        error_result = PriceResearchResult(
            session_id=msg.session_id,
            request_id=msg.request_id,
            success=False,
            error_message=f"Processing error: {str(e)}"
        )
        await ctx.send(sender, error_result)


@price_scraper_agent.on_interval(period=600.0)  # Every 10 minutes
async def health_check_interval(ctx: Context):
    """Periodic health check of the Price Scraper API."""
    health_status = await check_api_health()
    scraper_state.api_healthy = health_status.get("healthy", False)
    scraper_state.facebook_logged_in = health_status.get("facebook_logged_in", False)
    scraper_state.last_health_check = time.time()

    if scraper_state.api_healthy:
        ctx.logger.info(f"[PRICE_SCRAPER] Health check passed - Processed {scraper_state.requests_processed} requests")
        ctx.logger.info(f"[PRICE_SCRAPER] Facebook login status: {scraper_state.facebook_logged_in}")
    else:
        ctx.logger.warning("[PRICE_SCRAPER] Health check failed - API not available")


@price_scraper_agent.on_event("shutdown")
async def cleanup_price_scraper(ctx: Context):
    """Cleanup on shutdown."""
    ctx.logger.info("[PRICE_SCRAPER] Price Scraper Agent shutting down")


if __name__ == "__main__":
    print("[PRICE_SCRAPER] Starting Price Scraper Agent...")
    print("[PRICE_SCRAPER] Connecting to API at http://localhost:3002")
    print("[PRICE_SCRAPER] Waiting for PriceResearchRequest messages...")
    price_scraper_agent.run()