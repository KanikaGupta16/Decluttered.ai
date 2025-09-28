# Decluttered.ai API Documentation

## Overview
This documentation covers four main APIs that work together to provide a complete product recognition, pricing, and marketplace listing solution:

1. **Image Recognition API** (`main.py`) - Port 3001
2. **Price Scraper API** (`scraper.py`) - Port 3002  
3. **Marketplace Listing API** (`listing.py`) - Port 3003
4. **eBay Improved Listing API** (`ebay_improved.py`) - Port 3004

---

## 1. Image Recognition API (main.py) - Port 3001

### Base URL
- **Local**: `http://localhost:3001`
- **Public**: `https://your-ngrok-url.ngrok-free.app`

### Features
- Google reverse image search using Selenium
- Product name extraction with AI enhancement
- Pricing data extraction from Google Shopping
- Rating and review count extraction
- Fast mode with cookie persistence (no login required)

### Endpoints

#### GET `/health`
Health check endpoint to verify API status.

**Response:**
```json
{
  "status": "OK",
  "service": "fast_image_recognition", 
  "timestamp": "2025-09-28T12:00:00",
  "browser_ready": true,
  "login_check_skipped": true,
  "cookies_preserved": true
}
```

#### POST `/api/recognition/basic`
Main image recognition endpoint that processes images and returns product information.

**Content-Type Options:**
1. `multipart/form-data` (for file uploads)
2. `application/json` (for base64 encoded images)

**Request Body (File Upload):**
```bash
curl -X POST http://localhost:3001/api/recognition/basic \
  -F "image=@/path/to/image.jpg"
```

**Request Body (JSON with Base64):**
```json
{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD..."
}
```

**Response (Success):**
```json
{
  "ok": true,
  "data": {
    "product_name": "Anker Soundcore Liberty 4 NC Wireless Earbuds",
    "source_url": "https://amazon.com/product-url",
    "host": "amazon.com",
    "pricing": {
      "current_prices": [
        {
          "price": 59.99,
          "currency": "USD",
          "source": "shopping_result"
        }
      ],
      "typical_price_range": {
        "min": 45.00,
        "max": 79.99,
        "currency": "USD",
        "text": "Typically $45-$79"
      }
    },
    "rating": {
      "rating": 4.3,
      "rating_out_of": 5.0,
      "review_count": 2847,
      "review_count_text": "(2,847)"
    }
  },
  "diagnostics": {
    "provider": "google_fast_mode_cookies",
    "vision_ms": 3500,
    "login_skipped": true
  }
}
```

**Error Responses:**
- `400 Bad Request`: Missing image, image too large (>10MB)
- `500 Internal Server Error`: Search failed, processing error

---

## 2. Price Scraper API (scraper.py) - Port 3002

### Base URL
- **Local**: `http://localhost:3002`
- **Public**: `https://your-ngrok-url.ngrok-free.app`

### Features
- Facebook Marketplace scraping (requires login)
- eBay sold listings scraping
- Semantic product matching with Gemini AI
- Price statistics and market analysis
- Multi-platform search capabilities

### Endpoints

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "OK",
  "service": "marketplace_price_scraper",
  "timestamp": "2025-09-28T12:00:00",
  "browser_ready": true,
  "facebook_logged_in": false,
  "semantic_matching": true,
  "version": "2.0.0"
}
```

#### POST `/api/facebook/login`
Initiates Facebook login process for Marketplace access.

**Request Body:**
```json
{}
```

**Response (Success):**
```json
{
  "ok": true,
  "message": "Facebook login successful",
  "logged_in": true
}
```

#### POST `/api/prices`
**Main endpoint** - Gets market prices for a product across multiple platforms.

**Request Body:**
```json
{
  "name": "Anker Soundcore Liberty 4 NC",
  "platforms": ["facebook", "ebay"],
  "condition_filter": "all"
}
```

**Parameters:**
- `name` (required): Product name to search for
- `platforms` (optional): Array of platforms to search. Options: `["facebook", "ebay"]`. Default: `["facebook", "ebay"]`
- `condition_filter` (optional): Filter by condition. Options: `"all"`, `"new"`, `"used"`, `"good"`, `"fair"`. Default: `"all"`

**Response (Success):**
```json
{
  "ok": true,
  "data": {
    "query": "Anker Soundcore Liberty 4 NC",
    "comps": [
      {
        "platform": "facebook",
        "title": "Anker Soundcore Liberty 4 NC Earbuds",
        "price": 45.00,
        "condition": "used",
        "location": "San Francisco, CA",
        "url": "https://facebook.com/marketplace/item/...",
        "image_url": "https://...",
        "posted_date": "2 days ago",
        "semantic_match_score": 0.92
      },
      {
        "platform": "ebay",
        "title": "Anker Liberty 4 NC Wireless Earbuds - Black",
        "price": 52.99,
        "condition": "used",
        "sold_date": "Sep 25, 2025",
        "url": "https://ebay.com/itm/...",
        "shipping": "Free shipping"
      }
    ],
    "summary": {
      "total_listings": 15,
      "price_range": {
        "min": 35.00,
        "max": 65.00,
        "average": 48.50,
        "median": 47.00
      },
      "condition_breakdown": {
        "new": 2,
        "used": 13
      },
      "platform_breakdown": {
        "facebook": 8,
        "ebay": 7
      }
    },
    "currency": "USD",
    "total_found": 15,
    "good_matches": 12,
    "condition_filter": "all",
    "platforms_searched": ["facebook", "ebay"],
    "platform_results": {
      "facebook": {
        "found": 8,
        "success": true
      },
      "ebay": {
        "found": 7, 
        "success": true
      }
    }
  },
  "diagnostics": {
    "execution_time_ms": 8500,
    "semantic_matching": true,
    "provider": "marketplace_scraper_v2"
  }
}
```

#### GET `/api/test`
Test endpoint with sample product search.

---

## 3. Marketplace Listing API (listing.py) - Port 3003

### Base URL
- **Local**: `http://localhost:3003`
- **Public**: `https://your-ngrok-url.ngrok-free.app`

### Features
- Facebook Marketplace listing automation
- eBay API integration for listings
- AI-generated product descriptions
- Intelligent pricing based on market data
- Multi-platform listing creation

### Endpoints

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "OK",
  "service": "marketplace_listing_api",
  "timestamp": "2025-09-28T12:00:00",
  "browser_ready": true,
  "facebook_logged_in": false,
  "gemini_available": true,
  "ebay_configured": true,
  "version": "1.0.0"
}
```

#### POST `/api/facebook/login`
Initiates Facebook login process.

#### POST `/api/listings/create`
**Main endpoint** - Creates marketplace listings on multiple platforms.

**Request Body:**
```json
{
  "product": {
    "name": "Anker Soundcore Liberty 4 NC Wireless Earbuds",
    "condition": "used",
    "category": "Electronics"
  },
  "pricing_data": {
    "comps": [
      {
        "platform": "facebook",
        "price": 45.00,
        "condition": "used"
      }
    ],
    "summary": {
      "average": 48.50,
      "median": 47.00
    }
  },
  "platforms": ["facebook", "ebay"],
  "images": ["base64_image_data_optional"]
}
```

**Parameters:**
- `product` (required): Product information object
  - `name` (required): Product name
  - `condition` (required): Product condition (`"new"`, `"used"`, `"good"`, `"fair"`)
  - `category` (optional): Product category. Default: `"Electronics"`
- `pricing_data` (required): Pricing data from scraper API
- `platforms` (optional): Platforms to list on. Options: `["facebook", "ebay"]`. Default: `["facebook", "ebay"]`
- `images` (optional): Array of base64 encoded images

**Response (Success):**
```json
{
  "ok": true,
  "data": {
    "listings": {
      "facebook": {
        "success": true,
        "platform": "facebook",
        "status": "published",
        "listing_url": "https://facebook.com/marketplace/item/...",
        "message": "Facebook listing created successfully!"
      },
      "ebay": {
        "success": true,
        "platform": "ebay", 
        "status": "active",
        "listing_id": "123456789",
        "message": "eBay listing created via API!"
      }
    },
    "listing_data": {
      "title": "Anker Soundcore Liberty 4 NC Wireless Earbuds",
      "price": 47.50,
      "condition": "used",
      "description": "High-quality wireless earbuds in excellent used condition..."
    },
    "summary": {
      "platforms_attempted": 2,
      "successful_listings": 2,
      "failed_listings": 0
    }
  },
  "diagnostics": {
    "platforms_attempted": ["facebook", "ebay"],
    "gemini_used": true,
    "provider": "marketplace_listing_api_v1"
  }
}
```

#### POST `/api/listings/facebook`
Creates Facebook Marketplace listing only.

#### POST `/api/listings/ebay`
Creates eBay listing only.

---

## 4. eBay Improved Listing API (ebay_improved.py) - Port 3004

### Base URL
- **Local**: `http://localhost:3004`
- **Public**: `https://your-ngrok-url.ngrok-free.app`

### Features
- Advanced eBay listing automation with Selenium
- AI-powered field completion with Gemini
- Smart required field detection
- Post-listing flow handling (phone verification, etc.)
- LLM-guided navigation through verification steps

### Endpoints

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "OK",
  "service": "ebay_listing_automation_improved",
  "timestamp": "2025-09-28T12:00:00",
  "browser_ready": true,
  "ebay_logged_in": false,
  "gemini_available": true,
  "version": "2.1 - IMPROVED + AI-GUIDED"
}
```

#### POST `/api/ebay/listing`
**Main endpoint** - Creates eBay listing using improved automation with AI guidance.

**Request Body:**
```json
{
  "product": {
    "name": "Anker Soundcore Liberty 4 NC Wireless Earbuds",
    "condition": "used",
    "category": "Electronics"
  },
  "pricing_data": {
    "comps": [
      {
        "platform": "ebay",
        "price": 52.99,
        "condition": "used"
      }
    ],
    "summary": {
      "average": 48.50,
      "median": 47.00
    }
  }
}
```

**Parameters:**
- `product` (required): Product information object
  - `name` (required): Product name (truncated to 80 characters for eBay)
  - `condition` (required): Product condition (`"new"`, `"used"`, `"good"`, `"fair"`)  
  - `category` (optional): Product category. Default: `"Electronics"`
- `pricing_data` (required): Market pricing data for optimal price calculation

**Response (Success):**
```json
{
  "ok": true,
  "data": {
    "success": true,
    "platform": "ebay",
    "status": "completed",
    "message": "eBay listing completed successfully! LLM confirmed listing completion!",
    "current_url": "https://ebay.com/sl/confirmation/...",
    "steps_completed": 3,
    "method": "ai_guided_completion"
  },
  "listing_data": {
    "title": "Anker Soundcore Liberty 4 NC Wireless Earbuds",
    "price": 47.50,
    "condition": "used", 
    "description": "High-quality wireless earbuds in excellent used condition. Features active noise cancellation...",
    "category": "Electronics"
  },
  "diagnostics": {
    "method": "improved_ai_powered",
    "gemini_used": true,
    "focus": "required_fields_only"
  }
}
```

**Unique Features:**
- **AI Field Completion**: Uses Gemini to intelligently fill eBay form fields
- **Required Field Detection**: Focuses only on required fields, ignoring optional ones
- **Post-listing Flow**: Handles verification steps like phone confirmation automatically
- **LLM Navigation**: Uses AI to navigate complex post-listing pages

---

## Integration Workflow

### Complete Product Listing Flow:

1. **Image Recognition** (Port 3001):
   ```bash
   curl -X POST https://your-ngrok-url.ngrok-free.app/api/recognition/basic \
     -F "image=@product.jpg"
   ```

2. **Price Research** (Port 3002):
   ```bash
   curl -X POST https://your-ngrok-url.ngrok-free.app/api/prices \
     -H "Content-Type: application/json" \
     -d '{"name": "Anker Soundcore Liberty 4 NC"}'
   ```

3. **Create Listings** (Port 3003 or 3004):
   ```bash
   curl -X POST https://your-ngrok-url.ngrok-free.app/api/listings/create \
     -H "Content-Type: application/json" \
     -d '{
       "product": {
         "name": "Anker Soundcore Liberty 4 NC",
         "condition": "used"
       },
       "pricing_data": {...}
     }'
   ```

### Error Handling
All APIs follow consistent error response format:

```json
{
  "ok": false,
  "error_code": "SPECIFIC_ERROR_CODE",
  "message": "Human readable error description"
}
```

### Common Error Codes:
- `INVALID_REQUEST`: Malformed request body
- `MISSING_DATA`: Required fields missing
- `SEARCH_ERROR`: External service failure
- `LOGIN_REQUIRED`: Authentication needed
- `INTERNAL_ERROR`: Server-side processing error

### Rate Limiting
- Image Recognition: ~1 request per 5 seconds (Google rate limits)
- Price Scraper: ~1 request per 10 seconds (Anti-detection)
- Listing APIs: ~1 request per 30 seconds (Platform rate limits)

### Authentication Requirements:
- **Facebook**: Manual login required via `/api/facebook/login` endpoints
- **eBay**: Cookie-based authentication through browser automation
- **Google**: Uses persistent cookies, no login required

This comprehensive API suite enables complete automation of the product recognition, pricing research, and marketplace listing workflow.