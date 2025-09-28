#!/usr/bin/env python3
"""
Marketplace Listing API - Facebook Marketplace & eBay Auto-Listing
Integrates with image recognition and price scraping for intelligent listings
"""

import os
from dotenv import load_dotenv
import time
import re
import json
import random
import statistics
import tempfile
import base64
import threading
from datetime import datetime
from typing import Dict, List, Optional
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from webdriver_manager.chrome import ChromeDriverManager

# eBay SDK
try:
    import requests
    EBAY_AVAILABLE = True
    print("[OK] eBay API client available")
except ImportError:
    EBAY_AVAILABLE = False
    print("[WARNING] eBay API client not available")

# Gemini for description generation
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    print("[OK] Gemini AI available for description generation")
except ImportError:
    GEMINI_AVAILABLE = False
    print("[WARNING] Gemini AI not available")

app = Flask(__name__)
CORS(app)

class MarketplaceLister:
    def __init__(self):
        self.driver = None
        self.profile_path = os.path.abspath('chrome_profile_lister')
        self.facebook_logged_in = False
        self.ebay_token = None
        self.gemini_model = None
        self.gemini_client = None  # Ensure attribute always exists
        self.setup_gemini()
        self.setup_ebay()
        print("[ROCKET] Marketplace Lister initialized")
    

    def setup_gemini(self):
        """Initialize Gemini AI for description generation"""
        if not GEMINI_AVAILABLE:
            self.gemini_model = None
            return

        load_dotenv()
        key = os.getenv('GEMINI_API_KEY')
        if key and key.strip() and key != 'your_api_key_here':
            try:
                genai.configure(api_key=key.strip())
                self.gemini_model = genai.GenerativeModel("gemini-2.5-flash")
                # Test model
                try:
                    _ = self.gemini_model.generate_content("Test")
                    print(f"[OK] Gemini AI configured successfully: {key[:8]}...")
                    return
                except Exception as e:
                    print(f"[WARNING] Gemini model error: {e}")
                    print("Listing available models:")
                    try:
                        models = genai.list_models()
                        print(models)
                    except Exception as e2:
                        print(f"[WARNING] Could not list models: {e2}")
                    return
            except Exception as e:
                print(f"[WARNING] Gemini key failed {key[:8]}...: {e}")
                self.gemini_model = None
                return

        print("[WARNING] No working Gemini API key found")
        self.gemini_model = None
    
    def setup_ebay(self):
        """Initialize eBay API credentials"""
        load_dotenv()
        self.ebay_config = {
            'app_id': os.getenv('EBAY_APP_ID'),
            'cert_id': os.getenv('EBAY_CERT_ID'),
            'dev_id': os.getenv('EBAY_DEV_ID'),
            'user_token': os.getenv('EBAY_USER_TOKEN'),
            'sandbox': os.getenv('EBAY_SANDBOX', 'true').lower() == 'true'
        }
        
        if self.ebay_config['app_id']:
            print(f"[OK] eBay API configured: {self.ebay_config['app_id'][:8]}...")
        else:
            print("[WARNING] eBay API not configured - add credentials to .env")
    
    def start_browser(self, headless=False):
        """Start Chrome browser with anti-detection settings"""
        try:
            print("[GLOBE] Starting Chrome browser for Facebook...")
            if not os.path.exists(self.profile_path):
                os.makedirs(self.profile_path)
                print(f"[FOLDER] Created profile directory: {self.profile_path}")

            options = Options()
            # Anti-detection settings (same as scraper.py)
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

            print("[OK] Chrome browser started successfully")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to start browser: {e}")
            return False
    
    def check_facebook_login(self) -> bool:
        """Check if logged into Facebook"""
        try:
            print("🔍 Checking Facebook login status...")
            
            self.driver.get("https://www.facebook.com/marketplace/create/item")
            time.sleep(3)
            
            current_url = self.driver.current_url.lower()
            page_title = self.driver.title.lower()
            
            if ("marketplace" in current_url and 
                "login" not in current_url and 
                ("marketplace" in page_title or "create" in current_url)):
                
                print("[OK] Facebook login confirmed")
                self.facebook_logged_in = True
                return True
            
            print("[LOCK] Facebook login required")
            return False
            
        except Exception as e:
            print(f"[ERROR] Error checking Facebook login: {e}")
            return False
    
    def facebook_login_flow(self) -> bool:
        """Interactive Facebook login process"""
        try:
            print("\n[LOCK] FACEBOOK LOGIN REQUIRED")
            print("=" * 60)
            print("Facebook Marketplace requires authentication to create listings.")
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
            
            # Verify login by accessing marketplace create page
            for attempt in range(3):
                print(f"🔄 Verifying login... (attempt {attempt + 1}/3)")
                
                self.driver.get("https://www.facebook.com/marketplace/create/item")
                time.sleep(4)
                
                if self.check_facebook_login():
                    print("🎉 Facebook login successful and verified!")
                    return True
                
                if attempt < 2:
                    print("[WARNING] Login not detected, please check the browser window")
                    time.sleep(3)
            
            print("[ERROR] Facebook login verification failed")
            return False
            
        except Exception as e:
            print(f"[ERROR] Facebook login process failed: {e}")
            return False
    
    def handle_facebook_confirmation_dialogs(self) -> bool:
        """Handle various Facebook confirmation dialogs that might appear"""
        try:
            print("🔍 Checking for Facebook confirmation dialogs...")
            
            # Common Facebook confirmation dialogs and their buttons
            dialog_patterns = [
                {
                    'name': 'Leave Page',
                    'selectors': [
                        "//div[@aria-label='Leave Page']",
                        "//span[text()='Leave Page']/ancestor::div[@role='button']",
                        "//div[@role='button' and .//span[text()='Leave Page']]"
                    ]
                },
                {
                    'name': 'Continue',
                    'selectors': [
                        "//div[@aria-label='Continue']",
                        "//span[text()='Continue']/ancestor::div[@role='button']",
                        "//button[text()='Continue']"
                    ]
                },
                {
                    'name': 'Confirm',
                    'selectors': [
                        "//div[@aria-label='Confirm']",
                        "//span[text()='Confirm']/ancestor::div[@role='button']",
                        "//button[text()='Confirm']"
                    ]
                },
                {
                    'name': 'OK',
                    'selectors': [
                        "//div[@aria-label='OK']",
                        "//span[text()='OK']/ancestor::div[@role='button']",
                        "//button[text()='OK']"
                    ]
                }
            ]
            
            for dialog in dialog_patterns:
                for selector in dialog['selectors']:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                print(f"[OK] Found '{dialog['name']}' dialog button")
                                try:
                                    element.click()
                                    print(f"[OK] Successfully clicked '{dialog['name']}' button")
                                    time.sleep(2)
                                    return True
                                except Exception:
                                    try:
                                        self.driver.execute_script("arguments[0].click();", element)
                                        print(f"[OK] Successfully clicked '{dialog['name']}' button with JavaScript")
                                        time.sleep(2)
                                        return True
                                    except Exception as e:
                                        print(f"[WARNING] Failed to click '{dialog['name']}' button: {e}")
                                        continue
                    except Exception:
                        continue
            
            print("📝 No confirmation dialogs found")
            return False
            
        except Exception as e:
            print(f"[ERROR] Error handling confirmation dialogs: {e}")
            return False

    def ensure_facebook_access(self) -> bool:
        """Ensure Facebook access (login if needed)"""
        if not self.driver:
            if not self.start_browser():
                return False
        
        if self.check_facebook_login():
            return True
        
        return self.facebook_login_flow()
    


    def generate_description(self, product_name: str, pricing_data: Dict, condition: str = "used") -> str:
        """Generate concise, human-like product description using Gemini AI"""
        try:
            if not self.gemini_model:
                # Fallback description
                return f"{product_name} in {condition} condition. Great value item!"

            # Extract pricing insights
            comps = pricing_data.get('comps', [])
            if not comps:
                market_info = "Limited market data available."
            else:
                avg_price = statistics.mean([comp['price'] for comp in comps])
                conditions = [comp['condition'] for comp in comps]
                platforms = [comp['platform'] for comp in comps]
                market_info = f"Average price: ${avg_price:.2f}. Common conditions: {', '.join(set(conditions))}. Available on: {', '.join(set(platforms))}."

            prompt = f"""
You are helping someone sell an item online. Write a short, friendly, and natural-sounding marketplace description for:
Product: {product_name}
Condition: {condition}
{market_info}

Guidelines:
- Maximum 2 short paragraphs, no more than 5 sentences total.
- Avoid generic AI phrases and keep it conversational, as if you are the seller.
- Mention the condition honestly and highlight practical features or benefits.
- End with a simple call to action (e.g., 'Message me if interested!').
- Do not use excessive capitalization, markdown, or spammy language.
"""

            response = self.gemini_model.generate_content(prompt)

            if hasattr(response, 'text') and response.text:
                description = response.text.strip()
                # Remove markdown, excessive whitespace, and AI-sounding phrases
                description = re.sub(r'\*\*', '', description)
                description = re.sub(r'\n\n+', '\n', description)
                # Truncate to 5 sentences max
                sentences = re.split(r'(?<=[.!?]) +', description)
                description = ' '.join(sentences[:5]).strip()
                # Remove common AI phrases
                description = re.sub(r'(As an AI language model,|I am an AI|I can|I will|This item is perfect for you if|Don\'t miss out on)', '', description, flags=re.I)
                return description

        except Exception as e:
            print(f"[WARNING] Description generation failed: {e}")
            # Fallback description
            return f"{product_name} in {condition} condition. Well-maintained and ready for a new owner. Message me if interested!"
    
    def calculate_optimal_price(self, pricing_data: Dict, condition: str = "used") -> float:
        """Calculate optimal listing price based on market data"""
        try:
            comps = pricing_data.get('comps', [])
            if not comps:
                return 50.0  # Default fallback
            
            # Filter by similar condition
            condition_comps = [comp for comp in comps if comp['condition'] == condition]
            if not condition_comps:
                condition_comps = comps  # Use all if no exact condition matches
            
            prices = [comp['price'] for comp in condition_comps]
            
            # Calculate percentiles for intelligent pricing
            if len(prices) >= 4:
                prices_sorted = sorted(prices)
                p25 = prices_sorted[len(prices_sorted) // 4]
                p75 = prices_sorted[3 * len(prices_sorted) // 4]
                median = statistics.median(prices)
                
                # Price slightly below median for quick sale, but above P25
                optimal = median * 0.95
                optimal = max(optimal, p25 * 1.1)  # Don't go too low
                optimal = min(optimal, p75 * 0.9)  # Don't go too high
                
            else:
                # Use average with slight discount
                optimal = statistics.mean(prices) * 0.9
            
            return round(optimal, 2)
            
        except Exception as e:
            print(f"[WARNING] Price calculation failed: {e}")
            return 50.0
    
    def _handle_nested_category_selection(self, listing_data: Dict, depth: int = 0, max_depth: int = 3):
        """Recursively handle nested category selection until no more dropdowns appear"""
        try:
            if depth >= max_depth:
                print(f"[WARNING] Maximum category depth ({max_depth}) reached")
                return
            
            print(f"🔄 Checking for category level {depth + 1}...")
            time.sleep(2)  # Wait for any new dropdown to appear
            
            # First, check if there's actually a new category dropdown that appeared
            category_dropdowns = []
            try:
                # Look for new category dropdowns that might have appeared
                new_dropdowns = self.driver.find_elements(By.XPATH, "//label[@role='combobox' and .//span[contains(text(), 'Category') or contains(text(), 'Subcategory') or contains(text(), 'Type')]]")
                for dropdown in new_dropdowns:
                    if dropdown.is_displayed():
                        category_dropdowns.append(dropdown)
                        print(f"Found potential category dropdown: {dropdown.text[:50]}...")
            except Exception as e:
                print(f"Error finding category dropdowns: {e}")
            
            # If we found a new dropdown, click it first
            if category_dropdowns and depth < 2:  # Only try clicking new dropdowns for first couple levels
                try:
                    dropdown = category_dropdowns[0]
                    print(f"Clicking new category dropdown at level {depth + 1}")
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", dropdown)
                    time.sleep(0.5)
                    dropdown.click()
                    time.sleep(2)
                    print(f"[OK] Opened new category dropdown at level {depth + 1}")
                except Exception as e:
                    print(f"[WARNING] Failed to click new dropdown: {e}")
            
            # Get current category options that might have appeared at this level
            category_options = []
            
            # Look for clickable category elements
            all_spans = self.driver.find_elements(By.XPATH, "//span[string-length(text()) > 2 and string-length(text()) < 50]")
            
            # ALSO look specifically in dropdown/menu areas
            menu_spans = []
            try:
                # Look for spans in dropdown menus, listboxes, or popup areas
                dropdown_areas = self.driver.find_elements(By.XPATH, "//div[@role='listbox']//span | //div[contains(@class, 'menu')]//span | //div[contains(@style, 'position: absolute')]//span")
                menu_spans.extend(dropdown_areas)
                
                # Look for spans that appear after category selection (likely in popover/dropdown areas)
                category_related_spans = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'accessories') or contains(text(), 'phones') or contains(text(), 'audio') or contains(text(), 'video') or contains(text(), 'computer') or contains(text(), 'laptop') or contains(text(), 'tablet') or contains(text(), 'camera') or contains(text(), 'gaming') or contains(text(), 'headphone') or contains(text(), 'speaker') or contains(text(), 'cable') or contains(text(), 'charger') or contains(text(), 'case') or contains(text(), 'cover') or contains(text(), 'battery')]")
                menu_spans.extend(category_related_spans)
                
                print(f"Found {len(menu_spans)} spans in dropdown/menu areas")
            except Exception as e:
                print(f"Error finding menu spans: {e}")
            
            # Combine all spans but prioritize menu spans
            all_candidate_spans = menu_spans + all_spans
            
            # Filter for potential category options - much more strict filtering
            excluded_texts = [
                'Photos', 'Videos', 'Add photos', 'Add video', 'Save Draft', 'Publish',
                'Category', 'Condition', 'Description', 'Price', 'Location', 'Title',
                'notification', 'unread', 'message', 'comment', 'like', 'share',
                'Marketplace', 'Public', 'or drag and drop', 'minute max', 'Learn more', 
                'Try It', 'Required', 'Home', 'Profile', 'Menu', 'Search', 'Messages',
                'Notifications', 'Settings', 'Help', 'Logout', 'Create', 'Post',
                'Upload', 'Browse', 'Select', 'Choose', 'Edit', 'Delete', 'Save',
                'Cancel', 'Back', 'Next', 'Continue', 'Skip', 'Done', 'Finish',
                # NEW: Add the problematic UI elements we're seeing
                'More details', 'Hide from friends', 'Commerce Policies', 'Seller details',
                'Privacy', 'Terms', 'About', 'Contact', 'FAQ', 'Support', 'Community',
                'Guidelines', 'Report', 'Block', 'Follow', 'Unfollow', 'Share'
            ]
            
            # Look specifically for category-like elements, not just any spans
            known_category_patterns = [
                'accessories', 'phones', 'mobile', 'audio', 'video', 'computer', 'laptop',
                'tablet', 'camera', 'gaming', 'console', 'headphone', 'speaker', 'cable',
                'charger', 'case', 'cover', 'screen', 'battery', 'parts', 'repair'
            ]
            
            for span in all_candidate_spans:
                try:
                    if span.is_displayed():
                        text = span.text.strip()
                        if (len(text) > 3 and len(text) < 40 and  # Tighter length requirements
                            not text.isdigit() and
                            not any(excl.lower() in text.lower() for excl in excluded_texts) and
                            text not in [opt[1] for opt in category_options]):  # Avoid duplicates
                            
                            # Only consider if it contains category-like keywords or looks like a product category
                            is_category_like = (
                                any(pattern in text.lower() for pattern in known_category_patterns) or
                                (' and ' in text and len(text.split()) <= 4) or  # "Mobile phones and accessories"
                                text.lower().endswith(('s', 'accessories', 'equipment', 'devices', 'products'))
                            )
                            
                            # Additional check: avoid common UI text patterns
                            is_ui_element = (
                                text.lower().startswith(('welcome', 'hello', 'hi ', 'your ', 'my ')) or
                                text in ['Home', 'Feed', 'Friends', 'Watch', 'Groups', 'Gaming'] or
                                'ago' in text.lower() or
                                any(char in text for char in ['(', ')', '#', '@', '$']) or
                                text.isupper()  # ALL CAPS usually UI elements
                            )
                            
                            if is_category_like and not is_ui_element:
                                category_options.append((span, text))
                except:
                    continue
            
            # Remove obvious non-category options and limit to reasonable number
            potential_categories = []
            for span, text in category_options[:20]:  # Limit to first 20 to avoid too many options
                # Additional filtering for category-like text
                if (not text.startswith(('$', '#', '@')) and
                    len(text.split()) <= 6 and  # Categories usually aren't long phrases
                    not re.match(r'^\d+\s*(hour|day|week|month|year)s?\s*ago', text.lower())):
                    potential_categories.append((span, text))
            
            if not potential_categories:
                print(f"[OK] No more category levels found at depth {depth + 1}")
                return
            
            print(f"Found {len(potential_categories)} potential category options at level {depth + 1}: {[text for _, text in potential_categories[:8]]}")
            
            # DEBUG: Let's see what elements we're actually finding
            if depth < 2:  # Only debug first couple levels
                print(f"🔍 DEBUG Level {depth + 1} - All found elements:")
                for i, (span, text) in enumerate(potential_categories[:10]):
                    try:
                        parent_class = span.find_element(By.XPATH, "./..").get_attribute('class') or 'no-class'
                        element_tag = span.tag_name
                        is_clickable = span.is_enabled()
                        print(f"  {i+1}. '{text}' | Tag: {element_tag} | Clickable: {is_clickable} | Parent class: {parent_class[:50]}...")
                    except:
                        print(f"  {i+1}. '{text}' | Could not get element details")
            
            # Use Gemini to pick the best option if available
            selected_category = None
            if self.gemini_model and len(potential_categories) > 0:
                try:
                    option_texts = [text for _, text in potential_categories[:15]]  # Limit for token efficiency
                    
                    context = f"Product: '{listing_data.get('title', '')}'"
                    if listing_data.get('description'):
                        context += f" Description: '{listing_data.get('description', '')[:100]}...'"
                    
                    prompt = f"""
                    {context}
                    Category selection level {depth + 1}.
                    
                    Choose the BEST category from this list:
                    {', '.join(option_texts)}
                    
                    Return ONLY the exact text from the list that best matches the product, nothing else.
                    If none seem appropriate, return "SKIP".
                    """
                    
                    response = self.gemini_model.generate_content(prompt)
                    if response and hasattr(response, 'text') and response.text:
                        gemini_choice = response.text.strip()
                        print(f"Gemini suggested at level {depth + 1}: '{gemini_choice}'")
                        
                        if gemini_choice.upper() != "SKIP":
                            # Find the option that matches Gemini's choice
                            for span, text in potential_categories:
                                if (gemini_choice.lower() in text.lower() or 
                                    text.lower() in gemini_choice.lower() or
                                    SequenceMatcher(None, gemini_choice.lower(), text.lower()).ratio() > 0.7):
                                    selected_category = (span, text)
                                    break
                        else:
                            print("Gemini suggested to skip this level")
                            return
                
                except Exception as e:
                    print(f"Gemini selection error at level {depth + 1}: {e}")
            
            # If Gemini didn't pick or failed, use similarity matching with the product title
            if not selected_category and potential_categories:
                product_title = listing_data.get('title', '').lower()
                best_span = None
                best_score = 0.0
                
                for span, text in potential_categories:
                    # Calculate similarity score
                    score = SequenceMatcher(None, text.lower(), product_title).ratio()
                    
                    # Boost score for certain keywords that are relevant to the product
                    if any(keyword in text.lower() for keyword in ['audio', 'headphone', 'speaker', 'electronic', 'music']):
                        score += 0.2
                    
                    if score > best_score and score > 0.3:  # Minimum threshold
                        best_score = score
                        best_span = (span, text)
                
                selected_category = best_span
            
            # Click the selected category if found
            if selected_category:
                span, text = selected_category
                try:
                    # Scroll element into view
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", span)
                    time.sleep(0.5)
                    
                    # Try clicking
                    try:
                        span.click()
                        print(f"[OK] Selected category at level {depth + 1}: '{text}'")
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", span)
                        print(f"[OK] Selected category at level {depth + 1} with JS: '{text}'")
                    
                    time.sleep(2)
                    
                    # Recursively check for next level
                    self._handle_nested_category_selection(listing_data, depth + 1, max_depth)
                    
                except Exception as e:
                    print(f"[WARNING] Failed to click category '{text}' at level {depth + 1}: {e}")
            else:
                print(f"[OK] No suitable category found at level {depth + 1}, stopping recursion")
                
        except Exception as e:
            print(f"[WARNING] Error in nested category selection at depth {depth}: {e}")

    def create_facebook_listing(self, listing_data: Dict) -> Dict:
        """Create Facebook Marketplace listing using Selenium with exact selectors"""
        try:
            if not self.ensure_facebook_access():
                return {'error': 'Facebook access failed', 'platform': 'facebook'}
            
            print("📝 Creating Facebook Marketplace listing...")
            wait = WebDriverWait(self.driver, 15)
            
            # Go directly to the create item page
            self.driver.get("https://www.facebook.com/marketplace/create/item")
            time.sleep(3)
            # Fill out the listing form using exact selectors provided
            

            # Title - using robust CSS selector and id
            try:
                title_field = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'][id^='_r_'][class*='xjbqb8w']"))
                )
                title_field.clear()
                title_field.send_keys(listing_data['title'])
            except TimeoutException:
                return {'error': 'Could not find title field', 'platform': 'facebook'}

            # Price - improved selection for price field
            try:
                # Wait for all text inputs and select the one below the Title
                inputs = wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "input[type='text'][id^='_r_'][class*='xjbqb8w']"))
                if len(inputs) > 1:
                    price_field = inputs[1]
                else:
                    # Fallback: try to find by placeholder or aria-label
                    price_field = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Price'] | //input[@aria-label='Price']"))
                    )
                price_field.clear()
                price_field.send_keys(str(int(listing_data['price'])))
            except Exception as e:
                print(f"[WARNING] Could not find or fill price field: {e}")
            
            # Category - use Gemini API to predict best category/subcategory
            try:
                # We'll use Gemini to choose from actual available options instead of predicting
                fb_category = 'Electronics'  # fallback
                fb_subcategory = None

                # Click the category dropdown/button (do not type)
                try:
                    # Try multiple selectors to find the category field - looking for the specific blue-bordered dropdown
                    category_button = None
                    selectors = [
                        "//label[contains(@class, 'x1i10hfl') and .//span[text()='Category']]",
                        "//div[contains(@class, 'x1i10hfl') and .//span[text()='Category']]",
                        "//label[@role='combobox' and .//span[contains(text(), 'Category')]]",
                        "//div[@role='combobox' and .//span[contains(text(), 'Category')]]",
                        "//span[text()='Category']/ancestor::label",
                        "//span[text()='Category']/parent::*/parent::*/parent::*",
                        "//input[contains(@placeholder, 'Type to search') or contains(@aria-label, 'Category')]/ancestor::label",
                        "//div[contains(@style, 'border') and .//span[text()='Category']]"
                    ]
                    
                    for i, selector in enumerate(selectors):
                        try:
                            elements = self.driver.find_elements(By.XPATH, selector)
                            if elements:
                                category_button = elements[0]
                                print(f"[OK] Found category button with selector {i+1}: {selector}")
                                break
                        except Exception:
                            continue
                    
                    if not category_button:
                        print("[WARNING] Could not find category button with any selector")
                        # Try to find any clickable element with "Category" text
                        try:
                            category_elements = self.driver.find_elements(By.XPATH, "//span[text()='Category']")
                            if category_elements:
                                # Try clicking the parent elements
                                for elem in category_elements:
                                    parent = elem.find_element(By.XPATH, "./..")
                                    if parent.tag_name in ['label', 'div', 'button']:
                                        category_button = parent
                                        print("[OK] Found category button by traversing from text element")
                                        break
                        except Exception:
                            pass
                    
                    if not category_button:
                        raise Exception("Category button not found")
                    
                    # Scroll to element and click
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", category_button)
                    time.sleep(1)
                    
                    # Try multiple click methods
                    try:
                        category_button.click()
                        print("[OK] Clicked category button with standard click")
                    except Exception:
                        try:
                            self.driver.execute_script("arguments[0].click();", category_button)
                            print("[OK] Clicked category button with JavaScript click")
                        except Exception:
                            # Find any input field inside and click it
                            try:
                                input_field = category_button.find_element(By.XPATH, ".//input")
                                input_field.click()
                                print("[OK] Clicked input field inside category button")
                            except Exception:
                                raise Exception("Could not click category button")
                    
                    time.sleep(3)  # Wait longer for dropdown to appear

                    # Check if dropdown opened by looking for category options
                    dropdown_opened = False
                    try:
                        # Look for visible category options in dropdown
                        dropdown_options = self.driver.find_elements(By.XPATH, "//div[contains(@role, 'option') or contains(@class, 'menu') or contains(@class, 'dropdown')]//span[contains(text(), 'Electronics') or contains(text(), 'Antiques') or contains(text(), 'Arts') or contains(text(), 'Vehicle') or contains(text(), 'Mobile')]")
                        if dropdown_options:
                            dropdown_opened = True
                            print(f"[OK] Dropdown opened - found {len(dropdown_options)} category options")
                        else:
                            # Alternative check - look for any list of options that appeared
                            all_options = self.driver.find_elements(By.XPATH, "//div[contains(@style, 'position') or contains(@role, 'listbox')]//span")
                            visible_options = [opt for opt in all_options if opt.is_displayed() and opt.text.strip()]
                            if len(visible_options) > 5:  # If we see many options, dropdown probably opened
                                dropdown_opened = True
                                print(f"[OK] Dropdown likely opened - found {len(visible_options)} visible options")
                    except Exception as e:
                        print(f"Could not verify dropdown status: {e}")
                    
                    if not dropdown_opened:
                        print("[WARNING] Dropdown may not have opened, trying alternative approach")
                        # Try typing in the category field to trigger dropdown
                        try:
                            input_field = category_button.find_element(By.XPATH, ".//input")
                            input_field.clear()
                            input_field.send_keys(fb_category[:3])  # Type first 3 letters to trigger dropdown
                            time.sleep(2)
                            print(f"[OK] Typed '{fb_category[:3]}' to trigger dropdown")
                        except Exception:
                            print("[WARNING] Could not type in category field either")

                    # Refresh elements to avoid stale references and get real category options
                    time.sleep(1)  # Let DOM settle
                    
                    # Get fresh category options that are actually categories
                    category_options = []
                    try:
                        # Look for elements that appear after clicking category dropdown
                        all_spans = self.driver.find_elements(By.XPATH, "//span[string-length(text()) > 2 and string-length(text()) < 50]")
                        
                        # Known Facebook category names to look for
                        known_categories = [
                            'Electronics', 'Antiques and collectibles', 'Arts and crafts', 'Vehicle parts and accessories',
                            'Baby products', 'Books, films and music', 'Mobile phones and accessories', 
                            'Clothing, shoes and accessories', 'Home and garden', 'Sports and outdoors',
                            'Tools and hardware', 'Musical instruments', 'Pet supplies', 'Toys and games',
                            'Health and beauty', 'Jewellery and watches', 'Computers and software'
                        ]
                        
                        for span in all_spans:
                            try:
                                if span.is_displayed():
                                    text = span.text.strip()
                                    # Check if this looks like a category
                                    if any(cat.lower() in text.lower() or text.lower() in cat.lower() for cat in known_categories):
                                        category_options.append((span, text))
                            except:
                                continue
                        
                        # If we don't find known categories, look for clickable spans in dropdown areas
                        if not category_options:
                            dropdown_spans = self.driver.find_elements(By.XPATH, "//div[contains(@role, 'listbox') or contains(@class, 'menu')]//span | //div[contains(@style, 'position') and contains(@style, 'absolute')]//span")
                            for span in dropdown_spans:
                                try:
                                    if span.is_displayed():
                                        text = span.text.strip()
                                        if (len(text) > 3 and len(text) < 50 and 
                                            not text.isdigit() and 
                                            'notification' not in text.lower() and
                                            'unread' not in text.lower() and
                                            text not in ['Photos', 'Videos', 'Add photos', 'Add video', 'Save Draft']):
                                            category_options.append((span, text))
                                except:
                                    continue
                    
                    except Exception as e:
                        print(f"Error getting category options: {e}")
                    
                    print(f"Found {len(category_options)} category options: {[text for _, text in category_options[:10]]}")
                    
                    if not category_options:
                        print("[WARNING] No category options found")
                        raise Exception("No category options available")
                    
                    # Use Gemini to pick the best option from what's actually available
                    selected_category = None
                    if self.gemini_model and len(category_options) > 0:
                        try:
                            option_texts = [text for _, text in category_options[:15]]  # Limit to first 15 to avoid token limits
                            prompt = f"""
                            Given the product: '{listing_data.get('title', '')}' 
                            Description: '{listing_data.get('description', '')[:100]}...'
                            
                            Choose the BEST category from this exact list:
                            {', '.join(option_texts)}
                            
                            Return ONLY the exact text from the list, nothing else.
                            """
                            
                            response = self.gemini_model.generate_content(prompt)
                            if response and hasattr(response, 'text') and response.text:
                                gemini_choice = response.text.strip()
                                print(f"Gemini suggested: '{gemini_choice}'")
                                
                                # Find the option that matches Gemini's choice
                                for span, text in category_options:
                                    if gemini_choice.lower() in text.lower() or text.lower() in gemini_choice.lower():
                                        selected_category = (span, text)
                                        break
                        
                        except Exception as e:
                            print(f"Gemini category selection error: {e}")
                    
                    # If Gemini didn't pick or failed, use similarity matching
                    if not selected_category:
                        best_span = None
                        best_score = 0.0
                        for span, text in category_options:
                            score = SequenceMatcher(None, text.lower(), fb_category.lower()).ratio()
                            if score > best_score:
                                best_score = score
                                best_span = (span, text)
                        selected_category = best_span
                    
                    # Click the selected category
                    if selected_category:
                        span, text = selected_category
                        try:
                            # Scroll element into view
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", span)
                            time.sleep(0.5)
                            
                            # Try clicking
                            span.click()
                            print(f"[OK] Selected category: '{text}'")
                            time.sleep(2)
                        except Exception as e:
                            print(f"Failed to click category '{text}': {e}")
                            # Try JavaScript click as fallback
                            try:
                                self.driver.execute_script("arguments[0].click();", span)
                                print(f"[OK] Selected category with JS click: '{text}'")
                                time.sleep(2)
                            except Exception as e2:
                                print(f"Failed JS click too: {e2}")
                    else:
                        print("[WARNING] Could not find a suitable category to select")

                    # Handle nested category selection (can be n-levels deep)
                    self._handle_nested_category_selection(listing_data)
                    
                except Exception as e:
                    print(f"[WARNING] Could not select category/subcategory: {e}")
            except Exception as e:
                print(f"[WARNING] Could not select category/subcategory: {e}")
            
            # Condition - handle the dropdown properly with better element detection
            try:
                # Wait a bit for page to settle after category/subcategory selection
                time.sleep(2)
                
                # Try multiple approaches to find condition dropdown
                condition_dropdown = None
                condition_selectors = [
                    "//label[@role='combobox' and .//span[text()='Condition']]",
                    "//span[text()='Condition']/ancestor::label[@role='combobox']",
                    "//div[.//span[text()='Condition'] and @role='combobox']",
                    "//label[contains(@class, 'x78zum5') and .//span[text()='Condition']]"
                ]
                
                for selector in condition_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements:
                            condition_dropdown = elements[0]
                            print(f"[OK] Found condition dropdown with selector: {selector}")
                            break
                    except:
                        continue
                
                if condition_dropdown:
                    # Scroll into view and wait
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", condition_dropdown)
                    time.sleep(1)
                    
                    # Try clicking with different methods
                    try:
                        condition_dropdown.click()
                        print("[OK] Clicked condition dropdown")
                    except Exception:
                        try:
                            self.driver.execute_script("arguments[0].click();", condition_dropdown)
                            print("[OK] Clicked condition dropdown with JS")
                        except Exception:
                            print("[WARNING] Could not click condition dropdown")
                            raise Exception("Condition dropdown click failed")
                    
                    time.sleep(2)
                    
                    # Map conditions to Facebook options
                    condition_map = {
                        'new': 'New',
                        'like_new': 'Used – like new',
                        'good': 'Used – good', 
                        'fair': 'Used – fair',
                        'poor': 'Used – fair',
                        'used': 'Used – good'  # Default
                    }
                    
                    fb_condition = condition_map.get(listing_data.get('condition', 'used'), 'Used – good')
                    
                    # Wait for condition options to appear and select
                    try:
                        condition_option = wait.until(
                            EC.element_to_be_clickable((By.XPATH, f"//span[text()='{fb_condition}']"))
                        )
                        condition_option.click()
                        print(f"[OK] Selected condition: {fb_condition}")
                    except TimeoutException:
                        print(f"[WARNING] Could not find condition option: {fb_condition}")
                else:
                    print("[WARNING] Could not find condition dropdown")
                
            except Exception as e:
                print(f"[WARNING] Could not set condition: {e}")
            
            # Description - using the textarea structure you provided
            try:
                description_field = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Description']/ancestor::label//textarea | //textarea[@id[contains(., '_r_')]]"))
                )
                description_field.clear()
                description_field.send_keys(listing_data['description'])
            except TimeoutException:
                return {'error': 'Could not find description field', 'platform': 'facebook'}
            
            # Upload the first image from Downloads folder
            import glob
            import os
            downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
            image_files = glob.glob(os.path.join(downloads_folder, '*.jpg')) + glob.glob(os.path.join(downloads_folder, '*.png'))
            if image_files:
                image_path = image_files[0]
                try:
                    file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                    file_input.send_keys(image_path)
                    time.sleep(2)  # Wait for upload
                    print(f"[OK] Uploaded image: {image_path}")
                except Exception as e:
                    print(f"[WARNING] Could not upload photo: {e}")
            else:
                print("[WARNING] No image found in Downloads folder to upload.")

            # Click the publish button to complete the listing
            try:
                publish_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Publish']"))
                )
                
                # Check if button is disabled first
                is_disabled = publish_button.get_attribute('aria-disabled') == 'true'
                if is_disabled:
                    return {
                        'success': True,
                        'platform': 'facebook',
                        'status': 'form_completed_needs_images',
                        'message': 'Facebook listing form completed but publish button is disabled. Check if all required fields are filled.'
                    }
                
                # Scroll to publish button and click it
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", publish_button)
                time.sleep(1)
                
                try:
                    publish_button.click()
                    print("[OK] Clicked Publish button!")
                    time.sleep(3)  # Wait for publish to process
                    
                    # Handle "Leave Page?" confirmation dialog if it appears
                    try:
                        print("🔍 Checking for 'Leave Page?' confirmation dialog...")
                        
                        # Look for the "Leave Page" button with specific selectors
                        leave_page_selectors = [
                            "//div[@aria-label='Leave Page']",
                            "//div[contains(@class, 'x1i10hfl') and @aria-label='Leave Page']",
                            "//span[text()='Leave Page']/ancestor::div[@role='button']",
                            "//span[contains(text(), 'Leave Page')]/ancestor::div[@role='button']",
                            "//div[@role='button' and .//span[text()='Leave Page']]"
                        ]
                        
                        leave_page_button = None
                        for selector in leave_page_selectors:
                            try:
                                elements = self.driver.find_elements(By.XPATH, selector)
                                if elements and elements[0].is_displayed():
                                    leave_page_button = elements[0]
                                    print(f"[OK] Found 'Leave Page' button with selector: {selector}")
                                    break
                            except Exception:
                                continue
                        
                        if leave_page_button:
                            print("🖱️ Clicking 'Leave Page' to continue...")
                            try:
                                leave_page_button.click()
                                print("[OK] Successfully clicked 'Leave Page' button")
                                time.sleep(2)
                            except Exception:
                                try:
                                    self.driver.execute_script("arguments[0].click();", leave_page_button)
                                    print("[OK] Successfully clicked 'Leave Page' button with JavaScript")
                                    time.sleep(2)
                                except Exception as e:
                                    print(f"[WARNING] Failed to click 'Leave Page' button: {e}")
                        else:
                            print("📝 No 'Leave Page' dialog found, continuing...")
                            
                    except Exception as e:
                        print(f"[WARNING] Error handling 'Leave Page' dialog: {e}")
                    
                    time.sleep(2)  # Additional wait after handling dialog
                    
                    # Check if listing was successfully published
                    try:
                        # First, handle any remaining confirmation dialogs
                        self.handle_facebook_confirmation_dialogs()
                        
                        # Look for success indicators or redirect to marketplace
                        current_url = self.driver.current_url
                        if 'marketplace' in current_url and 'create' not in current_url:
                            return {
                                'success': True,
                                'platform': 'facebook',
                                'status': 'published',
                                'message': 'Facebook listing published successfully!',
                                'listing_url': current_url
                            }
                        else:
                            # Wait a bit more and check again
                            time.sleep(3)
                            # Handle any additional dialogs that might appear
                            self.handle_facebook_confirmation_dialogs()
                            current_url = self.driver.current_url
                            return {
                                'success': True,
                                'platform': 'facebook',
                                'status': 'publish_attempted',
                                'message': 'Publish button clicked. Please verify listing was created.',
                                'current_url': current_url
                            }
                    except Exception as e:
                        # Try to handle any dialogs one more time
                        self.handle_facebook_confirmation_dialogs()
                        return {
                            'success': True,
                            'platform': 'facebook',
                            'status': 'publish_attempted',
                            'message': 'Publish button clicked successfully. Listing should be live.'
                        }
                        
                except Exception as e:
                    # Try JavaScript click as fallback
                    try:
                        self.driver.execute_script("arguments[0].click();", publish_button)
                        print("[OK] Clicked Publish button with JavaScript!")
                        time.sleep(3)
                        
                        return {
                            'success': True,
                            'platform': 'facebook',
                            'status': 'published',
                            'message': 'Facebook listing published successfully with JS click!'
                        }
                    except Exception as e2:
                        print(f"[WARNING] Failed to click publish button: {e2}")
                        return {
                            'success': True,
                            'platform': 'facebook',
                            'status': 'ready_to_publish',
                            'message': 'Listing form completed. Please manually click Publish to complete.'
                        }
                        
            except TimeoutException:
                print("[WARNING] Could not find publish button")
                return {
                    'success': True,
                    'platform': 'facebook',
                    'status': 'form_filled',
                    'message': 'Facebook listing form completed successfully. Publish button may need manual click.'
                }
            
        except Exception as e:
            print(f"[ERROR] Facebook listing creation failed: {e}")
            return {'error': f'Facebook listing failed: {str(e)}', 'platform': 'facebook'}
    
    def create_ebay_listing(self, listing_data: Dict) -> Dict:
        """Create eBay listing using eBay API"""
        try:
            if not self.ebay_config['app_id']:
                return {'error': 'eBay API not configured', 'platform': 'ebay'}
            
            print("📝 Creating eBay listing via API...")
            
            # eBay API endpoint
            if self.ebay_config['sandbox']:
                base_url = "https://api.sandbox.ebay.com"
            else:
                base_url = "https://api.ebay.com"
            
            # Prepare listing data for eBay
            ebay_listing = {
                "Item": {
                    "Title": listing_data['title'][:80],  # eBay title limit
                    "Description": listing_data['description'],
                    "PrimaryCategory": {"CategoryID": "175672"},  # Electronics > Audio > Headphones (example)
                    "StartPrice": {
                        "currencyID": "USD",
                        "value": str(listing_data['price'])
                    },
                    "CategoryMappingAllowed": True,
                    "Country": "US",
                    "Currency": "USD",
                    "DispatchTimeMax": 3,
                    "ListingDuration": "Days_7",
                    "ListingType": "FixedPriceItem",
                    "PaymentMethods": ["PayPal"],
                    "PictureDetails": {
                        "GalleryType": "Gallery"
                    },
                    "Quantity": 1,
                    "ReturnPolicy": {
                        "ReturnsAcceptedOption": "ReturnsAccepted",
                        "RefundOption": "MoneyBack",
                        "ReturnsWithinOption": "Days_30"
                    },
                    "ShippingDetails": {
                        "ShippingType": "Flat",
                        "ShippingServiceOptions": [{
                            "ShippingServicePriority": 1,
                            "ShippingService": "USPSMedia",
                            "ShippingServiceCost": {
                                "currencyID": "USD", 
                                "value": "5.99"
                            }
                        }]
                    },
                    "Site": "US"
                }
            }
            
            # Map condition to eBay condition ID
            condition_map = {
                'new': '1000',
                'like_new': '1500', 
                'good': '3000',
                'fair': '4000',
                'poor': '5000',
                'used': '3000'
            }
            
            condition_id = condition_map.get(listing_data.get('condition', 'used'), '3000')
            ebay_listing["Item"]["ConditionID"] = condition_id
            
            # Headers for eBay API
            headers = {
                'X-EBAY-API-SITEID': '0',
                'X-EBAY-API-COMPATIBILITY-LEVEL': '967',
                'X-EBAY-API-CALL-NAME': 'AddFixedPriceItem',
                'X-EBAY-API-APP-NAME': self.ebay_config['app_id'],
                'X-EBAY-API-DEV-NAME': self.ebay_config['dev_id'],
                'X-EBAY-API-CERT-NAME': self.ebay_config['cert_id'],
                'Content-Type': 'text/xml'
            }
            
            # XML request body
            xml_request = f"""<?xml version="1.0" encoding="utf-8"?>
<AddFixedPriceItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
    <RequesterCredentials>
        <eBayAuthToken>{self.ebay_config['user_token']}</eBayAuthToken>
    </RequesterCredentials>
    <Item>
        <Title>{listing_data['title'][:80]}</Title>
        <Description><![CDATA[{listing_data['description']}]]></Description>
        <PrimaryCategory>
            <CategoryID>175672</CategoryID>
        </PrimaryCategory>
        <StartPrice currencyID="USD">{listing_data['price']}</StartPrice>
        <CategoryMappingAllowed>true</CategoryMappingAllowed>
        <ConditionID>{condition_id}</ConditionID>
        <Country>US</Country>
        <Currency>USD</Currency>
        <DispatchTimeMax>3</DispatchTimeMax>
        <ListingDuration>Days_7</ListingDuration>
        <ListingType>FixedPriceItem</ListingType>
        <Quantity>1</Quantity>
        <ReturnPolicy>
            <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
            <RefundOption>MoneyBack</RefundOption>
            <ReturnsWithinOption>Days_30</ReturnsWithinOption>
        </ReturnPolicy>
        <ShippingDetails>
            <ShippingType>Flat</ShippingType>
            <ShippingServiceOptions>
                <ShippingServicePriority>1</ShippingServicePriority>
                <ShippingService>USPSMedia</ShippingService>
                <ShippingServiceCost currencyID="USD">5.99</ShippingServiceCost>
            </ShippingServiceOptions>
        </ShippingDetails>
        <Site>US</Site>
    </Item>
</AddFixedPriceItemRequest>"""
            
            # Make API request
            response = requests.post(
                f"{base_url}/ws/api.dll",
                headers=headers,
                data=xml_request,
                timeout=30
            )
            
            if response.status_code == 200:
                # Parse XML response (simplified)
                if 'Success' in response.text:
                    # Extract item ID from response if needed
                    import re
                    item_match = re.search(r'<ItemID>(\d+)</ItemID>', response.text)
                    item_id = item_match.group(1) if item_match else None
                    
                    return {
                        'success': True,
                        'platform': 'ebay',
                        'item_id': item_id,
                        'status': 'listed',
                        'message': f'eBay listing created successfully. Item ID: {item_id}'
                    }
                else:
                    return {
                        'error': 'eBay API returned error',
                        'platform': 'ebay',
                        'details': response.text
                    }
            else:
                return {
                    'error': f'eBay API request failed: {response.status_code}',
                    'platform': 'ebay'
                }
            
        except Exception as e:
            print(f"[ERROR] eBay listing creation failed: {e}")
            return {'error': f'eBay listing failed: {str(e)}', 'platform': 'ebay'}
    
    def create_listings(self, product_data: Dict, pricing_data: Dict, platforms: List[str]) -> Dict:
        """Create listings on specified platforms"""
        results = {}
        
        # Generate optimal listing data
        condition = product_data.get('condition', 'used')
        optimal_price = self.calculate_optimal_price(pricing_data, condition)
        description = self.generate_description(
            product_data.get('name', 'Unknown Product'),
            pricing_data,
            condition
        )
        
        listing_data = {
            'title': product_data.get('name', 'Unknown Product')[:75],  # Limit for platforms
            'price': optimal_price,
            'condition': condition,
            'description': description,
            'category': product_data.get('category', 'Electronics')
        }
        
        print(f"📋 Creating listings for: {listing_data['title']} at ${optimal_price}")
        
        # Create Facebook listing
        if 'facebook' in platforms:
            fb_result = self.create_facebook_listing(listing_data)
            results['facebook'] = fb_result
        
        # Create eBay listing
        if 'ebay' in platforms:
            ebay_result = self.create_ebay_listing(listing_data)
            results['ebay'] = ebay_result
        
        return {
            'listings': results,
            'listing_data': listing_data,
            'platforms_attempted': platforms
        }
    
    def start_facebook_message_monitoring(self):
        """Start Facebook message monitoring in background thread"""
        try:
            from facebook_monitor import FacebookMessageMonitor
            
            print("[ROCKET] Starting Facebook message monitoring...")
            
            monitor = FacebookMessageMonitor()
            monitor.lister = self  # Use this lister's browser session
            
            # Start monitoring in background thread
            monitor_thread = threading.Thread(target=monitor.start_monitoring)
            monitor_thread.daemon = True  # Dies when main program exits
            monitor_thread.start()
            
            print("[OK] Facebook message monitor started in background")
            return monitor
            
        except Exception as e:
            print(f"[ERROR] Failed to start message monitor: {e}")
            return None
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                print("[FIRE] Browser closed")
            except:
                pass

# Initialize global lister
lister = MarketplaceLister()

# === API ROUTES ===

@app.route('/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'OK',
        'service': 'marketplace_listing_api',
        'timestamp': datetime.now().isoformat(),
        'browser_ready': lister.driver is not None,
        'facebook_logged_in': lister.facebook_logged_in,
        'gemini_available': lister.gemini_model is not None,
        'ebay_configured': bool(lister.ebay_config['app_id']),
        'version': '1.0.0'
    })

@app.route('/api/facebook/login', methods=['POST'])
def facebook_login():
    """Trigger Facebook login process"""
    try:
        success = lister.ensure_facebook_access()
        
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

@app.route('/api/listings/create', methods=['POST'])
def create_listings():
    """
    Create marketplace listings
    
    Body:
    {
        "product": {
            "name": "Anker Soundcore Liberty 4 NC",
            "condition": "used",
            "category": "Electronics"
        },
        "pricing_data": {pricing data from price scraper},
        "platforms": ["facebook", "ebay"],
        "images": ["base64_image_data"] // optional for now
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'ok': False,
                'error_code': 'INVALID_REQUEST',
                'message': 'JSON request body required'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'product' not in data:
            return jsonify({
                'ok': False,
                'error_code': 'MISSING_PRODUCT_DATA',
                'message': 'Product data is required'
            }), 400
        
        if 'pricing_data' not in data:
            return jsonify({
                'ok': False,
                'error_code': 'MISSING_PRICING_DATA',
                'message': 'Pricing data is required'
            }), 400
        
        # Extract parameters
        product_data = data['product']
        pricing_data = data['pricing_data']
        platforms = data.get('platforms', ['facebook', 'ebay'])
        
        # Validate platforms
        valid_platforms = ['facebook', 'ebay']
        platforms = [p for p in platforms if p in valid_platforms]
        
        if not platforms:
            return jsonify({
                'ok': False,
                'error_code': 'NO_VALID_PLATFORMS',
                'message': f'Valid platforms are: {valid_platforms}'
            }), 400
        
        # Create listings
        result = lister.create_listings(product_data, pricing_data, platforms)
        
        # Check if any listings succeeded
        successes = [r for r in result['listings'].values() if r.get('success')]
        errors = [r for r in result['listings'].values() if 'error' in r]
        
        return jsonify({
            'ok': True,
            'data': {
                'listings': result['listings'],
                'listing_data': result['listing_data'],
                'summary': {
                    'platforms_attempted': len(platforms),
                    'successful_listings': len(successes),
                    'failed_listings': len(errors)
                }
            },
            'diagnostics': {
                'platforms_attempted': result['platforms_attempted'],
                'gemini_used': lister.gemini_model is not None,
                'provider': 'marketplace_listing_api_v1'
            }
        })
    
    except Exception as e:
        print(f"[ERROR] API error: {e}")
        return jsonify({
            'ok': False,
            'error_code': 'INTERNAL_ERROR',
            'message': 'Listing creation failed'
        }), 500

@app.route('/api/listings/facebook', methods=['POST'])
def create_facebook_listing_only():
    """Create Facebook listing only"""
    try:
        data = request.get_json()
        
        if not data or 'product' not in data or 'pricing_data' not in data:
            return jsonify({
                'ok': False,
                'error_code': 'INVALID_DATA',
                'message': 'Product and pricing data required'
            }), 400
        
        result = lister.create_listings(
            data['product'], 
            data['pricing_data'], 
            ['facebook']
        )
        
        fb_result = result['listings'].get('facebook', {})
        
        return jsonify({
            'ok': fb_result.get('success', False),
            'data': fb_result,
            'listing_data': result['listing_data']
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@app.route('/api/listings/ebay', methods=['POST'])
def create_ebay_listing_only():
    """Create eBay listing only"""
    try:
        data = request.get_json()
        
        if not data or 'product' not in data or 'pricing_data' not in data:
            return jsonify({
                'ok': False,
                'error_code': 'INVALID_DATA',
                'message': 'Product and pricing data required'
            }), 400
        
        result = lister.create_listings(
            data['product'], 
            data['pricing_data'], 
            ['ebay']
        )
        
        ebay_result = result['listings'].get('ebay', {})
        
        return jsonify({
            'ok': ebay_result.get('success', False),
            'data': ebay_result,
            'listing_data': result['listing_data']
        })
    
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@app.route('/api/facebook/start-monitoring', methods=['POST'])
def start_facebook_monitoring():
    """Start Facebook message monitoring"""
    try:
        # Use your existing lister instance
        monitor = lister.start_facebook_message_monitoring()
        
        if monitor:
            return jsonify({
                'ok': True,
                'message': 'Facebook message monitoring started',
                'status': 'monitoring'
            })
        else:
            return jsonify({
                'ok': False,
                'error': 'Failed to start monitoring'
            }), 500
            
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@app.route('/api/facebook/monitor-status', methods=['GET'])
def get_monitor_status():
    """Get current monitoring status"""
    # Simple status check
    return jsonify({
        'ok': True,
        'status': 'running',  # You can make this more sophisticated
        'last_check': datetime.now().isoformat()
    })

# === MAIN ===

if __name__ == '__main__':
    print("[CART] Marketplace Listing API v1.0")
    print("=" * 50)
    print("[GLOBE] Server: http://localhost:3003")
    print("📝 Create Listings: POST /api/listings/create")
    print("📘 Facebook Only: POST /api/listings/facebook")  
    print("📙 eBay Only: POST /api/listings/ebay")
    print("[LOCK] FB Login: POST /api/facebook/login")
    print("[PHONE] Start Monitor: POST /api/facebook/start-monitoring")
    print("[CHART] Monitor Status: GET /api/facebook/monitor-status")
    print("❤️  Health: GET /health")
    print()
    print("[SPARKLES] Features:")
    print("  - Facebook Marketplace automation (Selenium)")
    print("  - eBay API integration for listings")
    print("  - AI-generated descriptions (Gemini)")
    print("  - Intelligent pricing based on market data")
    print("  - Anti-detection browser settings")
    print("  - Cookie-based login persistence")
    print("  🆕 - Facebook message monitoring")
    print()
    print("⚙️  Setup:")
    print("  1. Add eBay API credentials to .env")
    print("  2. Run Facebook login on first use")
    print("  3. Integrate with image recognition & price scraper")
    print("  4. Start Facebook message monitoring")
    print("[ROCKET] Ready for hackathon!")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=3003)
    except Exception as e:
        print(f"[ERROR] Server error: {e}")
    finally:
        lister.close()