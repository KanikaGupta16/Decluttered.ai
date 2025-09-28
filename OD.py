#!/usr/bin/env python3
"""
DECLUTTERED.AI - Object Detection Entry Point
This file now calls the complete pipeline in object_detection_pipeline.py
"""

import sys
import os

def main():
    """Main entry point that routes to the new pipeline"""
    print("🔥 DECLUTTERED.AI - Object Detection System")
    print("📄 This system now uses the complete integrated pipeline")
    print("✨ Features: YOLO detection → Recognition → Pricing → Marketplace listing")
    print()

    # Add current directory to Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    try:
        from object_detection_pipeline import main as pipeline_main
        pipeline_main()
        
    except ImportError as e:
        print(f"❌ Could not import pipeline: {e}")
        print("💡 Make sure all required packages are installed:")
        print("   pip install ultralytics opencv-python pillow supabase requests python-dotenv")
        
    except Exception as e:
        print(f"❌ Error running pipeline: {e}")

# Keep original imports for backward compatibility
try:
    from gemini_ACCESS import process_image_and_objects_for_resale, process_text_with_gemini
    print("✅ Gemini integration available")
except ImportError:
    print("⚠️ Gemini integration not available")

if __name__ == "__main__":
    main()