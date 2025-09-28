#!/usr/bin/env python3
"""
Production-ready Facebook monitor test
"""
import os
import time
from facebook_monitor import FacebookMessageMonitor

try:
    from agentmail import AgentMail
    AGENTMAIL_AVAILABLE = True
except ImportError:
    AGENTMAIL_AVAILABLE = False
    print("[WARNING] AgentMail not installed - install with: pip install agentmail")

def test_production_monitor():
    print("[ROCKET] PRODUCTION Facebook Message Monitor Test")
    print("=" * 60)
    
    # Check AgentMail setup
    if AGENTMAIL_AVAILABLE:
        try:
            agentmail = AgentMail()
            test_inbox = agentmail.inboxes.create(username="test-fb", domain="decluttered.ai")
            print(f"[OK] AgentMail working: {test_inbox.username}@decluttered.ai")
        except Exception as e:
            print(f"[ERROR] AgentMail setup failed: {e}")
            print("[BULB] Set AGENTMAIL_API_KEY environment variable")
            print("[BULB] Get your API key from: https://agentmail.com/dashboard")
            return False
    else:
        print("[WARNING] AgentMail not available - install with: pip install agentmail")
    
    # Test monitor
    print("\n[WRENCH] Initializing Facebook Monitor...")
    monitor = FacebookMessageMonitor()
    
    if not monitor.scraper.ensure_facebook_access():
        print("[ERROR] Facebook access failed")
        print("[BULB] Make sure you're logged into Facebook")
        return False
    
    print("[OK] Facebook access confirmed")
    print("\n🔍 Running 3-minute live test...")
    
    # Test for 3 minutes
    start_time = time.time()
    message_count = 0
    check_count = 0
    
    while time.time() - start_time < 180:  # 3 minutes
        check_count += 1
        print(f"\n--- Check #{check_count} (time: {int(time.time() - start_time)}s) ---")
        
        messages = monitor.check_facebook_inbox()
        
        if messages:
            message_count += len(messages)
            print(f"\n🎉 FOUND {len(messages)} NEW MESSAGES:")
            for i, msg in enumerate(messages, 1):
                print(f"\n  📨 Message #{i}:")
                print(f"     [USER] Buyer: {msg['buyer_name']}")
                print(f"     [PACKAGE] Item: {msg['item_title'][:50]}...")
                print(f"     💬 Message: {msg['latest_message'][:100]}...")
                print(f"     🕐 Time: {msg['timestamp']}")
                
                # Forward to AgentMail if available
                if monitor.agentmail:
                    try:
                        monitor.forward_to_agentmail(msg)
                        print(f"     [OK] Forwarded to AgentMail")
                    except Exception as e:
                        print(f"     [WARNING] AgentMail forward failed: {e}")
        else:
            print("   🔍 No new messages found")
        
        print("⏳ Waiting 30 seconds...")
        time.sleep(30)
    
    print(f"\n🏁 TEST COMPLETE!")
    print(f"   ⏱️  Runtime: 3 minutes")
    print(f"   🔍 Total checks: {check_count}")
    print(f"   📨 Messages found: {message_count}")
    print(f"   [OK] Average: {message_count/check_count:.1f} messages per check")
    
    if message_count > 0:
        print("\n[TARGET] SUCCESS! Your monitor is working and finding real buyers!")
        print("[ROCKET] Ready for production deployment")
    else:
        print("\n[BULB] No messages found - this is normal if no new activity")
        print("   Try sending yourself a test message on Facebook Marketplace")
    
    return True

def test_quick_check():
    """Quick single check test"""
    print("[LIGHTNING] QUICK CHECK - Single Facebook Inbox Scan")
    print("=" * 50)
    
    monitor = FacebookMessageMonitor()
    
    if not monitor.scraper.ensure_facebook_access():
        print("[ERROR] Facebook access failed")
        return False
    
    messages = monitor.check_facebook_inbox()
    
    if messages:
        print(f"[OK] Found {len(messages)} conversations:")
        for msg in messages:
            print(f"  [USER] {msg['buyer_name']}")
            print(f"  [PACKAGE] {msg['item_title'][:60]}...")
            print(f"  💬 {msg['latest_message'][:80]}...")
            print()
    else:
        print("🔍 No active conversations found")
    
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        test_quick_check()
    else:
        test_production_monitor()