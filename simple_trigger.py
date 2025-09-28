#!/usr/bin/env python3
"""
Simple trigger that creates images in the captures folder
to test the complete agent pipeline
"""

import shutil
import os
import time

def trigger_pipeline_test():
    """Copy test images to captures folder to trigger the agent pipeline"""

    print("🧪 Decluttered.ai - Pipeline Test Trigger")
    print("=" * 42)
    print("")

    # Check if we have test images
    test_folder = "test_captures"
    capture_folder = "captures"

    if not os.path.exists(test_folder):
        print("❌ No test images found. Run test_camera_standalone.py first")
        return False

    test_images = [f for f in os.listdir(test_folder) if f.endswith('.jpg')]
    if not test_images:
        print("❌ No test images found. Run test_camera_standalone.py first")
        return False

    print(f"📸 Found {len(test_images)} test images")
    print("🔄 Copying to captures folder to trigger agent pipeline...")
    print("")

    # Create captures folder
    os.makedirs(capture_folder, exist_ok=True)

    # Copy images with simulated timestamps
    base_time = int(time.time())
    for i, test_img in enumerate(sorted(test_images)):
        # Create new filename with current timestamp pattern
        new_filename = f"frame_{base_time + i}.jpg"

        src_path = os.path.join(test_folder, test_img)
        dst_path = os.path.join(capture_folder, new_filename)

        shutil.copy2(src_path, dst_path)
        print(f"📷 Copied: {test_img} → {new_filename}")

        # Small delay to simulate real capture timing
        time.sleep(0.5)

    print("")
    print("✅ Images copied to captures folder!")
    print("")
    print("🚀 Agent pipeline should now process these images:")
    print("   1. 🔍 Detection Agent will find objects")
    print("   2. 🧠 AI Evaluator will assess resale value")
    print("   3. ✂️  Image Processor will crop objects")
    print("   4. 📊 Report Coordinator will generate report")
    print("")
    print("📋 Monitor progress:")
    print("   📝 Detection logs: tail -f logs/detection_agent.log")
    print("   📝 AI Evaluator logs: tail -f logs/ai_evaluator_agent.log")
    print("   📝 Image Processor logs: tail -f logs/image_processor_agent.log")
    print("   📝 Coordinator logs: tail -f logs/report_coordinator_agent.log")
    print("")
    print("📁 Check results in ~30 seconds:")
    print("   ✂️  Cropped objects: cropped_resellables/")
    print("   📄 Analysis report: *_analysis_report_resellables.txt")

    return True

if __name__ == "__main__":
    success = trigger_pipeline_test()

    if success:
        print("")
        print("⏰ Wait about 30 seconds for processing to complete...")
        print("🎉 Then check the results!")
    else:
        print("")
        print("💡 Run 'python3 test_camera_standalone.py' first to capture test images")