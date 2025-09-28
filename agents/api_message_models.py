"""
Shared Message Models for API-Based Agents in Decluttered.ai
These models define the communication interface between agents for the full marketplace pipeline
"""

from uagents import Model
from typing import Dict, List, Optional, Any
# Removed pydantic Field import - using basic annotations for uAgents compatibility


# Input Models for Image Recognition
class ImageRecognitionRequest(Model):
    image_base64: str
    session_id: str = ""
    request_id: str = ""


class ImageRecognitionResult(Model):
    session_id: str
    request_id: str
    success: bool
    product_name: Optional[str] = None
    source_url: Optional[str] = None
    host: Optional[str] = None
    pricing: Optional[Dict[str, Any]] = None
    rating: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


# Price Research Models
class PriceResearchRequest(Model):
    product_name: str
    platforms: List[str] = ["facebook", "ebay"]
    condition_filter: str = "all"
    session_id: str
    request_id: str


class PriceComparison(Model):
    platform: str
    title: str
    price: float
    condition: str
    location: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    posted_date: Optional[str] = None
    sold_date: Optional[str] = None
    shipping: Optional[str] = None
    semantic_match_score: Optional[float] = None


class PriceSummary(Model):
    total_listings: int
    price_range: Dict[str, float]  # min, max, average, median
    condition_breakdown: Dict[str, int]
    platform_breakdown: Dict[str, int]


class PriceResearchResult(Model):
    session_id: str
    request_id: str
    success: bool
    query: Optional[str] = None
    comps: List[PriceComparison] = []
    summary: Optional[PriceSummary] = None
    currency: str = "USD"
    total_found: int = 0
    error_message: Optional[str] = None


# Listing Creation Models
class ProductInfo(Model):
    name: str
    condition: str  # "new", "used", "good", "fair"
    category: str = "Electronics"


class ListingRequest(Model):
    product: ProductInfo
    pricing_data: Dict[str, Any]  # From price research result
    platforms: List[str] = ["facebook", "ebay"]
    images: List[str] = []  # Base64 encoded images
    session_id: str
    request_id: str


class ListingResult(Model):
    platform: str
    success: bool
    status: Optional[str] = None
    listing_url: Optional[str] = None
    listing_id: Optional[str] = None
    message: Optional[str] = None
    error_message: Optional[str] = None


class ListingCreationResult(Model):
    session_id: str
    request_id: str
    success: bool
    listings: List[ListingResult] = []
    listing_data: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


# Facebook Login Models
class FacebookLoginRequest(Model):
    agent_id: str
    session_id: str


class FacebookLoginResult(Model):
    success: bool
    logged_in: bool
    message: str
    agent_id: str
    session_id: str


# Status and Health Models
class AgentStatusRequest(Model):
    agent_name: str


class AgentStatusResult(Model):
    agent_name: str
    status: str
    browser_ready: bool
    logged_in_status: Dict[str, bool] = {}  # platform -> logged_in
    additional_info: Dict[str, Any] = {}


# Complete Pipeline Request Model
class CompletePipelineRequest(Model):
    image_base64: str
    target_platforms: List[str] = ["facebook", "ebay"]
    condition_filter: str = "all"
    product_condition: str = "used"  # Condition for listing
    session_id: str


class CompletePipelineResult(Model):
    session_id: str
    success: bool
    steps_completed: List[str] = []
    image_recognition: Optional[ImageRecognitionResult] = None
    price_research: Optional[PriceResearchResult] = None
    listing_creation: Optional[ListingCreationResult] = None
    error_message: Optional[str] = None
    total_execution_time_ms: Optional[int] = None