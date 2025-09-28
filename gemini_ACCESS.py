
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

try:
    # Configure the API key
    genai.configure(api_key=API_KEY)
    
    # Use a vision-capable model for both tasks, as the core task is visual confirmation
    MODEL = genai.GenerativeModel('gemini-2.5-flash')
    print("[INFO] Gemini client initialized successfully.")
    
except Exception as e:
    print(f"[FATAL] Gemini client initialization failed. Ensure API key is correct.")
    print(f"Error details: {e}")
    MODEL = None

# ----------------------------------------------------------------------
# --- Function 1: IMAGE & TEXT PROCESSING (Primary Function for YOLO Workflow) ---
# ----------------------------------------------------------------------

def process_image_and_objects_for_resale(image_path, yolo_object_list_str):
    """
    Analyzes the image for resellable items, using the YOLO list as context.
    Returns a Python-style list of the original YOLO class names that correspond
    to resellable items.
    """
    if MODEL is None:
        return "[]"
        
    try:
        # 2. Enhanced, Permissive Prompt:
        prompt = (
            "You are an expert in decluttering and second-hand resale. "
            f"Here is a list of generic objects detected in the image: {yolo_object_list_str}. "
            "Examine the image visually and confirm which of these items are worth the effort of reselling. "
            "**Be permissive and include all functional electronics (e.g., laptop, keyboard), quality bags, and any items "
            "that appear to be branded or in excellent condition.** "
            
            "Return a Python list of the object names from the provided list "
            "that correspond to resellable items. Example format: ['laptop', 'handbag', 'book']. "
            "Do not add any extra text or explanation."
        )

        # 3. Generate content using the image and prompt
        response = MODEL.generate_content([prompt, {"mime_type": "image/jpeg", "data": open(image_path, "rb").read()}])
        
        # Print Gemini's raw reply for debugging (as requested)
        print(f"  [Gemini Raw Reply]: {response.text.strip()}")
        
        return response.text.strip()

    except Exception as e:
        print(f"[Error] process_image_and_objects_for_resale failed: {e}")
        return "[]" 

# ----------------------------------------------------------------------
# --- Function 2: TEXT PROCESSING (Needed by the main script's import, though unused) ---
# ----------------------------------------------------------------------

def process_text_with_gemini(text_prompt):
    """
    Kept for compatibility with the main script's imports, but now uses the MODEL object.
    (This function is currently unused in the YOLO workflow.)
    """
    if MODEL is None:
        return "[]"

    try:
        response = MODEL.generate_content(text_prompt)
        # Return the raw text
        return response.text.strip()
        
    except Exception as e:
        print(f"[Error] process_text_with_gemini failed: {e}")
        return "[]"