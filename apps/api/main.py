#!/usr/bin/env python3
"""
Fast Image Recognition API - Removed startup Google login check for speed
"""

import os
import time
import re
import json
import base64
import random
import urllib.parse
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
from urllib.parse import urlparse

# Gemini API for HTML analysis fallback
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    print("✅ Gemini available for HTML analysis")
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Gemini not available - install: pip install google-generativeai")

app = Flask(__name__)
CORS(app)

class FastImageRecognitionAPI:
    def __init__(self):
        self.driver = None
        self.profile_path = os.path.abspath('chrome_profile_google')
        # Skip login verification at startup for speed
        self.setup_gemini()
        
    def setup_gemini(self):
        """Setup Gemini for HTML analysis fallback"""
        self.gemini_model = None
        if GEMINI_AVAILABLE:
            api_keys = [
                os.getenv('GEMINI_API_KEY'),
                os.getenv('GOOGLE_AI_KEY'),
                os.getenv('GEMINI_API_KEY_1'),
                os.getenv('GEMINI_API_KEY_2')
            ]
            
            for key in api_keys:
                if key and key != 'your_gemini_api_key_here':
                    try:
                        genai.configure(api_key=key)
                        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                        # Test the model
                        test = self.gemini_model.generate_content("Hello")
                        if test and test.text:
                            print(f"✅ Gemini working: {key[:10]}...")
                            break
                    except Exception as e:
                        print(f"❌ Gemini key failed {key[:10]}...: {e}")
                        continue
    
    def start_browser(self):
        """Start Chrome with persistent profile (skip login check for speed)"""
        try:
            print("🚀 Starting browser with Google profile (fast mode)...")
            
            if not os.path.exists(self.profile_path):
                os.makedirs(self.profile_path)
                print(f"📁 Created profile directory: {self.profile_path}")
            
            options = Options()
            
            # Anti-detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Performance & stealth
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-logging')
            options.add_argument('--log-level=3')
            
            # Persistent profile for Google login (keep cookies)
            options.add_argument(f'--user-data-dir={self.profile_path}')
            
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Hide webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Browser started with Google profile (cookies preserved)")
            return True
            
        except Exception as e:
            print(f"❌ Browser startup failed: {e}")
            return False
    
    def ensure_browser_ready(self) -> bool:
        """Ensure browser is ready (skip login check for speed)"""
        if not self.driver:
            return self.start_browser()
        return True
    
    def extract_price_data(self) -> dict:
        """Extract pricing information from Google results"""
        price_data = {
            'current_prices': [],
            'typical_price_range': None,
            'currency': 'USD'
        }
        
        try:
            print("💰 Extracting price information...")
            
            # Extract current prices from shopping results
            price_selectors = [
                '.price',
                '.a-price-whole',
                '.notranslate',
                '[data-price]',
                'span:contains("$")',
                '.price-current',
                '.sr-price'
            ]
            
            for selector in price_selectors:
                try:
                    if ':contains(' in selector:
                        elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '$')]")
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements[:5]:  # Limit to first 5
                        text = element.text.strip()
                        # Extract price with regex
                        price_match = re.search(r'\$(\d+(?:\.\d{2})?)', text)
                        if price_match:
                            price = float(price_match.group(1))
                            if 10 <= price <= 1000:  # Reasonable price range
                                price_data['current_prices'].append({
                                    'price': price,
                                    'currency': 'USD',
                                    'source': 'shopping_result'
                                })
                except Exception as e:
                    continue
            
            # Extract "Typically $X-$Y" price range
            typical_price_selectors = [
                '[aria-label*="Typically"]',
                '.mQzvxd',
                '.gayxO',
                'div:contains("Typically")',
                '*:contains("Typically $")'
            ]
            
            for selector in typical_price_selectors:
                try:
                    if ':contains(' in selector:
                        elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), 'Typically')]")
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        text = element.get_attribute('aria-label') or element.text
                        print(f"   📊 Checking typical price text: '{text}'")
                        
                        # Extract price range
                        range_patterns = [
                            r'Typically\s+\$(\d+)\s+to\s+\$(\d+)',
                            r'Typically\s+\$(\d+)[-–—]\$(\d+)',
                            r'\$(\d+)[-–—]\$(\d+)'
                        ]
                        
                        for pattern in range_patterns:
                            match = re.search(pattern, text, re.I)
                            if match:
                                min_price = float(match.group(1))
                                max_price = float(match.group(2))
                                price_data['typical_price_range'] = {
                                    'min': min_price,
                                    'max': max_price,
                                    'currency': 'USD',
                                    'text': text.strip()
                                }
                                print(f"   ✅ Found typical price range: ${min_price}-${max_price}")
                                break
                        
                        if price_data['typical_price_range']:
                            break
                except Exception as e:
                    continue
                
                if price_data['typical_price_range']:
                    break
            
            print(f"   💰 Found {len(price_data['current_prices'])} current prices")
            if price_data['typical_price_range']:
                print(f"   📊 Typical range: ${price_data['typical_price_range']['min']}-${price_data['typical_price_range']['max']}")
            
        except Exception as e:
            print(f"❌ Price extraction error: {e}")
        
        return price_data
    
    def extract_rating_data(self) -> dict:
        """Extract rating and review information"""
        rating_data = {
            'rating': None,
            'rating_out_of': 5.0,
            'review_count': None,
            'review_count_text': None
        }
        
        try:
            print("⭐ Extracting rating information...")
            
            # Rating extraction selectors
            rating_selectors = [
                '[aria-label*="Rated"]',
                '.z3HNkc',
                '[role="img"][aria-label*="out of"]',
                '.rating',
                '.stars',
                '*[aria-label*="star"]'
            ]
            
            for selector in rating_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        aria_label = element.get_attribute('aria-label') or ''
                        text = element.text.strip()
                        
                        print(f"   ⭐ Checking rating text: '{aria_label}' / '{text}'")
                        
                        # Extract rating patterns
                        rating_patterns = [
                            r'Rated\s+([0-9.]+)\s+out\s+of\s+([0-9.]+)',
                            r'([0-9.]+)\s+out\s+of\s+([0-9.]+)',
                            r'([0-9.]+)\s*stars?',
                            r'([0-9.]+)\s*/\s*([0-9.]+)'
                        ]
                        
                        for pattern in rating_patterns:
                            match = re.search(pattern, aria_label + ' ' + text, re.I)
                            if match:
                                rating = float(match.group(1))
                                if len(match.groups()) >= 2:
                                    rating_out_of = float(match.group(2))
                                else:
                                    rating_out_of = 5.0
                                
                                if 0 <= rating <= rating_out_of:
                                    rating_data['rating'] = rating
                                    rating_data['rating_out_of'] = rating_out_of
                                    print(f"   ✅ Found rating: {rating}/{rating_out_of}")
                                    break
                        
                        if rating_data['rating']:
                            break
                except Exception as e:
                    continue
                
                if rating_data['rating']:
                    break
            
            # Review count extraction
            review_count_selectors = [
                '.RDApEe.YrbPuc',
                '.review-count',
                '*:contains("reviews")',
                '*:contains("(")',
                '[aria-label*="review"]'
            ]
            
            for selector in review_count_selectors:
                try:
                    if ':contains(' in selector:
                        if '"("' in selector:
                            elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '(') and contains(text(), ')')]")
                        else:
                            elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), 'review')]")
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements[:3]:
                        text = element.text.strip()
                        print(f"   📝 Checking review count text: '{text}'")
                        
                        # Extract review counts
                        count_patterns = [
                            r'\(([0-9,.]+[KkMm]?)\)',
                            r'\(([0-9,.]+)\s*reviews?\)',
                            r'([0-9,.]+[KkMm]?)\s*reviews?',
                            r'\(([0-9,.]+)\)'
                        ]
                        
                        for pattern in count_patterns:
                            match = re.search(pattern, text, re.I)
                            if match:
                                count_str = match.group(1).replace(',', '')
                                
                                # Convert K/M notation
                                if count_str.lower().endswith('k'):
                                    count = float(count_str[:-1]) * 1000
                                elif count_str.lower().endswith('m'):
                                    count = float(count_str[:-1]) * 1000000
                                else:
                                    count = float(count_str)
                                
                                if count > 0:
                                    rating_data['review_count'] = int(count)
                                    rating_data['review_count_text'] = match.group(0)
                                    print(f"   ✅ Found review count: {int(count)} ({rating_data['review_count_text']})")
                                    break
                        
                        if rating_data['review_count']:
                            break
                except Exception as e:
                    continue
                
                if rating_data['review_count']:
                    break
            
        except Exception as e:
            print(f"❌ Rating extraction error: {e}")
        
        return rating_data
    
    def extract_product_name(self, title: str) -> str:
        """Clean product name"""
        if not title:
            return None
            
        clean_title = re.sub(r'\s*-\s*(Amazon|eBay|Best Buy|Walmart|Target|Newegg).*$', '', title, flags=re.I)
        clean_title = re.sub(r'\s*\|\s*.*$', '', clean_title)
        clean_title = re.sub(r'\s*:\s*.*$', '', clean_title)
        clean_title = clean_title.replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()
        
        return clean_title if len(clean_title) > 5 else None
    
    def check_and_handle_related_search(self) -> bool:
        """Check for 'Related search' section and click on it if main product info not found"""
        try:
            print("🔍 Checking for 'Related search' section...")
            
            # Look for "Related search" elements
            related_search_selectors = [
                '.GuCxbd [data-hveid] a.Kg0xqe',  # Your specific case
                'div:contains("Related search") a',
                '.kRdUPb + a',
                '[data-hveid] a.sjVJQd',
                'a.Kg0xqe.sjVJQd'
            ]
            
            for selector in related_search_selectors:
                try:
                    if ':contains(' in selector:
                        # Use XPath for text-based selection
                        elements = self.driver.find_elements(By.XPATH, 
                            "//div[contains(text(), 'Related search')]/following-sibling::a | //div[contains(text(), 'Related search')]/..//a")
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if elements:
                        related_link = elements[0]  # Take the first related search result
                        
                        # Get the product name from the link
                        link_text = related_link.text.strip()
                        if len(link_text) > 5:  # Valid product name
                            print(f"🔗 Found related search: '{link_text}'")
                            print("🖱️ Clicking on related search link...")
                            
                            # Click the related search link
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", related_link)
                            time.sleep(0.5)  # Reduced from 1
                            related_link.click()
                            
                            # Wait for the new page to load
                            time.sleep(2.5)  # Reduced from 4
                            
                            print("✅ Navigated to related search results")
                            return True
                            
                except Exception as e:
                    print(f"⚠️ Error with selector {selector}: {e}")
                    continue
            
            print("📝 No related search links found")
            return False
            
        except Exception as e:
            print(f"❌ Error checking related search: {e}")
            return False

    def extract_product_from_results(self, html_content: str) -> dict:
        """Enhanced product extraction with pricing and rating data"""
        try:
            print("🔍 Extracting product information with enhanced data...")
            
            # First attempt: Try to extract from main results
            result = self._extract_main_product_info()
            
            # If no product found, check for "Related search" and try again
            if not result.get('product_name'):
                print("🔄 No product found in main results, checking for related search...")
                
                if self.check_and_handle_related_search():
                    # Try extraction again after clicking related search
                    print("🔍 Re-extracting after navigating to related search...")
                    time.sleep(2)  # Let the page stabilize
                    result = self._extract_main_product_info()
                    
                    if result.get('product_name'):
                        print("✅ Successfully extracted product from related search!")
                    else:
                        print("⚠️ Still no product found after related search navigation")
                else:
                    print("⚠️ Could not find or navigate to related search")
            
            return result
            
        except Exception as e:
            print(f"❌ Enhanced extraction error: {e}")
            return {'error': f'Extraction failed: {str(e)}'}
    
    def _extract_main_product_info(self) -> dict:
        """Extract main product information from current page"""
        try:
            # Product name extraction
            modern_selectors = [
                '.PZPZlf[data-attrid="title"]',
                '.PZPZlf.ssJ7i.xgAzOe',
                '[data-attrid="title"]',
                '.KsRP6 .PZPZlf',
                '[data-sh] h3 a',
                'h3 a[href*="amazon"]',
                'h3 a[href*="ebay"]',
                'h3 a[href*="soundcore"]',
                '.yuRUbf h3 a',
                'h3 a'
            ]
            
            product_name = None
            source_url = None
            host = None
            
            for selector in modern_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"   Found {len(elements)} elements with {selector}")
                    
                    for i, element in enumerate(elements[:3]):
                        try:
                            if element.tag_name == 'a':
                                text = element.text.strip()
                                href = element.get_attribute('href')
                            else:
                                text = element.text.strip()
                                try:
                                    parent = element.find_element(By.XPATH, '..')
                                    link = parent.find_element(By.TAG_NAME, 'a')
                                    href = link.get_attribute('href')
                                except:
                                    href = None
                            
                            if text and len(text) > 10:
                                product_name = self.extract_product_name(text)
                                
                                if href and href.startswith('/url?q='):
                                    match = re.search(r'/url\?q=([^&]+)', href)
                                    if match:
                                        source_url = urllib.parse.unquote(match.group(1))
                                elif href and href.startswith('http'):
                                    source_url = href
                                
                                if product_name:
                                    if source_url:
                                        try:
                                            host = urlparse(source_url).hostname
                                        except:
                                            pass
                                    print(f"✅ Found product: '{product_name}'")
                                    break
                        except Exception as e:
                            continue
                    
                    if product_name:
                        break
                        
                except Exception as e:
                    continue
            
            # Extract additional data
            price_data = self.extract_price_data()
            rating_data = self.extract_rating_data()
            
            return {
                'product_name': product_name,
                'source_url': source_url,
                'host': host,
                'pricing': price_data,
                'rating': rating_data
            }
            
        except Exception as e:
            print(f"❌ Main product info extraction error: {e}")
            return {
                'product_name': None,
                'source_url': None,
                'host': None,
                'pricing': {},
                'rating': {}
            }
    
    def perform_google_reverse_search(self, image_data: bytes) -> dict:
        """Perform Google reverse image search (fast mode - uses saved cookies)"""
        
        # Skip login check - just ensure browser is ready
        if not self.ensure_browser_ready():
            return {'error': 'Browser startup failed'}
        
        start_time = time.time()
        temp_file = None
        
        try:
            # Save image to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
                f.write(image_data)
                temp_file = f.name
            
            print("🖼️ Navigating to Google Images (using saved cookies)...")
            self.driver.get("https://images.google.com")
            time.sleep(1.5)  # Reduced from 2 + random
            
            # Quick human behavior simulation
            self.driver.execute_script(f"window.scrollTo(0, {random.randint(20, 100)});")
            time.sleep(0.5)  # Reduced from 1 + random
            
            print("📷 Looking for camera icon...")
            camera_selectors = [
                '[aria-label*="Search by image"]',
                '[title*="Search by image"]', 
                'div[jsaction*="camera"]',
                '.nDcEnd'
            ]
            
            camera_clicked = False
            for selector in camera_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            print(f"📷 Found camera icon: {selector}")
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                            time.sleep(0.3)  # Reduced from 0.5
                            self.driver.execute_script("arguments[0].click();", element)
                            camera_clicked = True
                            break
                    if camera_clicked:
                        break
                except:
                    continue
            
            if not camera_clicked:
                self.driver.get("https://images.google.com/imghp?hl=en&tab=wi")
                time.sleep(1.5)  # Reduced from 2
            
            time.sleep(0.5)  # Reduced from 1
            
            # Upload file
            print("📁 Uploading image...")
            file_input_selectors = [
                'input[type="file"]',
                'input[name="encoded_image"]',
                'input[accept*="image"]'
            ]
            
            file_uploaded = False
            for selector in file_input_selectors:
                try:
                    file_inputs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for file_input in file_inputs:
                        if file_input.is_enabled():
                            file_input.send_keys(temp_file)
                            file_uploaded = True
                            print("✅ File uploaded successfully")
                            break
                    if file_uploaded:
                        break
                except:
                    continue
            
            if not file_uploaded:
                return {'error': 'Could not upload file'}
            
            print("⏳ Waiting for search results...")
            time.sleep(3)  # Reduced from 4
            
            # Wait for results with shorter timeout
            try:
                WebDriverWait(self.driver, 10).until(  # Reduced from 15
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h3, [data-sh], .yuRUbf, .PZPZlf'))
                )
                print("✅ Search results loaded")
            except:
                print("⏳ Results still loading, proceeding anyway...")
            
            # Enhanced extraction with related search handling
            result = self.extract_product_from_results(self.driver.page_source)
            
            # Reduced wait time for next request
            time.sleep(1.5)  # Reduced from 3
            
            latency = int((time.time() - start_time) * 1000)
            
            return {
                'product_name': result.get('product_name'),
                'source_url': result.get('source_url'), 
                'host': result.get('host'),
                'pricing': result.get('pricing', {}),
                'rating': result.get('rating', {}),
                'diagnostics': {
                    'provider': 'google_fast_mode_cookies',
                    'vision_ms': latency,
                    'login_skipped': True  # Show that we skipped login check
                }
            }
            
        except Exception as e:
            print(f"❌ Google search error: {e}")
            return {'error': f'Search failed: {str(e)}'}
            
        finally:
            if temp_file:
                try:
                    os.unlink(temp_file)
                except:
                    pass

# Global API instance
api = FastImageRecognitionAPI()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'OK',
        'service': 'fast_image_recognition',
        'timestamp': datetime.now().isoformat(),
        'browser_ready': api.driver is not None,
        'login_check_skipped': True,
        'cookies_preserved': True
    })

@app.route('/api/recognition/basic', methods=['POST'])
def recognition_basic():
    try:
        image_data = None
        
        # Handle multipart form data
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                image_data = file.read()
        
        # Handle JSON with base64
        elif request.is_json:
            json_data = request.get_json()
            if 'image_base64' in json_data:
                base64_string = json_data['image_base64']
                if base64_string.startswith('data:image'):
                    base64_string = base64_string.split(',')[1]
                image_data = base64.b64decode(base64_string)
        
        if not image_data:
            return jsonify({
                'ok': False,
                'error_code': 'MISSING_IMAGE',
                'message': 'No image provided'
            }), 400
        
        if len(image_data) > 10 * 1024 * 1024:
            return jsonify({
                'ok': False,
                'error_code': 'IMAGE_TOO_LARGE',
                'message': 'Image must be less than 10MB'
            }), 400
        
        # Perform fast search (no login check)
        result = api.perform_google_reverse_search(image_data)
        
        if 'error' in result:
            return jsonify({
                'ok': False,
                'error_code': 'SEARCH_ERROR',
                'message': result['error']
            }), 500
        
        return jsonify({
            'ok': True,
            'data': {
                'product_name': result['product_name'],
                'source_url': result['source_url'],
                'host': result['host'],
                'pricing': result.get('pricing', {}),
                'rating': result.get('rating', {})
            },
            'diagnostics': result['diagnostics']
        })
        
    except Exception as e:
        print(f"❌ API error: {e}")
        return jsonify({
            'ok': False,
            'error_code': 'INTERNAL_ERROR',
            'message': 'Image recognition failed'
        }), 500

if __name__ == '__main__':
    print("🚀 FAST Image Recognition API")
    print("🌐 Server: http://localhost:3001")
    print("📷 Endpoint: POST /api/recognition/basic")
    print("⚡ Fast Mode: Skips Google login check, uses saved cookies!")
    print("💡 Features: Product name, prices, ratings, and review counts!")
    
    app.run(debug=True, host='0.0.0.0', port=3001)