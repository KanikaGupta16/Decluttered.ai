#!/usr/bin/env python3
"""
Complete Price Scraper API - Facebook Marketplace & eBay
Built from scratch with accurate selectors and login system
"""

import os
from dotenv import load_dotenv
import time
import re
import json
import random
import urllib.parse
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from difflib import SequenceMatcher

from flask import Flask, request, jsonify
from flask_cors import CORS

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from webdriver_manager.chrome import ChromeDriverManager

# Gemini for semantic matching
try:
    from google import genai
    GEMINI_AVAILABLE = True
    print("✅ Gemini AI available for semantic matching")
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Gemini AI not available - using basic string matching")

app = Flask(__name__)
CORS(app)

class MarketplaceScraper:
    def __init__(self):
        self.driver = None
        self.profile_path = os.path.abspath('chrome_profile_scraper')
        self.facebook_logged_in = False
        self.gemini_model = None
        self.setup_gemini()
        print("🛒 Marketplace Scraper initialized")
    
    def setup_gemini(self):
        """Initialize Gemini AI for semantic product matching using .env GEMINI_API_KEY only"""
        if not GEMINI_AVAILABLE:
            return

        load_dotenv()
        key = os.getenv('GEMINI_API_KEY')
        if key and key.strip() and key != 'your_api_key_here':
            try:
                self.gemini_client = genai.Client(api_key=key.strip())
                # Test the model
                test_response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash", contents="Test"
                )
                if test_response and hasattr(test_response, 'text'):
                    print(f"✅ Gemini AI configured successfully: {key[:8]}...")
                    return
            except Exception as e:
                print(f"⚠️ Gemini key failed {key[:8]}...: {e}")
                return

        print("⚠️ No working Gemini API key found - using basic string matching")
    
    def start_browser(self, headless=False):
        """Start Chrome browser with optimal settings"""
        try:
            print("🌐 Starting Chrome browser...")
            
            # Create profile directory
            if not os.path.exists(self.profile_path):
                os.makedirs(self.profile_path)
                print(f"📁 Created profile directory: {self.profile_path}")
            
            options = Options()
            
            # Anti-detection settings
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Performance settings
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-logging')
            options.add_argument('--log-level=3')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            
            # Persistent profile for login cookies
            options.add_argument(f'--user-data-dir={self.profile_path}')
            
            if headless:
                options.add_argument('--headless=new')
            else:
                options.add_argument('--start-maximized')
            
            # Install and start Chrome
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Hide automation indicators
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            print("✅ Chrome browser started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            return False
    
    def semantic_similarity(self, query_product: str, found_title: str) -> float:
        """Calculate semantic similarity between products using Gemini AI"""
        if not hasattr(self, 'gemini_client'):
            return SequenceMatcher(None, query_product.lower(), found_title.lower()).ratio()
        try:
            prompt = f"""
Rate the similarity between these two products on a scale from 0.0 to 1.0:

Query Product: "{query_product}"
Found Product: "{found_title}"

Consider:
- Brand names (exact match gets higher score)
- Product type/category (headphones, earbuds, phone, etc.)
- Model numbers and generations
- Key features and specifications
- Color variations (same product, different color = high score)

Scoring guide:
1.0 = Identical products
0.9 = Same product, different color/storage/minor variant  
0.8 = Same model line, different generation (iPhone 14 vs iPhone 15)
0.7 = Same brand, similar product category
0.5 = Same category, different brand
0.3 = Related products
0.1 = Somewhat related
0.0 = Completely different

Respond with ONLY the decimal number (e.g., 0.85):
"""
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            if response and hasattr(response, 'text'):
                score_match = re.search(r'([0-9]*\.?[0-9]+)', response.text.strip())
                if score_match:
                    score = float(score_match.group(1))
                    return max(0.0, min(1.0, score))
            return SequenceMatcher(None, query_product.lower(), found_title.lower()).ratio()
        except Exception as e:
            print(f"⚠️ Gemini similarity check failed: {e}")
            return SequenceMatcher(None, query_product.lower(), found_title.lower()).ratio()
    
    def normalize_condition(self, condition_text: str) -> str:
        """Normalize condition descriptions to standard categories"""
        if not condition_text:
            return 'unknown'
        
        condition_lower = condition_text.lower().strip()
        
        # Mapping various condition descriptions
        if any(term in condition_lower for term in ['new', 'brand new', 'sealed', 'unopened', 'unused']):
            return 'new'
        elif any(term in condition_lower for term in ['like new', 'excellent', 'mint', 'perfect']):
            return 'like_new' 
        elif any(term in condition_lower for term in ['good', 'very good', 'fine', 'great']):
            return 'good'
        elif any(term in condition_lower for term in ['fair', 'okay', 'decent', 'acceptable']):
            return 'fair'
        elif any(term in condition_lower for term in ['poor', 'bad', 'damaged', 'broken', 'parts']):
            return 'poor'
        elif any(term in condition_lower for term in ['used', 'pre-owned', 'preowned']):
            return 'used'
        else:
            return 'used'  # Default to used
    
    def extract_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        if not price_text:
            return None
        
        # Remove common currency symbols and whitespace
        cleaned = price_text.replace('$', '').replace(',', '').replace(' ', '')
        
        # Extract price patterns
        price_patterns = [
            r'^(\d+(?:\.\d{2})?)$',                    # Simple: "65.99"
            r'(\d+(?:\.\d{2})?)\s*(?:usd|dollars?)?',  # With currency: "65 USD"
            r'(\d+(?:\.\d{2})?)\s*each',               # Per item: "65 each"
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, cleaned, re.I)
            if match:
                try:
                    price = float(match.group(1))
                    if 1 <= price <= 50000:  # Reasonable price range
                        return price
                except ValueError:
                    continue
        
        return None
    
    # === FACEBOOK MARKETPLACE ===
    
    def check_facebook_login(self) -> bool:
        """Check if we're logged into Facebook"""
        try:
            print("🔍 Checking Facebook login status...")
            
            self.driver.get("https://www.facebook.com/marketplace")
            time.sleep(3)
            
            current_url = self.driver.current_url.lower()
            page_title = self.driver.title.lower()
            
            # Check for login indicators
            if ("marketplace" in current_url and 
                "login" not in current_url and 
                "marketplace" in page_title):
                
                print("✅ Facebook login confirmed")
                self.facebook_logged_in = True
                return True
            
            print("🔐 Facebook login required")
            return False
            
        except Exception as e:
            print(f"❌ Error checking Facebook login: {e}")
            return False
    
    def facebook_login_flow(self) -> bool:
        """Interactive Facebook login process"""
        try:
            print("\n🔐 FACEBOOK LOGIN REQUIRED")
            print("=" * 60)
            print("Facebook Marketplace requires authentication to view listings.")
            print("This is a ONE-TIME setup - your login will be saved.")
            print("=" * 60)
            
            # Navigate to Facebook login
            self.driver.get("https://www.facebook.com/login")
            time.sleep(3)
            
            print("\n👆 Please complete the following steps:")
            print("1. Log into your Facebook account in the browser window")
            print("2. Complete any security checks (2FA, etc.)")
            print("3. Wait for the page to fully load")
            print("4. Return here and press Enter")
            
            input("\n>>> Press Enter after you've successfully logged in...")
            
            # Verify login by accessing marketplace
            for attempt in range(3):
                print(f"🔄 Verifying login... (attempt {attempt + 1}/3)")
                
                self.driver.get("https://www.facebook.com/marketplace")
                time.sleep(4)
                
                if self.check_facebook_login():
                    print("🎉 Facebook login successful and verified!")
                    return True
                
                if attempt < 2:
                    print("⚠️ Login not detected, please check the browser window")
                    time.sleep(3)
            
            print("❌ Facebook login verification failed")
            print("Please ensure you're fully logged in and try again")
            return False
            
        except Exception as e:
            print(f"❌ Facebook login process failed: {e}")
            return False
    
    def ensure_facebook_access(self) -> bool:
        """Ensure Facebook access (login if needed)"""
        if not self.driver:
            if not self.start_browser():
                return False
        
        # Check current login status
        if self.check_facebook_login():
            return True
        
        # Need to login
        return self.facebook_login_flow()
    
    def scrape_facebook_marketplace(self, query: str, max_results: int = 15) -> List[Dict]:
        """Scrape Facebook Marketplace listings with expanded radius and batch Gemini filtering"""
        results = []

        # Ensure Facebook access
        if not self.ensure_facebook_access():
            print("❌ Facebook access failed - skipping Facebook scraping")
            return results

        try:
            print(f"🛒 Scraping Facebook Marketplace: '{query}' (radius: 160 km)")

            # Use expanded radius in km
            search_query = urllib.parse.quote(query)
            search_url = f"https://www.facebook.com/marketplace/search/?query={search_query}&radius_in_km=160"

            self.driver.get(search_url)
            time.sleep(2)

            # Find listing containers (no scrolling)
            listing_selectors = [
                'div[data-testid="marketplace-search-result"]',
                'a[href*="/marketplace/item/"]',
                'div.x9f619.x78zum5.xdt5ytf.x1qughib',
            ]

            listings = []
            for selector in listing_selectors:
                try:
                    found_listings = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if found_listings:
                        listings = found_listings
                        print(f"📦 Found {len(listings)} Facebook listings with: {selector}")
                        break
                except:
                    continue

            if not listings:
                print("⚠️ No Facebook listings found")
                return results

            # Collect candidate items
            candidates = []
            for i, listing in enumerate(listings[:max_results]):
                try:
                    # Extract price
                    price_text = None
                    price_selectors = [
                        '.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x676frb.x1lkfr7t.x1lbecb7.x1s688f.xzsf02u',
                        'span[dir="auto"]'
                    ]
                    for selector in price_selectors:
                        try:
                            price_elements = listing.find_elements(By.CSS_SELECTOR, selector)
                            for elem in price_elements:
                                text = elem.text.strip()
                                if '$' in text and len(text) < 15:
                                    price_text = text
                                    break
                            if price_text:
                                break
                        except:
                            continue
                    if not price_text:
                        continue

                    # Extract title
                    title_text = None
                    title_selectors = [
                        '.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6',
                        'span[dir="auto"]'
                    ]
                    for selector in title_selectors:
                        try:
                            title_elements = listing.find_elements(By.CSS_SELECTOR, selector)
                            for elem in title_elements:
                                text = elem.text.strip()
                                if text and len(text) > 15 and '$' not in text:
                                    title_text = text
                                    break
                            if title_text:
                                break
                        except:
                            continue
                    if not title_text:
                        continue

                    # Extract location
                    location_text = None
                    try:
                        location_elements = listing.find_elements(
                            By.XPATH, 
                            ".//*[contains(text(), 'MI') or contains(text(), 'CA') or contains(text(), 'TX') or contains(text(), 'FL') or contains(text(), 'NY')]"
                        )
                        for elem in location_elements:
                            text = elem.text.strip()
                            if len(text) < 50 and ',' in text:
                                location_text = text
                                break
                    except:
                        pass

                    # Parse price
                    price = self.extract_price(price_text)
                    if not price:
                        continue

                    candidates.append({
                        'title': title_text,
                        'price': price,
                        'currency': 'USD',
                        'platform': 'facebook',
                        'condition': self.normalize_condition(title_text),
                        'location': location_text,
                        'raw_price_text': price_text
                    })
                except Exception as e:
                    print(f"   ⚠️ Error processing Facebook listing {i}: {e}")
                    continue

            # Batch Gemini filtering
            if hasattr(self, 'gemini_client') and candidates:
                prompt = f"""
You are a product matching expert. For each candidate below, rate its similarity to the query product on a scale from 0.0 to 1.0.
Query Product: "{query}"
Candidates:
"""
                for idx, item in enumerate(candidates):
                    prompt += f"{idx+1}. {item['title']}\n"
                prompt += "\nRespond with a list of decimal numbers, one per candidate, in order."
                try:
                    response = self.gemini_client.models.generate_content(
                        model="gemini-2.5-flash", contents=prompt
                    )
                    scores = []
                    if response and hasattr(response, 'text'):
                        scores = [float(s) for s in re.findall(r'([0-9]*\.?[0-9]+)', response.text.strip())]
                    scores = [(max(0.0, min(1.0, s))) for s in scores]
                    while len(scores) < len(candidates):
                        scores.append(0.0)
                except Exception as e:
                    print(f"⚠️ Gemini batch filtering failed: {e}")
                    scores = [self.semantic_similarity(query, item['title']) for item in candidates]
            else:
                scores = [self.semantic_similarity(query, item['title']) for item in candidates]

            # Only include highly relevant products (similarity ≥ 0.7)
            for item, sim in zip(candidates, scores):
                if sim >= 0.7:
                    item['similarity_score'] = sim
                    results.append(item)
                    print(f"   ✅ FB: ${item['price']} - {item['title'][:40]}... (sim: {sim:.2f})")

            print(f"🛒 Facebook Marketplace: {len(results)} highly relevant listings found (Gemini batch filtered)")

        except Exception as e:
            print(f"❌ Facebook scraping failed: {e}")

        return results
    
    # === EBAY ===
    
    def scrape_ebay_sold(self, query: str, max_results: int = 20) -> List[Dict]:
        """Scrape eBay sold listings using accurate selectors"""
        results = []
        
        try:
            print(f"🔨 Scraping eBay sold listings: '{query}'")
            
            if not self.driver:
                if not self.start_browser():
                    return results
            
            # eBay sold listings URL
            search_query = urllib.parse.quote(query)
            ebay_url = (
                f"https://www.ebay.com/sch/i.html?"
                f"_nkw={search_query}&"
                f"_sacat=0&"
                f"LH_Sold=1&"
                f"LH_Complete=1&"
                f"_sop=13"  # Sort by newest
            )
            
            self.driver.get(ebay_url)
            time.sleep(4)
            
            # Wait for results to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".s-item"))
                )
            except TimeoutException:
                print("⚠️ eBay results did not load in time")
            
            # Find listings using your provided HTML structure
            listing_selectors = [
                'li.s-item.s-item--horizontal',  # From your HTML
                'li[data-listingid]',            # Has listing ID
                '.s-item',                       # Fallback
            ]
            
            listings = []
            for selector in listing_selectors:
                try:
                    found_listings = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if found_listings and len(found_listings) > 1:  # More than just the header
                        listings = found_listings
                        print(f"📦 Found {len(listings)} eBay listings with: {selector}")
                        break
                except:
                    continue
            
            if not listings:
                print("⚠️ No eBay listings found")
                return results
            
            # Process listings (skip first - often an ad)
            for i, listing in enumerate(listings[1:max_results+1]):
                try:
                    # Extract title using your HTML structure
                    title_text = None
                    title_selectors = [
                        '.su-styled-text.primary.default',  # From your HTML
                        '.s-item__title span',
                        '.s-item__title'
                    ]
                    
                    for selector in title_selectors:
                        try:
                            title_elem = listing.find_element(By.CSS_SELECTOR, selector)
                            title_text = title_elem.text.strip()
                            
                            # Clean up title
                            if title_text.startswith('NEW LISTING'):
                                title_text = title_text.replace('NEW LISTING', '').strip()
                            
                            if title_text and len(title_text) > 10:
                                break
                        except:
                            continue
                    
                    if not title_text:
                        continue
                    
                    # Extract price using your HTML structure
                    price_text = None
                    price_selectors = [
                        '.su-styled-text.positive.bold.large-1.s-card__price',  # From your HTML: $29.00
                        '.s-item__price',
                        '.s-card__price'
                    ]
                    
                    for selector in price_selectors:
                        try:
                            price_elem = listing.find_element(By.CSS_SELECTOR, selector)
                            price_text = price_elem.text.strip()
                            if price_text and '$' in price_text:
                                break
                        except:
                            continue
                    
                    if not price_text:
                        continue
                    
                    # Extract condition using your HTML structure  
                    condition_text = 'used'
                    condition_selectors = [
                        '.su-styled-text.secondary.default',  # From your HTML: "Pre-Owned"
                        '.s-item__subtitle',
                        '.SECONDARY_INFO'
                    ]
                    
                    for selector in condition_selectors:
                        try:
                            condition_elem = listing.find_element(By.CSS_SELECTOR, selector)
                            text = condition_elem.text.strip()
                            if text and text.lower() not in ['sponsored', '']:
                                condition_text = text
                                break
                        except:
                            continue
                    
                    # Extract sold date using your HTML structure
                    sold_date = None
                    sold_selectors = [
                        '.su-styled-text.positive.default',  # From your HTML: "Sold  Sep 25, 2025"
                        '.POSITIVE',
                        '.s-item__caption'
                    ]
                    
                    for selector in sold_selectors:
                        try:
                            sold_elem = listing.find_element(By.CSS_SELECTOR, selector)
                            sold_text = sold_elem.text.strip()
                            if 'sold' in sold_text.lower():
                                sold_date = re.sub(r'^sold\s*', '', sold_text, flags=re.I).strip()
                                break
                        except:
                            continue
                    
                    # Parse price (handle ranges like "$50 to $75")
                    price = None
                    if ' to ' in price_text and '$' in price_text:
                        # Average of price range
                        price_matches = re.findall(r'\$(\d+(?:\.\d{2})?)', price_text)
                        if len(price_matches) >= 2:
                            prices = [float(p) for p in price_matches]
                            price = sum(prices) / len(prices)
                    else:
                        price = self.extract_price(price_text)
                    
                    if not price:
                        continue
                    
                    # Check similarity
                    similarity = self.semantic_similarity(query, title_text)
                    
                    if similarity >= 0.3:
                        result = {
                            'title': title_text,
                            'price': price,
                            'currency': 'USD', 
                            'platform': 'ebay',
                            'condition': self.normalize_condition(condition_text),
                            'sold_date': sold_date,
                            'similarity_score': similarity,
                            'raw_price_text': price_text
                        }
                        results.append(result)
                        print(f"   ✅ eBay: ${price} - {title_text[:40]}... (sim: {similarity:.2f})")
                
                except Exception as e:
                    print(f"   ⚠️ Error processing eBay listing {i}: {e}")
                    continue
            
            print(f"🔨 eBay: {len(results)} matching sold listings found")
            
        except Exception as e:
            print(f"❌ eBay scraping failed: {e}")
        
        return results
    
    # === PRICE ANALYSIS ===
    
    def calculate_price_statistics(self, listings: List[Dict]) -> Dict:
        """Calculate comprehensive price statistics"""
        if not listings:
            return {
                'count': 0,
                'avg': None,
                'median': None,
                'min': None,
                'max': None,
                'p25': None,
                'p75': None,
                'count_by_platform': {},
                'count_by_condition': {},
                'price_distribution': []
            }
        
        # Extract prices and categorize
        prices = [listing['price'] for listing in listings]
        platforms = {}
        conditions = {}
        
        for listing in listings:
            platform = listing['platform']
            condition = listing['condition']
            
            platforms[platform] = platforms.get(platform, 0) + 1
            conditions[condition] = conditions.get(condition, 0) + 1
        
        # Calculate basic statistics
        prices_sorted = sorted(prices)
        
        stats = {
            'count': len(prices),
            'avg': round(statistics.mean(prices), 2),
            'median': round(statistics.median(prices), 2),
            'min': min(prices),
            'max': max(prices),
            'count_by_platform': platforms,
            'count_by_condition': conditions
        }
        
        # Calculate percentiles if enough data
        if len(prices) >= 4:
            try:
                percentiles = statistics.quantiles(prices_sorted, n=4)
                stats['p25'] = round(percentiles[0], 2)
                stats['p75'] = round(percentiles[2], 2)
            except:
                stats['p25'] = stats['min']
                stats['p75'] = stats['max']
        else:
            stats['p25'] = stats['min']
            stats['p75'] = stats['max']
        
        # Price distribution in $10 buckets
        if prices:
            min_bucket = int(min(prices) // 10) * 10
            max_bucket = int(max(prices) // 10) * 10 + 10
            
            distribution = []
            for bucket_start in range(min_bucket, max_bucket + 1, 10):
                bucket_end = bucket_start + 10
                count = sum(1 for p in prices if bucket_start <= p < bucket_end)
                if count > 0:
                    distribution.append({
                        'range': f"${bucket_start}-${bucket_end-1}",
                        'count': count
                    })
            
            stats['price_distribution'] = distribution
        
        return stats
    
    def search_all_platforms(self, query: str, platforms: List[str] = None) -> Dict:
        """Search across all platforms and return comprehensive results"""
        if platforms is None:
            platforms = ['facebook', 'ebay']
        
        start_time = time.time()
        all_listings = []
        platform_results = {}
        
        try:
            # Facebook Marketplace
            if 'facebook' in platforms:
                fb_listings = self.scrape_facebook_marketplace(query)
                all_listings.extend(fb_listings)
                platform_results['facebook'] = {
                    'count': len(fb_listings),
                    'success': True
                }
            
            # eBay sold listings
            if 'ebay' in platforms:
                ebay_listings = self.scrape_ebay_sold(query)
                all_listings.extend(ebay_listings)
                platform_results['ebay'] = {
                    'count': len(ebay_listings),
                    'success': True
                }
            
            # Filter high-quality matches
            good_matches = [
                listing for listing in all_listings 
                if listing.get('similarity_score', 0) >= 0.4
            ]
            
            # Calculate statistics
            stats = self.calculate_price_statistics(good_matches)
            
            # Execution time
            execution_time = int((time.time() - start_time) * 1000)
            
            return {
                'query': query,
                'total_found': len(all_listings),
                'good_matches': len(good_matches),
                'listings': good_matches,
                'statistics': stats,
                'platform_results': platform_results,
                'execution_time_ms': execution_time,
                'platforms_searched': platforms,
                'semantic_matching_enabled': self.gemini_model is not None
            }
        
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return {
                'error': f'Search failed: {str(e)}',
                'query': query,
                'platforms_searched': platforms,
                'execution_time_ms': int((time.time() - start_time) * 1000)
            }
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                print("🔄 Browser closed")
            except:
                pass

# Initialize global scraper
scraper = MarketplaceScraper()

# === API ROUTES ===

@app.route('/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'OK',
        'service': 'marketplace_price_scraper',
        'timestamp': datetime.now().isoformat(),
        'browser_ready': scraper.driver is not None,
        'facebook_logged_in': scraper.facebook_logged_in,
        'semantic_matching': scraper.gemini_model is not None,
        'version': '2.0.0'
    })

@app.route('/api/facebook/login', methods=['POST'])
def facebook_login():
    """Trigger Facebook login process"""
    try:
        success = scraper.ensure_facebook_access()
        
        if success:
            return jsonify({
                'ok': True,
                'message': 'Facebook login successful',
                'logged_in': True
            })
        else:
            return jsonify({
                'ok': False,
                'error_code': 'LOGIN_FAILED',
                'message': 'Facebook login process failed'
            }), 400
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error_code': 'LOGIN_ERROR',
            'message': f'Login error: {str(e)}'
        }), 500

@app.route('/api/prices', methods=['POST'])
def get_prices():
    """
    Get market prices for a product
    
    Body:
    {
        "name": "Product name to search for",
        "platforms": ["facebook", "ebay"],  // optional
        "condition_filter": "all"           // optional: new, used, good, etc.
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'ok': False,
                'error_code': 'INVALID_REQUEST',
                'message': 'JSON request body required'
            }), 400
        
        data = request.get_json()
        
        if 'name' not in data or not data['name'].strip():
            return jsonify({
                'ok': False,
                'error_code': 'MISSING_PRODUCT_NAME',
                'message': 'Product name is required'
            }), 400
        
        # Extract parameters
        product_name = data['name'].strip()
        platforms = data.get('platforms', ['facebook', 'ebay'])
        condition_filter = data.get('condition_filter', 'all')
        
        # Validate platforms
        valid_platforms = ['facebook', 'ebay']
        platforms = [p for p in platforms if p in valid_platforms]
        
        if not platforms:
            return jsonify({
                'ok': False,
                'error_code': 'NO_VALID_PLATFORMS',
                'message': f'Valid platforms are: {valid_platforms}'
            }), 400
        
        # Perform search
        result = scraper.search_all_platforms(product_name, platforms)
        
        if 'error' in result:
            return jsonify({
                'ok': False,
                'error_code': 'SEARCH_FAILED',
                'message': result['error']
            }), 500
        
        # Filter by condition if requested
        listings = result['listings']
        if condition_filter != 'all':
            listings = [
                listing for listing in listings 
                if listing.get('condition') == condition_filter
            ]
            
            # Recalculate stats for filtered results
            if condition_filter != 'all':
                filtered_stats = scraper.calculate_price_statistics(listings)
            else:
                filtered_stats = result['statistics']
        else:
            filtered_stats = result['statistics']
        
        # Return results
        return jsonify({
            'ok': True,
            'data': {
                'query': result['query'],
                'comps': listings,
                'summary': filtered_stats,
                'currency': 'USD',
                'total_found': result['total_found'],
                'good_matches': len(listings),
                'condition_filter': condition_filter,
                'platforms_searched': result['platforms_searched'],
                'platform_results': result['platform_results']
            },
            'diagnostics': {
                'execution_time_ms': result['execution_time_ms'],
                'semantic_matching': result['semantic_matching_enabled'],
                'provider': 'marketplace_scraper_v2'
            }
        })
    
    except Exception as e:
        print(f"❌ API error: {e}")
        return jsonify({
            'ok': False,
            'error_code': 'INTERNAL_ERROR',
            'message': 'Price search failed'
        }), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint with sample product"""
    try:
        test_product = "Anker Soundcore Liberty 4 NC"
        result = scraper.search_all_platforms(test_product, ['facebook', 'ebay'])
        
        return jsonify({
            'ok': True,
            'test_product': test_product,
            'result': result
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

# === MAIN ===

if __name__ == '__main__':
    print("🛒 Marketplace Price Scraper API v2.0")
    print("=" * 50)
    print("🌐 Server: http://localhost:3002")
    print("📊 Prices: POST /api/prices")
    print("🔐 FB Login: POST /api/facebook/login")
    print("🧪 Test: GET /api/test")
    print("❤️  Health: GET /health")
    print()
    print("✨ Features:")
    print("  - Facebook Marketplace scraping (login required)")
    print("  - eBay sold listings with accurate selectors")
    print("  - Semantic product matching with Gemini AI")
    print("  - Comprehensive price statistics")
    print("  - Cookie-based login persistence")
    print()
    print("⚠️  Setup: Run Facebook login on first use")
    print("🚀 Ready for production!")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=3002)
    finally:
        scraper.close()