#!/usr/bin/env python3
"""
Populate demo analytics data for hackathon presentation
"""

import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def setup_demo_data():
    """Add realistic demo data to showcase analytics capabilities"""
    
    # Connect to Supabase
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return
    
    supabase = create_client(url, key)
    print("✅ Connected to Supabase")
    
    # Sample analytics data
    demo_analytics = {
        "related_user": "demo_user_12345",
        "cache_type": "user_summary", 
        "cache_data": {
            "items": [
                {
                    "name": "Anker Soundcore Liberty 4 NC",
                    "platform": "facebook",
                    "listed_price": 79.99,
                    "inquiries": 12,
                    "avg_offer": 65.50,
                    "highest_offer": 75.00,
                    "views": 234,
                    "messages": 8,
                    "status": "active"
                },
                {
                    "name": "iPhone 13 Pro 256GB",
                    "platform": "ebay", 
                    "listed_price": 749.99,
                    "inquiries": 18,
                    "avg_offer": 680.25,
                    "highest_offer": 725.00,
                    "views": 456,
                    "messages": 12,
                    "status": "active"
                },
                {
                    "name": "MacBook Air M2 2022",
                    "platform": "facebook",
                    "listed_price": 999.99,
                    "inquiries": 6,
                    "avg_offer": 875.00,
                    "highest_offer": 950.00,
                    "views": 189,
                    "messages": 4,
                    "status": "sold"
                },
                {
                    "name": "Sony WH-1000XM4 Headphones",
                    "platform": "ebay",
                    "listed_price": 279.99,
                    "inquiries": 15,
                    "avg_offer": 245.50,
                    "highest_offer": 265.00,
                    "views": 312,
                    "messages": 9,
                    "status": "active"
                },
                {
                    "name": "Nintendo Switch OLED",
                    "platform": "facebook",
                    "listed_price": 329.99,
                    "inquiries": 22,
                    "avg_offer": 295.75,
                    "highest_offer": 320.00,
                    "views": 567,
                    "messages": 14,
                    "status": "pending_sale"
                }
            ],
            "total_inquiries": 73,
            "total_listings": 5,
            "conversion_rate": "68%",
            "avg_response_time": "2.4 hours",
            "total_revenue": 999.99,
            "pending_revenue": 1609.98
        },
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Sample communications data
    sample_communications = [
        {
            "agent_name": "negotiator",
            "inbox_address": "negotiations@decluttered.ai",
            "communication_type": "buyer_inquiry",
            "sender_email": "tech.buyer.sarah@gmail.com",
            "raw_message": "Hi! I'm interested in your iPhone 13 Pro. Is it unlocked? Would you consider $675 if I can pick up today?",
            "processed_intent": "price_negotiation",
            "response_generated": "Hi Sarah! Thanks for your interest. Yes, the iPhone 13 Pro is fully unlocked and in excellent condition. I appreciate your offer of $675. Given its pristine condition, would you be able to meet at $700? I can arrange pickup today!",
            "response_sent": True,
            "urgency_level": "high",
            "metadata": {
                "price_offer": 675.00,
                "buyer_qualification": "serious",
                "negotiation_strategy": "counter_offer"
            },
            "processed_at": (datetime.utcnow() - timedelta(hours=2)).isoformat()
        },
        {
            "agent_name": "negotiator", 
            "inbox_address": "negotiations@decluttered.ai",
            "communication_type": "buyer_inquiry",
            "sender_email": "music.lover.mike@outlook.com",
            "raw_message": "Are the Sony headphones still available? Do they come with the original case and cables?",
            "processed_intent": "availability_check",
            "response_generated": "Hi Mike! Yes, the Sony WH-1000XM4 headphones are still available and in excellent condition. They come with the original carrying case, USB-C cable, and 3.5mm audio cable. Would you like to arrange a time to check them out?",
            "response_sent": True,
            "urgency_level": "medium",
            "metadata": {
                "buyer_qualification": "casual",
                "negotiation_strategy": "provide_info"
            },
            "processed_at": (datetime.utcnow() - timedelta(hours=5)).isoformat()
        }
    ]
    
    # Sample voice interactions
    sample_voice_interactions = [
        {
            "auth0_sub": "demo_user_12345",
            "interaction_type": "voice_query",
            "user_input": "What are my best performing listings?",
            "recognized_intent": "analytics_query", 
            "agent_response": "Your top performer is the Nintendo Switch OLED with 22 inquiries and 567 views! The iPhone 13 Pro is also doing great with 18 inquiries and an average offer of $680.",
            "voice_enabled": True,
            "processing_time_ms": 750,
            "created_at": (datetime.utcnow() - timedelta(minutes=30)).isoformat()
        },
        {
            "auth0_sub": "demo_user_12345", 
            "interaction_type": "voice_query",
            "user_input": "How much revenue am I making?",
            "recognized_intent": "revenue_query",
            "agent_response": "You've made $999 from your sold MacBook Air, with $1,610 in potential revenue from pending sales. Your total portfolio value is $2,609!",
            "voice_enabled": True,
            "processing_time_ms": 650,
            "created_at": (datetime.utcnow() - timedelta(minutes=15)).isoformat()
        }
    ]
    
    # Market intelligence data
    market_intelligence = [
        {
            "intelligence_type": "pricing_trend",
            "data_points": "iPhone 13 Pro prices trending 8% higher due to iPhone 15 supply constraints",
            "confidence_score": 0.92,
            "source": "facebook_marketplace",
            "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat()
        },
        {
            "intelligence_type": "demand_spike",
            "data_points": "Nintendo Switch demand up 45% heading into holiday season",
            "confidence_score": 0.88,
            "source": "ebay_sold_listings", 
            "created_at": (datetime.utcnow() - timedelta(hours=6)).isoformat()
        },
        {
            "intelligence_type": "pricing_opportunity",
            "data_points": "Sony WH-1000XM4 underpriced by $30 compared to market average",
            "confidence_score": 0.85,
            "source": "cross_platform_analysis",
            "created_at": (datetime.utcnow() - timedelta(hours=3)).isoformat()
        }
    ]
    
    try:
        # Insert analytics cache
        print("📊 Adding analytics data...")
        result = supabase.table('analytics_cache').upsert(demo_analytics, on_conflict='related_user,cache_type').execute()
        print(f"✅ Analytics data added: {len(result.data)} records")
        
        # Insert communications
        print("📧 Adding communication records...")
        result = supabase.table('agent_communications').insert(sample_communications).execute()
        print(f"✅ Communications added: {len(result.data)} records")
        
        # Insert voice interactions
        print("🎤 Adding voice interactions...")
        result = supabase.table('voice_interactions').insert(sample_voice_interactions).execute()
        print(f"✅ Voice interactions added: {len(result.data)} records")
        
        # Insert market intelligence
        print("🧠 Adding market intelligence...")
        result = supabase.table('agent_market_intelligence').insert(market_intelligence).execute()
        print(f"✅ Market intelligence added: {len(result.data)} records")
        
        print("\n🎉 Demo data setup complete!")
        print("🚀 Your API now has rich analytics data to showcase!")
        
    except Exception as e:
        print(f"❌ Error setting up demo data: {e}")

if __name__ == "__main__":
    setup_demo_data()