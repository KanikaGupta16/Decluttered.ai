#!/usr/bin/env python3
"""
Quick test script for Facebook monitor - with debugging
"""

from facebook_monitor import FacebookMessageMonitor

def test_monitor():
    print("🧪 Testing Facebook Message Monitor (DEBUG MODE)")
    
    monitor = FacebookMessageMonitor()
    monitor._debug_mode = True  # Enable HTML saving for debugging
    
    # Manually check one conversation instead of looping
    print("[ROCKET] Starting manual test...")
    
    if not monitor.scraper.ensure_facebook_access():
        print("[ERROR] Facebook access failed")
        return
    
    print("📬 Checking inbox once...")
    messages = monitor.check_facebook_inbox()
    
    print(f"\n[OK] Test complete. Found {len(messages)} messages")
    
    if messages:
        print("\n📋 Message details:")
        for i, msg in enumerate(messages):
            print(f"\nMessage {i+1}:")
            print(f"  Buyer: '{msg['buyer_name']}'")
            print(f"  Item: '{msg['item_title']}'")
            print(f"  Message: '{msg['latest_message'][:100]}...'")
            print(f"  Debug: {msg.get('debug_info', 'N/A')}")

if __name__ == "__main__":
    test_monitor()