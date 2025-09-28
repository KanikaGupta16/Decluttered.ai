# declutter_detector_yolo.py

import cv2
import time
import os
import glob
from PIL import Image
from ultralytics import YOLO

# Import the function that interacts with the Gemini API (replace the mock with your actual file)
# NOTE: Ensure gemini_ACCESS.py has a function named process_text_with_gemini
#from gemini_ACCESS import process_image_with_gemini, process_text_with_gemini 
# OLD:
# from gemini_ACCESS import process_image_with_gemini, process_text_with_gemini

# NEW:
from gemini_ACCESS import process_image_and_objects_for_resale, process_text_with_gemini


# -------------------------- CONFIGURATION --------------------------
CAPTURE_FOLDER = "captures"
CROPPED_FOLDER = "cropped_resellables" # New folder for cropped images
ANALYSIS_DURATION_SECONDS = 10
CAMERA_INDEX = 0  
REPORT_FILENAME = "analysis_report_resellables.txt"
MAX_CAPTURES = 6 
CAPTURE_COOLDOWN_SECONDS = 1.0 

# Load the YOLOv9 Model once globally
# yolov9c is chosen for balance. Change to yolov9s for speed or yolov9e for accuracy.
try:
    YOLO_MODEL = YOLO("yolov9c.pt")
    print("[INFO] YOLOv9 model loaded successfully.")
except Exception as e:
    print(f"[FATAL] Could not load YOLOv9 model: {e}")
    YOLO_MODEL = None


# --- Helper Functions ---

def cleanup_folders():
    """Deletes all previous captures, cropped images, and analysis reports."""
    
    # List of folders and files to clean
    paths_to_clean = [CAPTURE_FOLDER, CROPPED_FOLDER, REPORT_FILENAME]
    
    for path in paths_to_clean:
        if os.path.exists(path):
            print(f"[INFO] Cleaning up: '{path}'...")
            try:
                if os.path.isdir(path):
                    # Delete all files inside the folder
                    for filename in os.listdir(path):
                        file_path = os.path.join(path, filename)
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    # Delete the folder itself
                    os.rmdir(path)
                elif os.path.isfile(path):
                    os.unlink(path)
            except Exception as e:
                print(f"[ERROR] Failed to clean up {path}. Reason: {e}")
                
    # Recreate necessary folders
    os.makedirs(CAPTURE_FOLDER, exist_ok=True)
    os.makedirs(CROPPED_FOLDER, exist_ok=True)
    print("[INFO] Cleanup and setup complete.")


def write_analysis_report(results):
    """
    Writes the final analysis results to the report file.
    """
    print(f"\n[INFO] Writing final analysis report to {REPORT_FILENAME}...")
    try:
        with open(REPORT_FILENAME, "w") as f:
            if not results:
                f.write("No resellable objects were detected across all captures.\n")
            else:
                f.write("--- Declutter Detector Analysis Report ---\n\n")
                for result in results:
                    f.write(result + "\n")
        print(f"[SUCCESS] Report saved successfully.")
    except IOError as e:
        print(f"[ERROR] Could not write report file: {e}")


def crop_and_save_image(original_img_path, coords, class_name, capture_ts, crop_index):
    """
    Crops the original image using XYXY coordinates and saves it.
    
    Args:
        original_img_path (str): Path to the original JPEG.
        coords (tuple): Bounding box (x_min, y_min, x_max, y_max).
        class_name (str): The object class (e.g., 'laptop').
        capture_ts (int): The timestamp of the original capture.
        crop_index (int): A unique index for this crop from the image.
    """
    try:
        img = Image.open(original_img_path)
        # Bounding box is defined as (left, top, right, bottom)
        cropped_img = img.crop(coords) 
        
        # Create a descriptive filename for the cropped image
        safe_class_name = class_name.replace(" ", "_")
        crop_filename = f"{capture_ts}_{crop_index}_{safe_class_name}.jpg"
        output_path = os.path.join(CROPPED_FOLDER, crop_filename)
        
        cropped_img.save(output_path)
        return output_path
        
    except Exception as e:
        print(f"  [ERROR] Failed to crop and save image for {class_name}: {e}")
        return None

# --- IMPORTANT: Ensure these imports are at the top of your declutter_detector.py ---
# from PIL import Image
# from ultralytics import YOLO
# from gemini_ACCESS import process_image_and_objects_for_resale, process_text_with_gemini
# --- And ensure YOLO_MODEL is defined globally ---

def analyze_for_resellable_objects(folder):
    """
    Processes all captured images using YOLO for bounding boxes, sends the original image
    and the list of detected objects to Gemini for filtering, and then crops the images 
    of confirmed resellable items.
    """
    if not YOLO_MODEL:
        return []

    print("\n[INFO] Starting YOLO detection and Gemini filtering pipeline...")
    final_report_entries = []
    
    # Get all captured images
    image_paths = sorted(glob.glob(os.path.join(folder, "*.jpg")))
    
    if not image_paths:
        print("[INFO] No captured images found for analysis.")
        return final_report_entries

    for i, filename in enumerate(image_paths):
        # Extract timestamp from filename for unique crop naming
        ts = os.path.basename(filename).split('_')[1].split('.')[0]
        print(f"\n--- [Analysis {i+1}/{len(image_paths)}] Processing {os.path.basename(filename)} ---")
        
        try:
            # 1. YOLOv9 Detection
            # Conf=0.25 is a common minimum confidence threshold
            results = YOLO_MODEL.predict(source=filename, conf=0.25, save=False, verbose=False)
            
            # Dictionary to store all detected objects and their coordinates
            # Key: Bounding Box Coordinates (tuple) | Value: Class Name (string)
            all_detections = {} 
            
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0].item())
                    class_name = YOLO_MODEL.names[class_id]
                    coords = tuple(int(c) for c in box.xyxy[0].tolist())
                    
                    # Store coordinates and class name
                    all_detections[coords] = class_name

            if not all_detections:
                print("  [YOLO] No objects detected with sufficient confidence.")
                continue
                
            # Prepare the list of UNIQUE object names for the Gemini prompt
            unique_object_names = list(set(all_detections.values()))
            object_list_str = str(unique_object_names)
            print(f"  [YOLO] Detected unique objects ({len(unique_object_names)}): {object_list_str}")

            # 2. Gemini Filtering using IMAGE and TEXT CONTEXT
            
            # Call the updated function that sends the image AND the YOLO list to Gemini
            gemini_raw_result = process_image_and_objects_for_resale(filename, object_list_str)
            
            # Simple parsing of the expected list output from Gemini (e.g., "['laptop', 'book']")
            try:
                # Use eval() to convert the string list into an actual Python list
                resellable_names = eval(gemini_raw_result) 
                # Basic safety check
                if not isinstance(resellable_names, list):
                    resellable_names = []
            except Exception:
                resellable_names = []
            
            # Normalize names to lowercase for robust matching
            resellable_names_normalized = [name.lower() for name in resellable_names]


            if not resellable_names_normalized:
                print("  [Gemini] No items identified as resellable.")
                continue

            print(f"  [Gemini] Resellable items (YOLO names): {resellable_names}")

            # 3. Cropping and Reporting
            resellable_crops = []
            crop_index = 0
            
            for coords, class_name in all_detections.items():
                # Check if the class name (normalized) is in Gemini's filtered list
                if class_name.lower() in resellable_names_normalized:
                    crop_index += 1
                    # Use the cropping function to save the isolated image
                    output_path = crop_and_save_image(filename, coords, class_name, ts, crop_index)
                    
                    if output_path:
                        resellable_crops.append(os.path.basename(output_path))
            
            # 4. Final Report Entry
            if resellable_crops:
                # Get the coordinates of the first detected resellable item for the report
                first_coords = next(coords for coords, name in all_detections.items() if name.lower() in resellable_names_normalized)
                
                report_entry = (
                    f"Capture: {os.path.basename(filename)}\n"
                    f"  - Resellable Objects: {', '.join(resellable_names)}\n"
                    f"  - Cropped Files: {', '.join(resellable_crops)}\n"
                    f"  - Location (First Item): XYXY {first_coords}\n"
                    f"{'-'*40}"
                )
                final_report_entries.append(report_entry)
            
        except Exception as e:
            print(f"  [ERROR] Analysis pipeline failed for {filename}: {e}")
            final_report_entries.append(f"Capture: {os.path.basename(filename)} - Analysis Failed: {e}")
            
    print("\n[INFO] Full pipeline analysis complete.")
    return final_report_entries
# --- Main Detection Logic ---

def capture_and_analyze():
    """
    Main function to capture frames and initiate the YOLO/Gemini analysis pipeline.
    """
    # 1. Setup
    cleanup_folders()
    
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    start_time = time.time()
    capture_count = 0 
    last_capture_time = 0 
    
    # CRITICAL: Check if the camera opened successfully 
    if not cap.isOpened():
        print(f"[FATAL] Error: Could not open camera at index {CAMERA_INDEX}.")
        write_analysis_report([]) 
        return

    print(f"[INFO] Starting image capture for {ANALYSIS_DURATION_SECONDS} seconds...")
    print("[INFO] NOTE: Captures are based on a timer/user input, not motion detection.")
    
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
            
        # Time-based Capture Logic
        if capture_count < MAX_CAPTURES and (time.time() - last_capture_time) > CAPTURE_COOLDOWN_SECONDS:
            ts = int(time.time())
            filename = os.path.join(CAPTURE_FOLDER, f"frame_{ts}.jpg")
            cv2.imwrite(filename, frame)
            
            # Update counters and time tracker
            capture_count += 1
            last_capture_time = time.time()
            
            print(f"[{round(elapsed_time, 2)}s] Captured {os.path.basename(filename)} - Total: {capture_count}/{MAX_CAPTURES}")

        # Show live feed and time remaining
        remaining_time = ANALYSIS_DURATION_SECONDS - elapsed_time
        display_frame = frame.copy()
        
        # Add text to the frame
        text = f"Time Left: {remaining_time:.1f}s | Captures: {capture_count}/{MAX_CAPTURES} | Press 'q' to Quit"
        cv2.putText(display_frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Declutter Detector (YOLO/Gemini)", display_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n[INFO] User quit detected.")
            break

    # 3. Cleanup Camera
    cap.release()
    cv2.destroyAllWindows()
    
    # 4. Process Saved Captures (Run the heavy work now)
    final_analysis_results = analyze_for_resellable_objects(CAPTURE_FOLDER)
    
    # 5. Save Final Report
    write_analysis_report(final_analysis_results)


if __name__ == "__main__":
    capture_and_analyze()