#!/usr/bin/env python3
"""
Facebook Message Monitor for Decluttered.ai
Polls FB messages every 30 seconds and forwards to AgentMail
"""

import os
import time
import json
import threading
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import your existing scraper
from scraper import MarketplaceScraper

try:
    from agentmail import AgentMail
    AGENTMAIL_AVAILABLE = True
    print("[OK] AgentMail library available")
except ImportError:
    AGENTMAIL_AVAILABLE = False
    print("[WARNING] AgentMail not installed - using console output")

class FacebookMessageMonitor:
    def __init__(self):
        self.scraper = MarketplaceScraper()
        self.last_checked = {}  # Track last message timestamps per conversation
        self.agentmail = None
        self.monitor_inbox = None
        
        if AGENTMAIL_AVAILABLE:
            self.setup_agentmail()
        
        self.running = False
        
    def setup_agentmail(self):
        """Setup AgentMail inbox for FB messages"""
        try:
            # Check if API key is available
            api_key = os.getenv('AGENTMAIL_API_KEY')
            if not api_key:
                print("[WARNING] AGENTMAIL_API_KEY not found in environment variables")
                return
                
            if api_key.startswith('am_42a33a4de15884a10d84785f54ffa4fe75eb04f6ec86555ae9cdb88e04d84f82'):
                print("[WARNING] Please replace the placeholder AGENTMAIL_API_KEY in .env with your actual API key")
                print("[BULB] Get your API key from: https://agentmail.com/dashboard")
                return
            
            print(f"🔑 Using AgentMail API key: {api_key[:8]}...")
            self.agentmail = AgentMail(api_key=api_key)
            self.monitor_inbox = self.agentmail.inboxes.create(
                username="fb-messages",
                domain="decluttered.ai"
            )
            print(f"[OK] AgentMail inbox created: {self.monitor_inbox.username}@decluttered.ai")
        except Exception as e:
            print(f"[WARNING] AgentMail setup failed: {e}")
            print("[BULB] Make sure your AGENTMAIL_API_KEY is correct in .env file")
            self.agentmail = None

    def start_monitoring(self):
        """Start the Facebook message monitoring loop"""
        print("[ROCKET] Starting Facebook Message Monitor...")
        
        # Ensure Facebook access using existing scraper logic
        if not self.scraper.ensure_facebook_access():
            print("[ERROR] Facebook access failed")
            return False
            
        self.running = True
        
        # Run monitoring loop
        while self.running:
            try:
                new_messages = self.check_facebook_inbox()
                
                if new_messages:
                    print(f"📨 Found {len(new_messages)} new messages")
                    for msg in new_messages:
                        self.process_message(msg)
                else:
                    print("🔍 No new messages found")
                    
                # Wait 30 seconds before next check
                for i in range(30):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"[ERROR] Monitor error: {e}")
                print("⏳ Waiting 60 seconds before retry...")
                time.sleep(60)
                
        print("🛑 Facebook Message Monitor stopped")
        return True

    def get_actual_message_for_buyer(self, buyer_name, item_preview):
        """Click into conversation to get the actual latest message"""
        try:
            print(f"💬 Getting actual message from {buyer_name}...")
            
            # Look for clickable conversation row with this buyer
            conversation_xpath = f"//span[contains(text(), '{buyer_name}') and contains(text(), 'Anker')]"
            
            try:
                conv_element = self.scraper.driver.find_element(By.XPATH, conversation_xpath)
                # Find the clickable parent row
                clickable_row = conv_element.find_element(By.XPATH, "./ancestor::div[@role='row']")
                clickable_row.click()
                time.sleep(3)
                
                # Now extract the actual latest message
                message_selectors = [
                    'div[dir="auto"]:last-child',  # Last message
                    '[data-testid="message"] div[dir="auto"]',
                    'div[dir="auto"]'
                ]
                
                for selector in message_selectors:
                    try:
                        message_elements = self.scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                        # Get messages that aren't UI text
                        for elem in reversed(message_elements):  # Start from most recent
                            text = elem.text.strip()
                            if (text and len(text) > 3 and 
                                text not in ['Marketplace', buyer_name, 'Message sent', 'You sent'] and
                                not text.startswith('Seen by') and
                                not text.endswith('...') and
                                text != item_preview[:50]):
                                
                                print(f"   [OK] Found real message: {text}")
                                return text
                    except:
                        continue
                
                return "Could not extract message content"
                
            except Exception as e:
                print(f"   [WARNING] Could not click into conversation: {e}")
                return f"New message from {buyer_name}"
                
        except Exception as e:
            print(f"   [ERROR] Message extraction failed: {e}")
            return f"Activity from {buyer_name}"

    def check_facebook_inbox(self):
        """Extract messages directly from inbox previews - no clicking needed!"""
        new_messages = []
        
        try:
            print("📬 Checking Facebook Marketplace inbox...")
            self.scraper.driver.get("https://www.facebook.com/marketplace/inbox/")
            time.sleep(4)
            
            WebDriverWait(self.scraper.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[role="main"]'))
            )
            
            print("🔍 Extracting conversation previews directly...")
            
            # Look for conversation containers
            conversation_containers = self.scraper.driver.find_elements(
                By.CSS_SELECTOR, 
                'div[class*="x9f619"][class*="x1n2onr6"][class*="x1ja2u2z"]'
            )
            
            seen_conversations = set()
            
            for container in conversation_containers:
                try:
                    # Extract buyer name and item (format: "Name · Item")
                    buyer_item_elements = container.find_elements(
                        By.XPATH, 
                        ".//span[contains(text(), '·') and contains(text(), 'Anker')]"
                    )
                    
                    if not buyer_item_elements:
                        continue
                    
                    buyer_item_text = buyer_item_elements[0].text.strip()
                    print(f"   📋 Found conversation preview: {buyer_item_text}")
                    
                    # Parse "Kanika · Anker Soundcore Liberty 4 NC Wireless Earbuds"
                    if '·' in buyer_item_text:
                        parts = buyer_item_text.split('·', 1)
                        buyer_name = parts[0].strip()
                        item_title = parts[1].strip()
                    else:
                        continue
                    
                    # Extract the actual latest message 
                    latest_message = "No message preview"
                    
                    # Look for message preview patterns like "Kanika: Shshshd"
                    message_elements = container.find_elements(
                        By.XPATH, 
                        f".//span[starts-with(text(), '{buyer_name}:')]"
                    )
                    
                    if message_elements:
                        message_text = message_elements[0].text.strip()
                        # Remove "Kanika: " prefix to get just "Shshshd"
                        if ':' in message_text:
                            latest_message = message_text.split(':', 1)[1].strip()
                        else:
                            latest_message = message_text
                        print(f"   💬 Extracted message: {latest_message}")
                    
                    # Check if unread
                    unread_indicators = container.find_elements(
                        By.XPATH, 
                        ".//div[contains(text(), 'Unread message')]"
                    )
                    is_unread = len(unread_indicators) > 0
                    
                    # Get timestamp
                    timestamp = "unknown"
                    time_elements = container.find_elements(
                        By.XPATH, 
                        ".//span[contains(text(), 'm') or contains(text(), 'h') or contains(text(), ':')]"
                    )
                    for time_elem in time_elements:
                        time_text = time_elem.text.strip()
                        if re.match(r'\d+[mh]|\d+:\d+', time_text):
                            timestamp = time_text
                            break
                    
                    # Create unique conversation ID
                    conv_key = f"{buyer_name}_{item_title[:30]}"
                    
                    if conv_key not in seen_conversations:
                        seen_conversations.add(conv_key)
                        
                        # Check if this is new activity
                        current_state = f"{buyer_item_text}|{latest_message}|{timestamp}"
                        
                        if self.is_new_conversation(conv_key, current_state):
                            message_data = {
                                'conversation_id': conv_key,
                                'buyer_name': buyer_name,
                                'item_title': item_title,
                                'latest_message': latest_message,
                                'platform': 'facebook_marketplace',
                                'timestamp': datetime.now().isoformat(),
                                'fb_timestamp': timestamp,
                                'is_unread': is_unread,
                                'url': self.scraper.driver.current_url,
                                'raw_preview': buyer_item_text
                            }
                            
                            new_messages.append(message_data)
                            print(f"📨 NEW: {buyer_name} -> '{latest_message}' ({timestamp})")
                            
                            # If unread, it's definitely new/important
                            if is_unread:
                                print(f"   🔴 UNREAD MESSAGE from {buyer_name}!")
                        else:
                            print(f"   [OK] Already seen: {buyer_name}")
                    
                except Exception as e:
                    print(f"   [WARNING] Error processing container: {e}")
                    continue
            
            return new_messages
            
        except Exception as e:
            print(f"[ERROR] Inbox extraction failed: {e}")
            return []

    def is_new_conversation(self, conv_id, preview_text):
        """Check if this conversation preview is new"""
        if conv_id in self.last_checked:
            if self.last_checked[conv_id] == preview_text:
                return False  # Same preview as last time
        
        # Update our record
        self.last_checked[conv_id] = preview_text
        return True

    def extract_conversation_data(self):
        """Extract message data from current Facebook conversation - with debugging"""
        try:
            wait = WebDriverWait(self.scraper.driver, 5)
            
            print(f"🔍 Current URL: {self.scraper.driver.current_url}")
            
            # Save page source for debugging
            if hasattr(self, '_debug_mode'):
                with open(f'fb_debug_{int(time.time())}.html', 'w', encoding='utf-8') as f:
                    f.write(self.scraper.driver.page_source)
            
            # Get buyer name - try multiple strategies
            buyer_name = "Unknown"
            
            print("[USER] Looking for buyer name...")
            
            # Strategy 1: Look for profile names in various locations
            buyer_selectors = [
                'h1[dir="auto"]',
                'span[dir="auto"]',  # Profile names are often in spans
                '[data-testid="conversation_header"] span',
                '.x1heor9g.x1qlqyl8.x1pd3egz.x16tdsg8',
                'div[role="complementary"] span',  # Profile sidebar
                'a[role="link"] span[dir="auto"]'  # Profile links
            ]
            
            for selector in buyer_selectors:
                try:
                    elements = self.scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        print(f"   Found text with '{selector}': '{text}'")
                        # Skip common UI text
                        if (text and len(text) > 2 and 
                            text not in ['Marketplace', 'Create new listing', 'Messages', 'Home', 'Profile'] and
                            not text.startswith('$') and 
                            'listing' not in text.lower()):
                            buyer_name = text
                            print(f"   [OK] Using buyer name: {buyer_name}")
                            break
                    if buyer_name != "Unknown":
                        break
                except Exception as e:
                    print(f"   [WARNING] Selector failed '{selector}': {e}")
                    continue
            
            # Get item title/reference - try finding the actual listing
            item_title = "Unknown Item"
            
            print("[PACKAGE] Looking for item title...")
            
            item_selectors = [
                'img[alt]:not([alt=""])',  # Images with alt text
                '[aria-label*="listing"]',
                'div[dir="auto"]',  # General text divs
                'span[dir="auto"]',  # Text spans
                'a[href*="/marketplace/item/"]'  # Direct marketplace links
            ]
            
            for selector in item_selectors:
                try:
                    elements = self.scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.get_attribute('alt') if elem.tag_name == 'img' else elem.text
                        text = text.strip() if text else ""
                        print(f"   Found text with '{selector}': '{text[:50]}...'")
                        
                        # Look for actual product names
                        if (text and len(text) > 10 and 
                            text not in ['Create new listing', 'Marketplace', 'Messages'] and
                            not text.startswith('Profile photo') and
                            ('$' in text or any(word in text.lower() for word in 
                            ['headphones', 'phone', 'laptop', 'car', 'bike', 'furniture', 
                            'clothes', 'book', 'game', 'electronics', 'sony', 'apple', 'samsung']))):
                            item_title = text
                            print(f"   [OK] Using item title: {item_title}")
                            break
                            
                    if item_title != "Unknown Item":
                        break
                except Exception as e:
                    print(f"   [WARNING] Selector failed '{selector}': {e}")
                    continue
            
            # Get latest message - focus on actual message bubbles
            latest_message = "No message found"
            
            print("💬 Looking for messages...")
            
            message_selectors = [
                '[data-testid="message"] div[dir="auto"]',  # Message containers
                '[role="row"] div[dir="auto"]',  # Message rows
                'div[dir="auto"]:not(:empty)',  # Any non-empty text div
                'span:not(:empty)',  # Non-empty spans
            ]
            
            all_messages = []
            for selector in message_selectors:
                try:
                    elements = self.scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if (text and len(text) > 3 and 
                            text not in ['Marketplace', 'Create new listing', 'Messages', buyer_name, item_title] and
                            not text.startswith('$') and
                            text not in all_messages):  # Avoid duplicates
                            all_messages.append(text)
                            print(f"   Found message with '{selector}': '{text[:50]}...'")
                except Exception as e:
                    print(f"   [WARNING] Message selector failed '{selector}': {e}")
                    continue
            
            if all_messages:
                # Get the last few messages (most recent)
                latest_message = all_messages[-1]  # Most recent
                print(f"   [OK] Using latest message: {latest_message[:100]}...")
            
            # Create conversation ID
            conversation_id = f"{buyer_name}_{hash(item_title) % 10000}"
            
            message_data = {
                'conversation_id': conversation_id,
                'buyer_name': buyer_name,
                'item_title': item_title,
                'latest_message': latest_message,
                'platform': 'facebook_marketplace',
                'timestamp': datetime.now().isoformat(),
                'url': self.scraper.driver.current_url,
                'all_messages_found': len(all_messages),
                'debug_info': f"Found {len(all_messages)} messages total"
            }
            
            print(f"📝 Final extraction: {buyer_name} -> {item_title[:30]}... -> {latest_message[:50]}...")
            return message_data
            
        except Exception as e:
            print(f"[ERROR] Data extraction failed: {e}")
            return None

    def is_new_message(self, message_data):
        """Check if this is a new message we haven't processed"""
        if not message_data:
            return False
            
        conv_id = message_data['conversation_id']
        current_message = message_data['latest_message']
        
        # Check if we've seen this exact message before
        if conv_id in self.last_checked:
            if self.last_checked[conv_id] == current_message:
                return False  # Same message as last time
        
        # Update our record
        self.last_checked[conv_id] = current_message
        return True

    def process_message(self, message_data):
        """Enhanced message processing with unread priority"""
        priority = "🔴 HIGH PRIORITY" if message_data.get('is_unread', False) else "📨 Normal"
        
        print(f"\n{priority} - PROCESSING MESSAGE:")
        print(f"   [USER] Buyer: {message_data['buyer_name']}")
        print(f"   [PACKAGE] Item: {message_data['item_title']}")
        print(f"   💬 Message: '{message_data['latest_message']}'")
        print(f"   [CLOCK] Time: {message_data.get('fb_timestamp', 'unknown')}")
        print(f"   📍 Status: {'UNREAD' if message_data.get('is_unread', False) else 'Read'}")
        
        if self.agentmail and self.monitor_inbox:
            self.forward_to_agentmail_enhanced(message_data)
        else:
            self.log_to_console_enhanced(message_data)
            
        # Save to file with priority
        self.save_to_file(message_data)

    def forward_to_agentmail_enhanced(self, message_data):
        """Enhanced AgentMail forwarding with priority and context"""
        try:
            priority_prefix = "🔴 URGENT" if message_data.get('is_unread', False) else "📨"
            subject = f"{priority_prefix} FB: {message_data['buyer_name']} - {message_data['item_title'][:40]}"
            
            email_body = f"""🚨 FACEBOOK MARKETPLACE MESSAGE {'(UNREAD!)' if message_data.get('is_unread', False) else ''}

[USER] BUYER: {message_data['buyer_name']}
[PACKAGE] ITEM: {message_data['item_title']}
💬 MESSAGE: "{message_data['latest_message']}"
[CLOCK] TIME: {message_data.get('fb_timestamp', 'unknown')} ago
📍 STATUS: {'🔴 UNREAD' if message_data.get('is_unread', False) else '[OK] Read'}

[TARGET] QUICK ACTIONS:
- Respond immediately if unread
- Check for price negotiation keywords
- Assess buyer interest level

[CHART] CONTEXT:
Platform: Facebook Marketplace
Detected: {message_data['timestamp']}
Conversation ID: {message_data['conversation_id']}

--- Raw Data ---
{json.dumps(message_data, indent=2)}
"""
            
            # Send with priority routing
            recipient = "urgent@decluttered.ai" if message_data.get('is_unread', False) else "negotiations@decluttered.ai"
            
            self.agentmail.inboxes.messages.send(
                inbox_id=self.monitor_inbox.inbox_id,
                to=[recipient],
                subject=subject,
                text=email_body
            )
            
            status = "[OK] URGENT forwarded" if message_data.get('is_unread', False) else "[OK] Forwarded"
            print(f"   {status} to AgentMail")
            
        except Exception as e:
            print(f"[ERROR] AgentMail forward failed: {e}")

    def log_to_console_enhanced(self, message_data):
        """Enhanced console logging with priority and context"""
        is_unread = message_data.get('is_unread', False)
        priority = "🔴 URGENT" if is_unread else "📨 NORMAL"
        
        print("\n" + "="*60)
        print(f"{priority} FACEBOOK MARKETPLACE MESSAGE")
        print("="*60)
        print(f"[USER] Buyer: {message_data['buyer_name']}")
        print(f"[PACKAGE] Item: {message_data['item_title']}")
        print(f"💬 Message: \"{message_data['latest_message']}\"")
        print(f"[CLOCK] FB Time: {message_data.get('fb_timestamp', 'unknown')}")
        print(f"🕐 Detected: {message_data['timestamp']}")
        print(f"📍 Status: {'🔴 UNREAD' if is_unread else '[OK] Read'}")
        print(f"🔗 URL: {message_data['url']}")
        if is_unread:
            print("[WARNING]  ACTION REQUIRED: Respond to unread message!")
        print("="*60)

    def process_message(self, message_data):
        """Process new message - forward to AgentMail or console"""
        print(f"\n📨 PROCESSING NEW MESSAGE:")
        print(f"   Buyer: {message_data['buyer_name']}")
        print(f"   Item: {message_data['item_title']}")
        print(f"   Message: {message_data['latest_message'][:100]}...")
        
        if self.agentmail and self.monitor_inbox:
            self.forward_to_agentmail(message_data)
        else:
            self.log_to_console(message_data)
            
        # Also save to file for debugging
        self.save_to_file(message_data)

    def forward_to_agentmail(self, message_data):
        """Forward message to AgentMail"""
        try:
            subject = f"FB: {message_data['item_title'][:50]}"
            
            email_body = f"""NEW FACEBOOK MARKETPLACE MESSAGE

Buyer: {message_data['buyer_name']}
Item: {message_data['item_title']}
Platform: Facebook Marketplace
Time: {message_data['timestamp']}

Message:
{message_data['latest_message']}

Conversation URL: {message_data['url']}

--- Raw Data ---
{json.dumps(message_data, indent=2)}
"""
            
            # Send to negotiator agent (or create one)
            self.agentmail.inboxes.messages.send(
                inbox_id=self.monitor_inbox.inbox_id,
                to=["negotiations@decluttered.ai"],  # Your negotiator agent
                subject=subject,
                text=email_body
            )
            
            print("[OK] Message forwarded to AgentMail")
            
        except Exception as e:
            print(f"[ERROR] AgentMail forward failed: {e}")

    def log_to_console(self, message_data):
        """Log message to console (fallback when no AgentMail)"""
        print("\n" + "="*60)
        print("📨 NEW FACEBOOK MARKETPLACE MESSAGE")
        print("="*60)
        print(f"Buyer: {message_data['buyer_name']}")
        print(f"Item: {message_data['item_title']}")
        print(f"Time: {message_data['timestamp']}")
        print(f"Message: {message_data['latest_message']}")
        print(f"URL: {message_data['url']}")
        print("="*60)

    def save_to_file(self, message_data):
        """Save message to file for debugging"""
        try:
            filename = f"fb_messages_{datetime.now().strftime('%Y%m%d')}.jsonl"
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(json.dumps(message_data) + '\n')
        except Exception as e:
            print(f"[WARNING] File save failed: {e}")

    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.running = False

def main():
    """Main function for testing"""
    monitor = FacebookMessageMonitor()
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitor...")
        monitor.stop_monitoring()
        print("[OK] Monitor stopped")

if __name__ == "__main__":
    main()