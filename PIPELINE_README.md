# 🔥 Decluttered.AI - Complete Object Detection & Marketplace Pipeline

## 🌟 Overview

Decluttered.AI is a complete automated system that takes a single image, detects resellable objects, identifies them, finds market prices, and automatically lists them on Facebook Marketplace and eBay.

## ✨ Features

### 🎯 Core Pipeline
- **YOLO v9 Object Detection** - Detects objects in images with high accuracy
- **Gemini AI Filtering** - Intelligently filters for resellable items
- **Google Reverse Image Search** - Identifies products automatically  
- **Market Price Analysis** - Scrapes Facebook Marketplace & eBay for comparable prices
- **Automated Listing** - Posts to Facebook Marketplace and eBay automatically
- **Database Storage** - Stores all data in Supabase for tracking

### 🚀 Workflow
```
📸 Single Image → 🎯 Object Detection → ✂️ Crop Objects → 🔍 Product Recognition 
                ↓
💰 Price Research → 📝 Generate Listings → 🏪 Post to Marketplaces → 💾 Save to Database
```

## 📁 Project Structure

```
Decluttered.ai/
├── 🔥 object_detection_pipeline.py    # Main integrated pipeline
├── 📷 OD.py                          # Entry point (calls new pipeline)
├── ⚙️ setup_pipeline.py               # Setup script
├── 📋 requirements.txt               # Python dependencies
├── 🤖 gemini_ACCESS.py              # Gemini AI integration
├── 🧠 yolov9c.pt                    # YOLO model file
├── apps/api/                        # API servers
│   ├── 🔍 main.py                   # Recognition API (port 3001)
│   ├── 💰 scraper.py                # Price scraping API (port 3002) 
│   ├── 📘 listing.py                # Facebook listing API (port 3003)
│   └── 🔨 ebay_improved.py          # eBay listing API (port 3004)
├── frontend/                        # Next.js dashboard
└── cropped_resellables/            # Output folder for detected objects
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Run the setup script
python setup_pipeline.py

# Or install manually
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file with:
```env
# Gemini AI (Required for smart object filtering)
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase Database (Optional - for data storage)
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# eBay API (Optional - for eBay listings)
EBAY_APP_ID=your_ebay_app_id
EBAY_CERT_ID=your_ebay_cert_id
EBAY_DEV_ID=your_ebay_dev_id
EBAY_USER_TOKEN=your_ebay_user_token
```

### 3. Start API Servers (in separate terminals)
```bash
# Terminal 1: Recognition API
cd apps/api && python main.py

# Terminal 2: Price Scraping API  
cd apps/api && python scraper.py

# Terminal 3: Facebook Listing API
cd apps/api && python listing.py

# Terminal 4: eBay Listing API
cd apps/api && python ebay_improved.py
```

### 4. Run the Pipeline
```bash
# Process a single image through complete pipeline
python object_detection_pipeline.py

# Or use the legacy entry point
python OD.py
```

## 🔧 API Endpoints

| Service | Port | Endpoint | Purpose |
|---------|------|----------|---------|
| Recognition | 3001 | `/api/recognition/basic` | Product identification |
| Scraper | 3002 | `/api/prices` | Market price analysis |
| Facebook | 3003 | `/api/facebook/listing` | Facebook Marketplace listing |
| eBay | 3004 | `/api/ebay/listing` | eBay listing automation |

## 💾 Database Schema

### Photos Table
```sql
- id: UUID (Primary Key)
- filename: TEXT
- url: TEXT (Supabase storage URL)
- size: BIGINT
- processed: BOOLEAN
- uploaded_at: TIMESTAMP
```

### Cropped Objects Table  
```sql
- id: UUID (Primary Key)
- photo_id: UUID (Foreign Key)
- object_name: TEXT
- confidence: DECIMAL
- bounding_box: JSONB
- cropped_image_url: TEXT
- estimated_value: DECIMAL
```

### Listings Table
```sql
- id: UUID (Primary Key) 
- photo_id: UUID (Foreign Key)
- cropped_id: UUID (Foreign Key)
- title: TEXT
- description: TEXT
- price: DECIMAL
- platforms: TEXT[] (facebook, ebay)
- status: TEXT (draft, posted, sold)
- facebook_post_id: TEXT
- ebay_listing_id: TEXT
- posted_at: TIMESTAMP
```

## 🎯 How It Works

### Step 1: Object Detection
- Uses YOLO v9 to detect objects in the image
- Filters for the largest instance of each object type
- Crops objects with intelligent borders

### Step 2: AI Filtering  
- Sends image + detected objects to Gemini AI
- Filters for items that are actually resellable
- Focuses on electronics, devices, and valuable items

### Step 3: Product Recognition
- Calls Google reverse image search API
- Identifies specific product names and models
- Extracts pricing and rating information

### Step 4: Market Research
- Scrapes Facebook Marketplace for comparable listings
- Searches eBay sold listings for market data
- Calculates optimal pricing using statistics

### Step 5: Listing Generation
- Uses Gemini AI to generate compelling descriptions
- Creates listings optimized for each platform
- Handles platform-specific requirements

### Step 6: Automated Posting
- **Facebook**: Selenium automation with login persistence
- **eBay**: Enhanced form filling with required field detection
- Handles verification steps and confirmation dialogs

## 📊 Sample Output

```
🔥 DECLUTTERED.AI - COMPLETE PIPELINE REPORT
==================================================
Timestamp: 2024-01-15T10:30:00
Image: my_desk_photo.jpg
Objects detected: 3
Total estimated value: $247.50

OBJECT 1: laptop
  Identified as: MacBook Air M1 13-inch
  Market research: 24 comparables  
  Average market price: $650.00
  Estimated value: $599.00
  Facebook listing: Success
  eBay listing: Success

OBJECT 2: mouse
  Identified as: Logitech MX Master 3
  Market research: 18 comparables
  Average market price: $85.00
  Estimated value: $78.50
  Facebook listing: Success
  eBay listing: Success
```

## 🛠️ Advanced Configuration

### Custom Object Classes
Modify the resellable categories in `object_detection_pipeline.py`:
```python
resellable_categories = [
    'laptop', 'computer', 'phone', 'tablet',
    'camera', 'headphones', 'speaker', 'watch'
    # Add your custom categories
]
```

### Pricing Strategy
Adjust pricing calculation in `calculate_optimal_price()`:
```python
# Current: 5% below median for competitive pricing
optimal_price = median_price * 0.95

# More aggressive: 10% below median
optimal_price = median_price * 0.90
```

### Platform Selection
Choose which platforms to use:
```python
platforms = ["facebook", "ebay"]  # Both
platforms = ["facebook"]         # Facebook only  
platforms = ["ebay"]             # eBay only
```

## 🔒 Security & Privacy

- Uses persistent browser profiles for login cookies
- No credentials stored in code - uses environment variables
- Images stored securely in Supabase with public URLs
- Anti-detection measures for web scraping

## 🐛 Troubleshooting

### Common Issues

1. **YOLO Model Download Fails**
   ```bash
   # Download manually
   python -c "from ultralytics import YOLO; YOLO('yolov9c.pt')"
   ```

2. **API Servers Not Starting**
   ```bash
   # Check port conflicts
   netstat -an | findstr :3001
   # Kill processes using ports 3001-3004
   ```

3. **Facebook Login Issues**
   ```bash
   # Clear browser profile
   rm -rf chrome_profile_*
   # Run Facebook login flow again
   ```

4. **Database Connection Fails**
   ```bash
   # Verify Supabase credentials in .env
   # Check network connectivity
   # Run database setup: python -c "from object_detection_pipeline import *; pipeline = ObjectDetectionPipeline()"
   ```

## 📈 Performance Tips

- **Faster Processing**: Use `yolov9s.pt` instead of `yolov9c.pt`
- **Better Accuracy**: Use `yolov9e.pt` for higher precision
- **Memory Usage**: Process one image at a time for large images
- **API Limits**: Add delays between API calls if rate limited

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the console output for error details
3. Ensure all API keys are properly configured
4. Verify all API servers are running

---

**🎉 Happy decluttering and selling with Decluttered.AI!**