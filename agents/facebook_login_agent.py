"""
Facebook Login Coordinator Agent for Decluttered.ai
Centralizes Facebook login management for multiple marketplace APIs
"""

from uagents import Agent, Context
import requests
import time
import sys
import os
sys.path.append(os.path.dirname(__file__))
from typing import Dict, Set
from api_message_models import (
    FacebookLoginRequest,
    FacebookLoginResult
)

# Facebook Login Agent Configuration
PRICE_SCRAPER_API_URL = "http://localhost:3002"
MARKETPLACE_LISTING_API_URL = "http://localhost:3003"

# Create the Facebook Login Agent (Mailbox enabled)
facebook_login_agent = Agent(
    name="facebook_login_agent",
    seed="facebook_login_agent_seed_decluttered_api",
    port=8014,
    mailbox=True
)

class FacebookLoginState:
    def __init__(self):
        self.price_scraper_logged_in = False
        self.marketplace_listing_logged_in = False
        self.pending_requests: Dict[str, FacebookLoginRequest] = {}
        self.login_attempts = 0
        self.last_login_attempt = 0
        self.last_status_check = 0

facebook_state = FacebookLoginState()


async def check_facebook_status(api_url: str) -> bool:
    """Check Facebook login status for a specific API."""
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            return health_data.get("facebook_logged_in", False)
        return False
    except Exception:
        return False


async def attempt_facebook_login(api_url: str) -> bool:
    """Attempt Facebook login for a specific API."""
    try:
        response = requests.post(f"{api_url}/api/facebook/login", json={}, timeout=30)
        if response.status_code == 200:
            login_data = response.json()
            return login_data.get("ok", False) and login_data.get("logged_in", False)
        return False
    except Exception:
        return False


@facebook_login_agent.on_event("startup")
async def setup_facebook_login(ctx: Context):
    """Initialize Facebook login status checking."""
    ctx.logger.info("[FACEBOOK_LOGIN] Facebook Login Coordinator Agent starting up...")

    # Check initial login status for both APIs
    facebook_state.price_scraper_logged_in = await check_facebook_status(PRICE_SCRAPER_API_URL)
    facebook_state.marketplace_listing_logged_in = await check_facebook_status(MARKETPLACE_LISTING_API_URL)
    facebook_state.last_status_check = time.time()

    ctx.logger.info(f"[FACEBOOK_LOGIN] Initial status - Price Scraper: {facebook_state.price_scraper_logged_in}")
    ctx.logger.info(f"[FACEBOOK_LOGIN] Initial status - Marketplace Listing: {facebook_state.marketplace_listing_logged_in}")


@facebook_login_agent.on_message(model=FacebookLoginRequest)
async def handle_facebook_login_request(ctx: Context, sender: str, msg: FacebookLoginRequest):
    """Handle Facebook login requests from other agents."""
    ctx.logger.info(f"[FACEBOOK_LOGIN] Facebook login requested by {msg.agent_id} for session {msg.session_id}")

    # Store the request for tracking
    request_key = f"{msg.agent_id}_{msg.session_id}"
    facebook_state.pending_requests[request_key] = msg

    # Check current login status
    current_time = time.time()
    if current_time - facebook_state.last_status_check > 60:  # Check every minute
        facebook_state.price_scraper_logged_in = await check_facebook_status(PRICE_SCRAPER_API_URL)
        facebook_state.marketplace_listing_logged_in = await check_facebook_status(MARKETPLACE_LISTING_API_URL)
        facebook_state.last_status_check = current_time

    # If already logged in somewhere, consider it successful
    if facebook_state.price_scraper_logged_in or facebook_state.marketplace_listing_logged_in:
        ctx.logger.info("[FACEBOOK_LOGIN] Facebook already logged in on at least one API")

        login_result = FacebookLoginResult(
            success=True,
            logged_in=True,
            message="Facebook already logged in",
            agent_id=msg.agent_id,
            session_id=msg.session_id
        )

        await ctx.send(sender, login_result)
        facebook_state.pending_requests.pop(request_key, None)
        return

    # Rate limit login attempts (max 1 per 5 minutes)
    if current_time - facebook_state.last_login_attempt < 300:
        time_remaining = 300 - (current_time - facebook_state.last_login_attempt)
        ctx.logger.warning(f"[FACEBOOK_LOGIN] Rate limited - wait {time_remaining:.0f} seconds before next attempt")

        login_result = FacebookLoginResult(
            success=False,
            logged_in=False,
            message=f"Rate limited - wait {time_remaining:.0f} seconds before next attempt",
            agent_id=msg.agent_id,
            session_id=msg.session_id
        )

        await ctx.send(sender, login_result)
        facebook_state.pending_requests.pop(request_key, None)
        return

    ctx.logger.info("[FACEBOOK_LOGIN] Attempting Facebook login on both APIs...")

    # Try login on Price Scraper API first
    price_scraper_success = await attempt_facebook_login(PRICE_SCRAPER_API_URL)
    facebook_state.price_scraper_logged_in = price_scraper_success

    # Try login on Marketplace Listing API
    marketplace_listing_success = await attempt_facebook_login(MARKETPLACE_LISTING_API_URL)
    facebook_state.marketplace_listing_logged_in = marketplace_listing_success

    facebook_state.last_login_attempt = current_time
    facebook_state.login_attempts += 1

    # Determine overall success
    overall_success = price_scraper_success or marketplace_listing_success

    if overall_success:
        success_apis = []
        if price_scraper_success:
            success_apis.append("Price Scraper")
        if marketplace_listing_success:
            success_apis.append("Marketplace Listing")

        message = f"Facebook login successful on: {', '.join(success_apis)}"
        ctx.logger.info(f"[FACEBOOK_LOGIN] {message}")
    else:
        message = "Facebook login failed on all APIs"
        ctx.logger.error(f"[FACEBOOK_LOGIN] {message}")

    # Send response back
    login_result = FacebookLoginResult(
        success=overall_success,
        logged_in=overall_success,
        message=message,
        agent_id=msg.agent_id,
        session_id=msg.session_id
    )

    await ctx.send(sender, login_result)
    facebook_state.pending_requests.pop(request_key, None)


@facebook_login_agent.on_interval(period=300.0)  # Every 5 minutes
async def status_check_interval(ctx: Context):
    """Periodic status check and cleanup."""
    # Check login status on both APIs
    facebook_state.price_scraper_logged_in = await check_facebook_status(PRICE_SCRAPER_API_URL)
    facebook_state.marketplace_listing_logged_in = await check_facebook_status(MARKETPLACE_LISTING_API_URL)
    facebook_state.last_status_check = time.time()

    ctx.logger.info(f"[FACEBOOK_LOGIN] Status check - Price Scraper: {facebook_state.price_scraper_logged_in}, Marketplace: {facebook_state.marketplace_listing_logged_in}")

    # Clean up old pending requests (older than 10 minutes)
    current_time = time.time()
    old_requests = []
    for request_key, request in facebook_state.pending_requests.items():
        # Since we don't have timestamp in the request, we'll clean up based on tracking
        if len(facebook_state.pending_requests) > 10:  # Arbitrary cleanup threshold
            old_requests.append(request_key)

    for request_key in old_requests[:5]:  # Clean up oldest 5
        facebook_state.pending_requests.pop(request_key, None)

    if facebook_state.login_attempts > 0:
        ctx.logger.info(f"[FACEBOOK_LOGIN] Total login attempts: {facebook_state.login_attempts}")


@facebook_login_agent.on_event("shutdown")
async def cleanup_facebook_login(ctx: Context):
    """Cleanup on shutdown."""
    ctx.logger.info("[FACEBOOK_LOGIN] Facebook Login Coordinator Agent shutting down")
    ctx.logger.info(f"[FACEBOOK_LOGIN] Handled {facebook_state.login_attempts} login attempts")


if __name__ == "__main__":
    print("[FACEBOOK_LOGIN] Starting Facebook Login Coordinator Agent...")
    print("[FACEBOOK_LOGIN] Managing Facebook logins for marketplace APIs")
    print("[FACEBOOK_LOGIN] Waiting for FacebookLoginRequest messages...")
    facebook_login_agent.run()