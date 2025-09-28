# declutter_detector.py
import cv2
import time
import os
import glob
# Import the function that interacts with the Gemini API (replace the mock with your actual file)
from gemini_ACCESS import process_image_with_gemini 



# Configuration
CAPTURE_FOLDER = "captures"
ANALYSIS_DURATION_SECONDS = 10
CAMERA_INDEX = 0  # Changed from 1 to 0, as 0 is usually the default camera. Change back to 1 if necessary.
MOTION_THRESHOLD = 5000 
REPORT_FILENAME = "analysis_report.txt" # Static report file name
MAX_CAPTURES = 6 # Maximum number of images to capture
CAPTURE_COOLDOWN_SECONDS = 1.0 # NEW: Minimum time between captures

# --- Helper Functions ---

def cleanup_old_reports():
    """Deletes all previous analysis report files in the current directory."""
    # 1. Look for the static report file and delete it
    if os.path.exists(REPORT_FILENAME):
        print(f"[INFO] Cleaning up previous analysis report: '{REPORT_FILENAME}'...")
        try:
            os.unlink(REPORT_FILENAME)
        except Exception as e:
            print(f"[ERROR] Failed to delete old report {REPORT_FILENAME}. Reason: {e}")
    
    # 2. Also clean up any legacy timestamped reports just in case
    legacy_reports = glob.glob("analysis_report_*.txt") 
    if legacy_reports:
         print(f"[INFO] Cleaning up {len(legacy_reports)} legacy timestamped report files...")
         for report_file in legacy_reports:
             try:
                 os.unlink(report_file)
             except Exception as e:
                 print(f"[ERROR] Failed to delete legacy report {report_file}. Reason: {e}")


def write_analysis_report(results):
    """
    Writes the collected analysis results to a single file named REPORT_FILENAME.
    """
    # 1. Clean up old reports first (ensures only one report exists)
    cleanup_old_reports()
    
    # 2. Use the static file name
    report_filename = REPORT_FILENAME
    
    print(f"\n[INFO] Writing final analysis report to {report_filename}...")
    
    try:
        with open(report_filename, "w") as f:
            if not results:
                f.write("No significant scene changes were detected.\n")
            else:
                # Write only the raw results (filename : [objects identified])
                for result in results:
                    f.write(result + "\n")
        print(f"[SUCCESS] Report saved successfully.")
    except IOError as e:
        print(f"[ERROR] Could not write report file: {e}")


def parse_gemini_list_string(s):
    """
    Attempts to parse a string representation of a Python list (e.g., "['item1', 'item2']")
    into a proper list of strings.
    """
    if s.startswith("[") and s.endswith("]"):
        s = s.strip("[]").replace("'", "").replace('"', '')
        # Simple split, stripping whitespace
        return [item.strip() for item in s.split(',') if item.strip()]
    return []


def process_saved_captures(folder):
    """
    Processes all images in the specified folder using the Gemini API and
    checks for object redundancy against previously processed images.
    """
    print("\n[INFO] Starting batch analysis of saved captures with Gemini...")
    analysis_results = []
    # Set to track all unique objects encountered across all images
    all_detected_objects = set() 
    
    # Get all jpg files in the capture folder and sort them by name (timestamp)
    image_paths = sorted(glob.glob(os.path.join(folder, "*.jpg")))
    
    if not image_paths:
        print("[INFO] No captured images found for analysis.")
        return analysis_results

    for i, filename in enumerate(image_paths):
        print(f"[Analysis {i+1}/{len(image_paths)}] Processing {os.path.basename(filename)}...")
        
        try:
            # Call Gemini for analysis (returns a string like "['laptop', 'coffee cup']")
            gemini_raw_result = process_image_with_gemini(filename)
            current_objects = parse_gemini_list_string(gemini_raw_result)
            
            new_objects = []
            redundant_objects = []
            
            # Check redundancy and populate the master set
            for obj in current_objects:
                # Normalize case for reliable checking
                normalized_obj = obj.lower()
                if normalized_obj in all_detected_objects:
                    redundant_objects.append(obj)
                else:
                    new_objects.append(obj)
                    all_detected_objects.add(normalized_obj) # Add new unique object to the master set

            # Format the output for the console (full detail)
            if new_objects or redundant_objects:
                new_str = f"NEW: {new_objects}" if new_objects else ""
                redundant_str = f"REDUNDANT: {redundant_objects}" if redundant_objects else ""
                
                # Concatenate for full console output
                console_output = new_str + (", " if new_str and redundant_str else "") + redundant_str
            else:
                console_output = "No identifiable objects."

            # Format the result for the FINAL REPORT FILE (only includes NEW objects)
            report_output = f"NEW: {new_objects}" if new_objects else "No NEW objects detected."
            formatted_result = f"{filename} : [{report_output}]"
            
            analysis_results.append(formatted_result)
            print(f"  [SUCCESS] Full Analysis: {console_output}")
            
        except Exception as e:
            print(f"  [ERROR] Gemini call failed for {filename}: {e}")
            formatted_result = f"{filename} : [Analysis failed due to API error: {e}]"
            analysis_results.append(formatted_result)
            
    print("[INFO] Batch analysis complete.")
    return analysis_results


# --- Main Detection Logic ---

def detect_changes():
    # 1. Setup
    
    # Cleanup routine to delete previous capture images
    if os.path.exists(CAPTURE_FOLDER):
        print(f"[INFO] Cleaning up previous captures in '{CAPTURE_FOLDER}'...")
        for filename in os.listdir(CAPTURE_FOLDER):
            file_path = os.path.join(CAPTURE_FOLDER, filename)
            try:
                # Check if it's a file before deleting
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"[ERROR] Failed to delete {file_path}. Reason: {e}")
        print("[INFO] Cleanup complete.")
    
    os.makedirs(CAPTURE_FOLDER, exist_ok=True)
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    start_time = time.time()
    capture_count = 0 
    last_capture_time = 0 # NEW: Initialize time tracker for cooldown
    
    # CRITICAL: Check if the camera opened successfully 
    if not cap.isOpened():
        print(f"[FATAL] Error: Could not open camera at index {CAMERA_INDEX}.")
        print("       Check if the device is connected or if another app is using it.")
        print("       Also check system permissions for the camera.")
        write_analysis_report([]) # Save an empty report if we can't start
        return

    print(f"[INFO] Starting image capture for {ANALYSIS_DURATION_SECONDS} seconds...")
    
    # Capture the first frame to initialize 'prev_gray'
    ret, prev = cap.read()
    if not ret:
        print("[FATAL] Error: Could not read the initial frame.")
        cap.release()
        write_analysis_report([])
        return
        
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

    # 2. Main Capture Loop
    while True:
        # Check time limit
        elapsed_time = time.time() - start_time
        if elapsed_time > ANALYSIS_DURATION_SECONDS:
            print(f"\n[INFO] {ANALYSIS_DURATION_SECONDS} seconds elapsed. Stopping capture.")
            break

        # Read the current frame
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read frame from camera. Stopping loop.")
            break

        # Motion Detection Logic (Only saves the image, no Gemini call)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(prev_gray, gray)
        non_zero = cv2.countNonZero(diff)

        # Scene change detected
        if non_zero > MOTION_THRESHOLD:  
            
            # Check cooldown period first
            if (time.time() - last_capture_time) < CAPTURE_COOLDOWN_SECONDS:
                # Motion detected, but still in cooldown
                print(f"[{round(elapsed_time, 2)}s] Motion detected, skipping (Cooldown).")
            
            # Check if we have hit the capture limit
            elif capture_count < MAX_CAPTURES:
                ts = int(time.time())
                filename = os.path.join(CAPTURE_FOLDER, f"frame_{ts}.jpg")
                cv2.imwrite(filename, frame)
                
                # Update counters and time tracker
                capture_count += 1
                last_capture_time = time.time()
                
                # Confirmation that the image was captured, but analysis is deferred
                print(f"[{round(elapsed_time, 2)}s] Scene change detected → saved {filename} (Analysis Deferred) - Total: {capture_count}/{MAX_CAPTURES}")
            else:
                print(f"[{round(elapsed_time, 2)}s] Scene change detected, but capture limit ({MAX_CAPTURES}) reached. Skipping capture.")


        prev_gray = gray

        # Show live feed and time remaining
        remaining_time = ANALYSIS_DURATION_SECONDS - elapsed_time
        display_frame = frame.copy()
        
        # Add text to the frame
        text = f"Time Left: {remaining_time:.1f}s | Captures: {capture_count}/{MAX_CAPTURES} | Press 'q' to Quit"
        cv2.putText(display_frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Live Object Detector", display_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n[INFO] User quit detected.")
            break

    # 3. Cleanup Camera
    cap.release()
    cv2.destroyAllWindows()
    
    # 4. Process Saved Captures (Run the heavy work now)
    final_analysis_results = process_saved_captures(CAPTURE_FOLDER)
    
    # 5. Save Final Report
    write_analysis_report(final_analysis_results)


if __name__ == "__main__":
    detect_changes()
