#!/usr/bin/env python3
"""
Reset Pipeline Script
Clears processed files, results, and logs for fresh testing
"""

import os
import shutil
import glob

def reset_pipeline():
    """Reset the pipeline for fresh testing"""
    print("🔄 Resetting Decluttered.ai Pipeline...")

    # Folders to clear
    folders_to_clear = [
        "captures",
        "cropped_resellables",
        "web_uploads",
        "logs"
    ]

    # Clear folders but keep them
    for folder in folders_to_clear:
        if os.path.exists(folder):
            print(f"  🗑️  Clearing {folder}/")
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"    ⚠️  Could not delete {file_path}: {e}")
        else:
            print(f"  📁 Creating {folder}/")
            os.makedirs(folder, exist_ok=True)

    # Remove analysis reports
    report_files = glob.glob("*_analysis_report_resellables.txt")
    for report in report_files:
        try:
            os.remove(report)
            print(f"  🗑️  Removed {report}")
        except Exception as e:
            print(f"    ⚠️  Could not remove {report}: {e}")

    # Remove agent addresses file
    if os.path.exists("agent_addresses.json"):
        try:
            os.remove("agent_addresses.json")
            print("  🗑️  Removed agent_addresses.json")
        except Exception as e:
            print(f"    ⚠️  Could not remove agent_addresses.json: {e}")

    print("✅ Pipeline reset complete!")
    print("\nNext steps:")
    print("1. Start agents: python3 deploy_agents.py")
    print("2. Test pipeline: curl -X POST -F 'file=@your_image.jpg' http://localhost:8006/test-pipeline")

if __name__ == "__main__":
    reset_pipeline()