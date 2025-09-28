#!/usr/bin/env python3
"""
eBay Listing Automation API - IMPROVED VERSION v2.1
- Better required field detection based on actual eBay structure
- Gemini AI for intelligent field completion
- Focus on only required fields (not 21 recommended ones)
- Enhanced HTML debugging capabilities
- NEW: AI-guided post-listing flow handling
- NEW: Automatic verification step navigation (phone, confirmation, etc.)
- NEW: Intelligent HTML analysis and LLM-powered decision making
"""

import os
from dotenv import load_dotenv
import time
import re
import json
import random
import glob
import tempfile
import statistics
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from webdriver_manager.chrome import ChromeDriverManager

# Gemini for description generation and field completion
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    print("✅ Gemini AI available for description generation and field completion")
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Gemini AI not available")

app = Flask(__name__)
CORS(app)

class EbayAutomatorImproved:
    def __init__(self):
        self.driver = None
        self.profile_path = os.path.abspath('chrome_profile_ebay')
        self.ebay_logged_in = False
        self.gemini_model = None
        self.setup_gemini()
        print("🛒 eBay Automator IMPROVED initialized")
    
    def setup_gemini(self):
        """Initialize Gemini AI for description generation and field completion"""
        if not GEMINI_AVAILABLE:
            return

        load_dotenv()
        key = os.getenv('GEMINI_API_KEY')
        if key and key.strip() and key != 'your_api_key_here':
            try:
                genai.configure(api_key=key.strip())
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                # Test the model
                test = self.gemini_model.generate_content("Test")
                if test and test.text:
                    print(f"✅ Gemini AI configured successfully: {key[:8]}...")
                    return
            except Exception as e:
                print(f"⚠️ Gemini key failed {key[:8]}...: {e}")
                return

        print("⚠️ No working Gemini API key found")
    
    def save_debug_html(self, stage_name: str) -> str:
        """Save current page HTML for debugging with detailed info"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"ebay_{stage_name}_debug_{timestamp}.html"
            html_path = os.path.join(os.getcwd(), html_filename)
            
            html_content = self.driver.page_source
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"📄 {stage_name.upper()} HTML saved to: {html_path}")
            print(f"📊 HTML size: {len(html_content):,} characters")
            print(f"🌐 URL: {self.driver.current_url}")
            print(f"📖 Title: {self.driver.title}")
            
            return html_path
            
        except Exception as e:
            print(f"⚠️ Error saving debug HTML for {stage_name}: {e}")
            return None
    
    def extract_key_html_elements(self) -> str:
        """Extract key HTML elements for LLM analysis using regex patterns"""
        try:
            html_content = self.driver.page_source
            
            # Extract important elements using regex patterns
            patterns = {
                'buttons': r'<button[^>]*>([^<]+)</button>',
                'inputs': r'<input[^>]*(?:type=["\']([^"\'\/]*)["\'][^>]*)?(?:placeholder=["\']([^"\'\/]*)["\'][^>]*)?[^>]*>',
                'forms': r'<form[^>]*>(.*?)</form>',
                'links': r'<a[^>]*href=["\']([^"\'\/]*)["\'][^>]*>([^<]+)</a>',
                'headings': r'<h[1-6][^>]*>([^<]+)</h[1-6]>',
                'error_messages': r'<[^>]*(?:class=["\'][^"\'\/]*(?:error|warning|alert|danger)[^"\'\/]*["\']|style=["\'][^"\'\/]*color\s*:\s*red[^"\'\/]*["\'])[^>]*>([^<]+)</',
                'modal_content': r'<[^>]*(?:class=["\'][^"\'\/]*modal[^"\'\/]*["\']|role=["\']dialog["\'])[^>]*>(.*?)</[^>]*>',
                'progress_indicators': r'<[^>]*(?:class=["\'][^"\'\/]*(?:progress|step|wizard)[^"\'\/]*["\'])[^>]*>([^<]+)</',
                'verification_elements': r'<[^>]*(?:class=["\'][^"\'\/]*(?:verify|confirm|phone|code)[^"\'\/]*["\'])[^>]*>([^<]*)</',
                'navigation_elements': r'<[^>]*(?:class=["\'][^"\'\/]*(?:nav|menu|breadcrumb)[^"\'\/]*["\'])[^>]*>([^<]*)</',
                'text_content': r'<(?:p|span|div)[^>]*>([^<]{20,100})</(?:p|span|div)>'
            }
            
            extracted = {}
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
                if matches:
                    # Clean and filter matches
                    clean_matches = []
                    for match in matches[:20]:  # Limit to avoid overwhelming LLM
                        if isinstance(match, tuple):
                            match_text = ' '.join(filter(None, match))
                        else:
                            match_text = match
                        
                        # Clean the text
                        match_text = re.sub(r'\s+', ' ', match_text).strip()
                        if len(match_text) > 3 and match_text not in clean_matches:
                            clean_matches.append(match_text)
                    
                    extracted[pattern_name] = clean_matches
            
            # Build summary for LLM
            summary = f"PAGE ANALYSIS:\nURL: {self.driver.current_url}\nTitle: {self.driver.title}\n\n"
            
            for element_type, elements in extracted.items():
                if elements:
                    summary += f"{element_type.upper()}:\n"
                    for elem in elements[:10]:  # Top 10 most relevant
                        summary += f"- {elem}\n"
                    summary += "\n"
            
            return summary
            
        except Exception as e:
            print(f"⚠️ Error extracting HTML elements: {e}")
            return f"URL: {self.driver.current_url}\nTitle: {self.driver.title}\nError extracting details: {str(e)}"
    
    def get_llm_guidance(self, html_summary: str, context: str = "post_listing") -> Dict:
        """Get LLM guidance on what action to take next"""
        try:
            if not self.gemini_model:
                return {'action': 'wait', 'element': None, 'reason': 'No LLM available'}
            
            prompt = f"""You are an expert eBay automation assistant. I need you to analyze the current page and tell me what action to take next.

CONTEXT: {context}
The user just clicked "List it" on eBay and may encounter verification steps, confirmations, or other requirements.

CURRENT PAGE ANALYSIS:
{html_summary}

Your task: Analyze this page and determine the SINGLE MOST IMPORTANT action to take next.

Possible scenarios:
1. Phone verification required
2. Additional confirmation needed
3. Form field missing/error
4. Success page reached
5. Payment/fee confirmation
6. Terms acceptance required
7. Category selection needed
8. Waiting for processing

Respond with JSON format:
{{
  "action": "click|input|wait|success|error",
  "element": "exact text or description of element to interact with",
  "input_value": "value to enter if action is input",
  "reason": "brief explanation of why this action",
  "confidence": "high|medium|low",
  "wait_time": number_of_seconds_to_wait_if_action_is_wait
}}

Guidelines:
- Look for verification requirements (phone, email, etc.)
- Identify continue/confirm/accept buttons
- Watch for error messages that need addressing
- If you see success indicators, return "success"
- If unsure, choose "wait" with appropriate time
- Be specific about element text to click/interact with

Provide ONLY the JSON response:"""
            
            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                try:
                    # Extract JSON from response
                    json_text = response.text.strip()
                    # Remove markdown code blocks if present
                    if json_text.startswith('```'):
                        json_text = re.search(r'```(?:json)?\s*({.*?})\s*```', json_text, re.DOTALL)
                        if json_text:
                            json_text = json_text.group(1)
                    
                    guidance = json.loads(json_text)
                    print(f"🤖 LLM Guidance: {guidance.get('action')} - {guidance.get('reason')}")
                    return guidance
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️ LLM response not valid JSON: {response.text[:200]}")
                    return {'action': 'wait', 'element': None, 'reason': 'Invalid LLM response', 'wait_time': 5}
            
            return {'action': 'wait', 'element': None, 'reason': 'No LLM response', 'wait_time': 3}
            
        except Exception as e:
            print(f"⚠️ Error getting LLM guidance: {e}")
            return {'action': 'wait', 'element': None, 'reason': f'LLM error: {str(e)}', 'wait_time': 5}
    
    def execute_llm_action(self, guidance: Dict) -> bool:
        """Execute the action suggested by the LLM"""
        try:
            action = guidance.get('action', 'wait')
            element_text = guidance.get('element')
            input_value = guidance.get('input_value')
            wait_time = guidance.get('wait_time', 3)
            
            wait = WebDriverWait(self.driver, 10)
            
            if action == 'click':
                if not element_text:
                    print("❌ No element specified for click action")
                    return False
                
                # Try multiple strategies to find the element
                selectors = [
                    f"//button[contains(text(), '{element_text}')]",
                    f"//a[contains(text(), '{element_text}')]",
                    f"//input[@value='{element_text}']",
                    f"//*[contains(text(), '{element_text}') and (self::button or self::a or self::input)]",
                    f"//*[contains(@class, 'btn') and contains(text(), '{element_text}')]",
                    f"//*[contains(@onclick, '{element_text.lower()}') or contains(@id, '{element_text.lower()}')]"
                ]
                
                for selector in selectors:
                    try:
                        element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                        time.sleep(1)
                        element.click()
                        print(f"✅ Clicked: {element_text}")
                        time.sleep(2)
                        return True
                    except TimeoutException:
                        continue
                
                print(f"❌ Could not find clickable element: {element_text}")
                return False
            
            elif action == 'input':
                if not element_text or not input_value:
                    print("❌ Missing element or input value for input action")
                    return False
                
                # Try to find input field
                selectors = [
                    f"//input[contains(@placeholder, '{element_text}')]",
                    f"//input[contains(@name, '{element_text.lower()}')]",
                    f"//input[contains(@id, '{element_text.lower()}')]",
                    f"//input[@type='text' or @type='tel' or @type='email']",
                    "//input[not(@type) or @type='text']"
                ]
                
                for selector in selectors:
                    try:
                        input_elem = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        input_elem.clear()
                        input_elem.send_keys(input_value)
                        print(f"✅ Entered '{input_value}' in {element_text}")
                        time.sleep(1)
                        return True
                    except TimeoutException:
                        continue
                
                print(f"❌ Could not find input field: {element_text}")
                return False
            
            elif action == 'wait':
                print(f"⏳ Waiting {wait_time} seconds as suggested by LLM")
                time.sleep(wait_time)
                return True
            
            elif action == 'success':
                print("🎉 LLM detected successful completion!")
                return True
            
            elif action == 'error':
                print(f"❌ LLM detected error: {guidance.get('reason')}")
                return False
            
            else:
                print(f"⚠️ Unknown action: {action}")
                return False
                
        except Exception as e:
            print(f"❌ Error executing LLM action: {e}")
            return False
    
    def handle_post_listing_flow(self, max_steps: int = 10) -> Dict:
        """Handle post-listing flow with LLM guidance"""
        print("🚀 Starting intelligent post-listing flow...")
        
        for step in range(max_steps):
            print(f"\n🔄 Post-listing step {step + 1}/{max_steps}")
            
            # Wait for page to stabilize
            time.sleep(3)
            
            # Save debug HTML
            self.save_debug_html(f"post_listing_step_{step + 1}")
            
            # Extract key elements
            html_summary = self.extract_key_html_elements()
            
            # Get LLM guidance
            guidance = self.get_llm_guidance(html_summary, f"post_listing_step_{step + 1}")
            
            # Check for success conditions
            current_url = self.driver.current_url.lower()
            page_title = self.driver.title.lower()
            
            # Success indicators
            if any(indicator in current_url for indicator in ['success', 'confirmation', 'listed', 'complete']):
                print("🎉 Success detected in URL!")
                return {
                    'success': True,
                    'status': 'completed',
                    'message': 'Listing successfully completed!',
                    'final_url': self.driver.current_url,
                    'steps_completed': step + 1
                }
            
            if any(indicator in page_title for indicator in ['success', 'confirmation', 'listed', 'complete', 'congratulations']):
                print("🎉 Success detected in title!")
                return {
                    'success': True,
                    'status': 'completed',
                    'message': 'Listing successfully completed!',
                    'final_url': self.driver.current_url,
                    'steps_completed': step + 1
                }
            
            # Execute LLM action
            if guidance['action'] == 'success':
                print("🎉 LLM confirmed successful completion!")
                return {
                    'success': True,
                    'status': 'completed',
                    'message': 'LLM confirmed listing completion!',
                    'final_url': self.driver.current_url,
                    'steps_completed': step + 1
                }
            
            if guidance['action'] == 'error':
                return {
                    'success': False,
                    'status': 'error',
                    'message': f'LLM detected error: {guidance.get("reason")}',
                    'final_url': self.driver.current_url,
                    'steps_completed': step + 1
                }
            
            # Execute the suggested action
            action_success = self.execute_llm_action(guidance)
            
            if not action_success and guidance['action'] != 'wait':
                print(f"⚠️ Failed to execute action: {guidance['action']}")
                # Continue anyway, maybe the page changed
            
            # Check if we've been redirected to a different domain (possible completion)
            if 'ebay.com' not in current_url:
                print("🔄 Redirected away from eBay - assuming completion")
                return {
                    'success': True,
                    'status': 'completed_redirect',
                    'message': 'Redirected away from eBay, likely completed',
                    'final_url': self.driver.current_url,
                    'steps_completed': step + 1
                }
        
        # Max steps reached
        print(f"⚠️ Reached maximum steps ({max_steps}) without clear completion")
        return {
            'success': False,
            'status': 'timeout',
            'message': f'Reached maximum steps ({max_steps}) without completion',
            'final_url': self.driver.current_url,
            'steps_completed': max_steps
        }
    
    def get_intelligent_field_value(self, field_name: str, listing_data: Dict) -> str:
        """Use Gemini AI to intelligently determine field values based on product title and context"""
        try:
            if not self.gemini_model:
                # Fallback to basic logic
                return self.get_smart_field_value(field_name, listing_data)
            
            # Prepare context for Gemini
            product_title = listing_data.get('title', 'Unknown Product')
            field_name_clean = field_name.replace('attributes.', '')
            
            prompt = f"""You are an eBay listing expert. For the product "{product_title}", I need to fill the "{field_name_clean}" field.

Analyze the product title and provide the most appropriate value for this field. Be specific and accurate.

Product: {product_title}
Field to fill: {field_name_clean}

Guidelines:
- For Model: Extract the exact model name/number (e.g., "Liberty 4 NC" for Anker Soundcore Liberty 4 NC)
- For Connectivity: Choose from Bluetooth, Wired, USB-C, Lightning, 3.5mm, Wireless, etc.
- For Color: Choose from Black, White, Blue, Red, Silver, Gray, Gold, Pink, Green, etc.
- For Type: For audio devices choose from "Earbud (In Ear)", "Ear-Cup (Over the Ear)", "Ear-Pad (On the Ear)"
- For Brand: Extract the brand name (e.g., "Anker" for Anker products)
- For Features: Choose relevant features like Wireless, Noise Cancelling, Water Resistant, etc.
- Be concise and match eBay's expected format

Provide only the field value, nothing else:"""
            
            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                ai_value = response.text.strip()
                # Clean up the response
                ai_value = ai_value.replace('"', '').replace("'", '').strip()
                print(f"🤖 Gemini suggested for {field_name_clean}: {ai_value}")
                return ai_value
            
        except Exception as e:
            print(f"⚠️ Gemini field completion failed: {e}")
        
        # Fallback to original logic
        return self.get_smart_field_value(field_name, listing_data)
    
    def get_smart_field_value(self, field_name: str, listing_data: Dict) -> str:
        """Get intelligent value for a specific field based on field name and product data (fallback)"""
        field_name_lower = field_name.lower()
        title_lower = listing_data['title'].lower()
        
        if 'model' in field_name_lower:
            return self.extract_model_from_title(listing_data['title'])
        
        elif 'connectivity' in field_name_lower or 'connection' in field_name_lower:
            if any(word in title_lower for word in ['wireless', 'bluetooth', 'bt']):
                return 'Bluetooth'
            elif any(word in title_lower for word in ['usb-c', 'usb c', 'type-c']):
                return 'USB-C'
            else:
                return 'Bluetooth'  # Default for most modern devices
        
        elif 'color' in field_name_lower or 'colour' in field_name_lower:
            color_options = ['black', 'white', 'blue', 'red', 'silver', 'gray', 'grey', 'gold']
            for color in color_options:
                if color in title_lower:
                    return color.capitalize()
            return 'Black'  # Default fallback
        
        elif 'type' in field_name_lower:
            if any(word in title_lower for word in ['earbud', 'earphone']):
                return 'Earbud (In Ear)'
            elif any(word in title_lower for word in ['headphone', 'headset']):
                return 'Ear-Cup (Over the Ear)'
            else:
                return 'Earbud (In Ear)'
        
        else:
            return self.extract_generic_attribute(listing_data['title'])
    
    def extract_model_from_title(self, title: str) -> str:
        """Extract likely model name from product title"""
        try:
            title_lower = title.lower()
            
            # For Anker products
            if 'anker' in title_lower:
                words = title.split()
                anker_idx = next((i for i, word in enumerate(words) if word.lower() == 'anker'), -1)
                
                if anker_idx >= 0 and anker_idx < len(words) - 1:
                    model_words = []
                    for i in range(anker_idx + 1, min(len(words), anker_idx + 5)):
                        word = words[i]
                        if word.lower() in ['wireless', 'bluetooth', 'earbuds', 'headphones']:
                            break
                        model_words.append(word)
                        if len(model_words) >= 3:
                            break
                    
                    if model_words:
                        return ' '.join(model_words)
            
            # Fallback: return first few meaningful words
            words = title.split()
            for i, word in enumerate(words):
                if any(char.isdigit() for char in word) and len(word) <= 15:
                    model_words = [word]
                    if i > 0 and len(words[i-1]) <= 12:
                        model_words.insert(0, words[i-1])
                    if i < len(words) - 1:
                        model_words.append(words[i+1])
                    return ' '.join(model_words)
            
            return words[0] if words else 'Unknown'
            
        except Exception as e:
            print(f"⚠️ Error extracting model from title: {e}")
            return 'Unknown'
    
    def extract_generic_attribute(self, title: str) -> str:
        """Extract generic attribute value from title"""
        words = title.split()
        common_words = {'new', 'used', 'original', 'genuine', 'authentic', 'wireless', 'bluetooth'}
        for word in words[:3]:
            if len(word) > 2 and word.lower() not in common_words:
                return word
        return words[0] if words else 'Unknown'

    def start_browser(self, headless=False):
        """Start Chrome browser with optimal settings for eBay"""
        try:
            print("🌐 Starting Chrome browser for eBay...")
            
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

    def check_ebay_login(self) -> bool:
        """Check if we're logged into eBay"""
        try:
            print("🔍 Checking eBay login status...")
            
            self.driver.get("https://www.ebay.com/mye/myebay/summary")
            wait = WebDriverWait(self.driver, 10)
            
            current_url = self.driver.current_url.lower()
            page_title = self.driver.title.lower()
            
            if ("myebay" in current_url and 
                "signin" not in current_url and 
                ("my ebay" in page_title or "summary" in page_title)):
                
                print("✅ eBay login confirmed")
                self.ebay_logged_in = True
                return True
            
            print("🔐 eBay login required")
            return False
            
        except Exception as e:
            print(f"❌ Error checking eBay login: {e}")
            return False

    def ensure_ebay_access(self) -> bool:
        """Ensure eBay access (login if needed)"""
        if not self.driver:
            if not self.start_browser():
                return False
        
        return self.check_ebay_login()

    def identify_required_fields(self, attribute_buttons) -> tuple:
        """Enhanced required field identification based on eBay's actual structure"""
        required_fields = []
        optional_fields = []
        
        print("🔍 ANALYZING FIELDS TO IDENTIFY REQUIRED VS OPTIONAL...")
        print("📋 Using enhanced eBay-specific detection methods")
        
        # Critical fields that are ALWAYS required for eBay electronics listings
        # Based on your attachment image and eBay requirements
        CRITICAL_REQUIRED_FIELDS = ['Model', 'Connectivity', 'Color']
        
        for button in attribute_buttons:
            try:
                field_name = button.get_attribute('name') or 'unknown'
                button_text = button.text.strip() or '–'
                
                # Skip if already filled
                if button_text != '–' and button_text != '':
                    print(f"✅ Skipping {field_name} - already filled with: {button_text}")
                    continue
                
                is_required = False
                required_indicators = []
                
                # Method 1: Check against critical required fields
                field_name_clean = field_name.replace('attributes.', '')
                if field_name_clean in CRITICAL_REQUIRED_FIELDS:
                    is_required = True
                    required_indicators.append("critical_field")
                
                # Method 2: Look for eBay validation errors (red text, missing warnings)
                try:
                    # Scroll to field to make it visible
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(0.5)
                    
                    # Check for existing error messages near this field
                    parent_container = button.find_element(By.XPATH, "./ancestor::div[3]")
                    error_elements = parent_container.find_elements(By.XPATH, 
                        ".//*[contains(@class, 'error') or contains(@style, 'color: red') or contains(@style, 'color:#') or contains(text(), 'missing') or contains(text(), 'Add')]")
                    
                    for error_elem in error_elements:
                        error_text = error_elem.text.lower()
                        if any(keyword in error_text for keyword in ['missing', 'required', 'add', 'enter']):
                            is_required = True
                            required_indicators.append("validation_error")
                            break
                except Exception:
                    pass
                
                # Method 3: Common eBay required patterns for electronics
                ebay_required_patterns = ['model', 'connectivity', 'color', 'condition', 'brand']
                field_name_lower = field_name.lower().replace('attributes.', '')
                
                if any(pattern in field_name_lower for pattern in ebay_required_patterns):
                    is_required = True
                    required_indicators.append("ebay_pattern")
                
                # Method 4: Check if field is in "Required" section (eBay groups them)
                try:
                    # Look for section headers
                    section_elements = self.driver.find_elements(By.XPATH, 
                        "//h1[contains(text(), 'Required')] | //h2[contains(text(), 'Required')] | //*[contains(@class, 'required') and contains(@class, 'section')]")
                    
                    for section in section_elements:
                        # Check if button is within this required section
                        try:
                            section.find_element(By.XPATH, f".//button[@name='{field_name}']")
                            is_required = True
                            required_indicators.append("required_section")
                            break
                        except:
                            continue
                except Exception:
                    pass
                
                if is_required:
                    required_fields.append((button, field_name))
                    indicators_str = ", ".join(required_indicators)
                    print(f"✅ REQUIRED field: {field_name} (detected by: {indicators_str})")
                else:
                    optional_fields.append((button, field_name))
                    print(f"📋 Optional field: {field_name}")
                    
            except Exception as e:
                print(f"⚠️ Error analyzing field {field_name}: {e}")
                # When in doubt, check if it's critical
                field_lower = field_name.lower() if field_name else ''
                if any(critical in field_lower for critical in ['model', 'connectivity', 'color']):
                    required_fields.append((button, field_name))
                    print(f"⚠️ Added {field_name} to required (error fallback)")
                else:
                    optional_fields.append((button, field_name))
        
        print(f"🎯 ANALYSIS COMPLETE:")
        print(f"   📍 {len(required_fields)} REQUIRED fields identified")
        print(f"   📋 {len(optional_fields)} optional fields identified")
        
        return required_fields, optional_fields

    def fill_dropdown_field_enhanced(self, field_name: str, field_value: str, wait) -> bool:
        """Enhanced dropdown field filling with AI-powered suggestions"""
        try:
            print(f"   🔽 Filling dropdown {field_name} with: {field_value}")
            
            # Look for various types of input elements
            input_selectors = [
                f"input[name='search-box-{field_name.replace('attributes.', '')}']",
                f"input[name*='search-box'][name*='{field_name.split('.')[-1]}']",
                "input[name*='search-box']",
                "input[role='combobox']",
                "input[aria-autocomplete='list']",
                "input[type='text']"
            ]
            
            search_input = None
            for selector in input_selectors:
                try:
                    search_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"   ✅ Found input with: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if search_input:
                # Enhanced searchable dropdown strategy
                print(f"   📝 Using searchable dropdown for {field_name}")
                search_input.clear()
                search_input.send_keys(field_value)
                time.sleep(3)  # Wait for suggestions to populate
                
                # Multiple selection strategies with priorities
                selection_strategies = [
                    # Exact match (highest priority)
                    (f"//div[contains(@class, 'menu') or contains(@role, 'menu')]//*[text()='{field_value}']", "exact_match"),
                    # Case insensitive exact match
                    (f"//*[contains(@role, 'option') or contains(@class, 'menu')]//*[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{field_value.lower()}']", "case_insensitive"),
                    # Partial match (good fallback)
                    (f"//*[contains(@role, 'option') or contains(@class, 'menu')]//*[contains(text(), '{field_value[:8]}')]", "partial_match"),
                    # First valid suggestion
                    ("//*[contains(@role, 'option')][1] | //div[contains(@class, 'menu__item')][1] | //li[contains(@role, 'option')][1]", "first_suggestion")
                ]
                
                for xpath, strategy_name in selection_strategies:
                    try:
                        option = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                        option_text = option.text or option.get_attribute('aria-label') or 'Selected'
                        print(f"   ✅ Selected with {strategy_name}: {option_text}")
                        option.click()
                        time.sleep(1)
                        return True
                    except TimeoutException:
                        print(f"   ⚠️ {strategy_name} failed")
                        continue
                
                # Final fallback: try to add custom value
                try:
                    print("   🔄 Attempting custom value addition...")
                    search_input.send_keys(Keys.ENTER)
                    time.sleep(1)
                    print(f"   ✅ Added custom value via Enter: {field_value}")
                    return True
                except Exception as e:
                    print(f"   ❌ Custom value failed: {e}")
            
            print(f"   ❌ Could not fill {field_name} with any strategy")
            return False
            
        except Exception as e:
            print(f"   ❌ Error filling dropdown {field_name}: {e}")
            return False

    def create_ebay_listing_improved(self, listing_data: Dict) -> Dict:
        """Improved eBay listing creation focusing on required fields only"""
        try:
            if not self.ensure_ebay_access():
                return {'error': 'eBay access failed', 'platform': 'ebay'}
            
            print("📝 Creating eBay listing with IMPROVED method...")
            wait = WebDriverWait(self.driver, 15)
            
            # Navigate to eBay listing page
            self.driver.get("https://www.ebay.com/sl/prelist/suggest")
            
            # Fill in the search box
            try:
                search_input = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "textbox__control")))
                search_input.clear()
                search_input.send_keys(listing_data['title'])
                print(f"✅ Entered product title: {listing_data['title']}")
            except TimeoutException:
                return {'error': 'Could not find eBay search input', 'platform': 'ebay'}
            
            # Handle suggestions and continue
            try:
                time.sleep(2)
                suggestion = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.suggestion-list__item#option-0 button.item-button")))
                suggestion.click()
                print("✅ Clicked suggestion")
                time.sleep(1)
            except TimeoutException:
                print("⚠️ No suggestions found, continuing")
            
            # Click search button
            try:
                search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.keyword-suggestion__button.btn.btn--primary")))
                search_button.click()
                print("✅ Clicked search button")
                time.sleep(3)
            except TimeoutException:
                return {'error': 'Could not find eBay search button', 'platform': 'ebay'}
            
            # Continue without match
            try:
                continue_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.textual-display.btn.btn--secondary.prelist-radix__next-action")))
                continue_button.click()
                print("✅ Clicked 'Continue without match'")
                time.sleep(5)
                
                # Save debug HTML after transition
                self.save_debug_html("after_continue_improved")
                
            except TimeoutException:
                return {'error': 'Could not find continue without match button', 'platform': 'ebay'}
            
            # Handle condition selection
            try:
                condition_map = {'new': '1000', 'like_new': '1500', 'good': '3000', 'fair': '3000', 'poor': '7000', 'used': '3000'}
                condition_value = condition_map.get(listing_data.get('condition', 'used'), '3000')
                
                condition_text_map = {'1000': 'New', '1500': 'Open box', '3000': 'Used', '7000': 'For parts or not working'}
                condition_text = condition_text_map.get(condition_value, 'Used')
                
                condition_label = wait.until(EC.element_to_be_clickable((By.XPATH, f"//label[text()='{condition_text}']")))
                self.driver.execute_script("arguments[0].click();", condition_label)
                print(f"✅ Selected condition: {condition_text}")
                
                # Click continue in condition modal
                continue_modal_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.condition-dialog-radix__continue-btn:not([disabled])")))
                self.driver.execute_script("arguments[0].click();", continue_modal_btn)
                print("✅ Clicked continue in condition modal")
                time.sleep(3)
                
            except Exception as e:
                print(f"⚠️ Error in condition selection: {e}")
            
            # Fill title
            try:
                title_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Title']")))
                title_input.clear()
                title_input.send_keys(listing_data['title'][:80])
                print(f"✅ Entered title: {listing_data['title'][:80]}")
            except Exception as e:
                print(f"⚠️ Could not fill title: {e}")
            
            # Upload images
            try:
                downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
                image_files = (glob.glob(os.path.join(downloads_folder, '*.jpg')) + 
                              glob.glob(os.path.join(downloads_folder, '*.png')))
                
                if image_files:
                    image_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                    image_files = image_files[:3]
                    
                    file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                    if file_inputs:
                        file_input = file_inputs[0]
                        file_paths = '\n'.join(image_files)
                        file_input.send_keys(file_paths)
                        print(f"✅ Uploaded {len(image_files)} images")
                        time.sleep(10)  # Wait for upload processing
                
            except Exception as e:
                print(f"⚠️ Could not upload photos: {e}")
            
            # MAIN IMPROVEMENT: Handle ONLY required item specifics with AI
            try:
                print("🎯 FOCUSING ON REQUIRED ITEM SPECIFICS ONLY...")
                time.sleep(5)  # Ensure page is stable
                
                # Save debug HTML at this critical point
                self.save_debug_html("listing_form_improved")
                
                # Find all attribute buttons
                attribute_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[name^='attributes.']")
                print(f"📋 Found {len(attribute_buttons)} total attribute fields")
                
                if attribute_buttons:
                    # Use enhanced required field identification
                    required_fields, optional_fields = self.identify_required_fields(attribute_buttons)
                    
                    print(f"🚀 Processing ONLY the {len(required_fields)} REQUIRED fields (ignoring {len(optional_fields)} optional)")
                    
                    # Process ONLY required fields with AI assistance
                    for i, (button, field_name) in enumerate(required_fields):
                        try:
                            print(f"🔧 Processing REQUIRED field {i+1}/{len(required_fields)}: {field_name}")
                            
                            # Re-find button to avoid stale elements
                            current_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[name^='attributes.']")
                            button = None
                            for btn in current_buttons:
                                if btn.get_attribute('name') == field_name:
                                    button = btn
                                    break
                            
                            if not button:
                                print(f"⚠️ Could not re-find button for {field_name}")
                                continue
                            
                            # Scroll to field and click
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                            time.sleep(2)
                            
                            clickable_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(button))
                            clickable_button.click()
                            time.sleep(3)
                            
                            # Use AI to determine the best value
                            field_value = self.get_intelligent_field_value(field_name, listing_data)
                            print(f"🎯 Using AI-suggested value for {field_name}: {field_value}")
                            
                            # Fill the dropdown with enhanced method
                            success = self.fill_dropdown_field_enhanced(field_name, field_value, wait)
                            
                            if success:
                                print(f"✅ Successfully filled REQUIRED {field_name}: {field_value}")
                            else:
                                print(f"❌ FAILED to fill REQUIRED {field_name} - this may prevent listing!")
                            
                            # Close dropdown
                            self.driver.execute_script("document.body.click();")
                            time.sleep(2)
                            
                        except Exception as e:
                            print(f"❌ Error processing REQUIRED field {field_name}: {e}")
                            try:
                                self.driver.execute_script("document.body.click();")
                                time.sleep(1)
                            except:
                                pass
                            continue
                    
                    print(f"✅ Completed processing {len(required_fields)} REQUIRED fields")
                    print(f"⏭️ Skipped {len(optional_fields)} optional/recommended fields as requested")
                
            except Exception as e:
                print(f"⚠️ Error in item specifics handling: {e}")
            
            # Fill description (if available)
            if listing_data.get('description'):
                try:
                    # Try HTML editor first
                    html_toggle = self.driver.find_element(By.CSS_SELECTOR, "input.feature--editHtml")
                    if not html_toggle.is_selected():
                        html_toggle.click()
                        time.sleep(2)
                    
                    description_textarea = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".listRte__editorSource textarea")))
                    description_textarea.clear()
                    description_textarea.send_keys(listing_data['description'])
                    print("✅ Entered description")
                except Exception as e:
                    print(f"⚠️ Could not fill description: {e}")
            
            # Fill price
            try:
                price_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='price']")))
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", price_input)
                time.sleep(2)
                price_input.clear()
                price_input.send_keys(str(listing_data['price']))
                print(f"✅ Entered price: ${listing_data['price']}")
            except Exception as e:
                print(f"⚠️ Could not fill price: {e}")
            
            # Final step: List the item and handle post-listing flow
            try:
                print("🎯 Looking for List it button...")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                list_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-key='listItCallToAction']")))
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", list_button)
                time.sleep(2)
                
                if not list_button.get_attribute('disabled'):
                    list_button.click()
                    print("✅ Clicked 'List it' button")
                    time.sleep(5)
                    
                    # Start intelligent post-listing flow
                    print("🤖 Starting AI-guided post-listing flow to handle verification steps...")
                    post_listing_result = self.handle_post_listing_flow(max_steps=15)
                    
                    if post_listing_result['success']:
                        return {
                            'success': True,
                            'platform': 'ebay',
                            'status': 'completed',
                            'message': f'eBay listing completed successfully! {post_listing_result["message"]}',
                            'current_url': post_listing_result['final_url'],
                            'steps_completed': post_listing_result['steps_completed'],
                            'method': 'ai_guided_completion'
                        }
                    else:
                        return {
                            'success': False,
                            'platform': 'ebay',
                            'status': post_listing_result['status'],
                            'message': f'Post-listing flow incomplete: {post_listing_result["message"]}',
                            'current_url': post_listing_result['final_url'],
                            'steps_completed': post_listing_result['steps_completed'],
                            'error': 'post_listing_flow_failed'
                        }
                else:
                    print("⚠️ List it button is disabled - likely validation errors")
                    return {'error': 'List it button disabled - validation errors', 'platform': 'ebay'}
                    
            except TimeoutException:
                return {'error': 'Could not find List it button', 'platform': 'ebay'}
            
        except Exception as e:
            print(f"❌ eBay listing creation failed: {e}")
            return {'error': f'eBay listing failed: {str(e)}', 'platform': 'ebay'}
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                print("🔥 Browser closed")
            except:
                pass

# Initialize global automator
automator_improved = EbayAutomatorImproved()

# === API ROUTES ===

@app.route('/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'OK',
        'service': 'ebay_listing_automation_improved',
        'timestamp': datetime.now().isoformat(),
        'browser_ready': automator_improved.driver is not None,
        'ebay_logged_in': automator_improved.ebay_logged_in,
        'gemini_available': automator_improved.gemini_model is not None,
        'version': '2.0.0 - IMPROVED'
    })

@app.route('/api/ebay/listing', methods=['POST'])
def create_ebay_listing():
    """Create eBay listing using improved method"""
    try:
        if not request.is_json:
            return jsonify({
                'ok': False,
                'error_code': 'INVALID_REQUEST',
                'message': 'JSON request body required'
            }), 400
        
        data = request.get_json()
        
        if 'product' not in data or 'pricing_data' not in data:
            return jsonify({
                'ok': False,
                'error_code': 'MISSING_DATA',
                'message': 'Product and pricing data required'
            }), 400
        
        product_data = data['product']
        pricing_data = data['pricing_data']
        
        # Calculate optimal price
        def calculate_optimal_price(pricing_data: Dict, condition: str = "used") -> float:
            try:
                comps = pricing_data.get('comps', [])
                if not comps:
                    return 50.0
                
                condition_comps = [comp for comp in comps if comp['condition'] == condition]
                if not condition_comps:
                    condition_comps = comps
                
                prices = [comp['price'] for comp in condition_comps]
                
                if len(prices) >= 2:
                    median = statistics.median(prices)
                    optimal = median * 0.95  # Slightly competitive
                else:
                    optimal = statistics.mean(prices) * 0.92
                
                return round(optimal, 2)
            except:
                return 50.0
        
        # Generate description using Gemini
        def generate_description(product_name: str, pricing_data: Dict, condition: str = "used") -> str:
            try:
                if automator_improved.gemini_model:
                    prompt = f"""Create a compelling eBay listing description for: {product_name}

Product condition: {condition}

Requirements:
- 2-3 short paragraphs
- Highlight key features and benefits
- Mention condition honestly
- Include shipping/return info
- Sound natural and trustworthy

Write a description that would make someone want to buy this item:"""
                    
                    response = automator_improved.gemini_model.generate_content(prompt)
                    if response and response.text:
                        return response.text.strip()
            except:
                pass
            
            return f"{product_name} in {condition} condition. Well-maintained and ready for a new owner. Fast shipping and returns accepted. Buy with confidence!"
        
        condition = product_data.get('condition', 'used')
        optimal_price = calculate_optimal_price(pricing_data, condition)
        description = generate_description(product_data.get('name', 'Unknown Product'), pricing_data, condition)
        
        listing_data = {
            'title': product_data.get('name', 'Unknown Product')[:80],
            'price': optimal_price,
            'condition': condition,
            'description': description,
            'category': product_data.get('category', 'Electronics')
        }
        
        print(f"📋 Creating IMPROVED eBay listing for: {listing_data['title']} at ${optimal_price}")
        
        # Create eBay listing with improved method
        result = automator_improved.create_ebay_listing_improved(listing_data)
        
        return jsonify({
            'ok': result.get('success', False),
            'data': result,
            'listing_data': listing_data,
            'diagnostics': {
                'method': 'improved_ai_powered',
                'gemini_used': automator_improved.gemini_model is not None,
                'focus': 'required_fields_only'
            }
        })
    
    except Exception as e:
        print(f"❌ API error: {e}")
        return jsonify({
            'ok': False,
            'error_code': 'INTERNAL_ERROR',
            'message': 'eBay listing creation failed'
        }), 500

if __name__ == '__main__':
    print("🛒 eBay Listing Automation API v2.1 - IMPROVED + AI-GUIDED")
    print("=" * 65)
    print("✨ NEW FEATURES:")
    print("  - AI-powered field completion with Gemini")
    print("  - Enhanced required field detection")
    print("  - Focus ONLY on required fields (not 21 recommended)")
    print("  - Better HTML debugging capabilities")
    print("  - Improved dropdown handling with fallbacks")
    print("  🆕 - AI-guided post-listing flow (handles verification steps!)")
    print("  🆕 - Intelligent navigation through phone confirmations")
    print("  🆕 - LLM-powered decision making for complex flows")
    print()
    print("🌐 Server: http://localhost:3004")
    print("📝 Create Listing: POST /api/ebay/listing")
    print("❤️  Health: GET /health")
    print()
    print("🚀 Ready for testing!")
     
    try:
        app.run(debug=True, host='0.0.0.0', port=3004)
    finally:
        automator_improved.close()