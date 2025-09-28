
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

try:
    # Use the genai.Client() for the latest API functionality
    genai.configure(api_key=API_KEY)
    client = genai.Client()
    
    # Use a vision-capable model for both tasks, as the core task is visual confirmation
    MODEL = 'gemini-2.5-flash' 
    print("[INFO] Gemini client initialized successfully.")
    
except Exception as e:
    # This catches the 'module has no attribute Client' if the SDK is still old
    print(f"[FATAL] Gemini client initialization failed. Ensure SDK is updated and API key is correct.")
    print(f"Error details: {e}")
    client = None

# ----------------------------------------------------------------------
# --- Function 1: IMAGE & TEXT PROCESSING (Primary Function for YOLO Workflow) ---
# ----------------------------------------------------------------------

def process_image_and_objects_for_resale(image_path, yolo_object_list_str):
    """
    Analyzes the image for resellable items, using the YOLO list as context.
    Returns a Python-style list of the original YOLO class names that correspond
    to resellable items.
    """
    if client is None:
        return "[]"
        
    try:
        # 1. Upload the image file
        uploaded_file = client.files.upload(file=image_path)
        
        # 2. Enhanced, Permissive Prompt:
        prompt = (
            "You are an expert in decluttering and second-hand resale. "
            f"Here is a list of generic objects detected in the image: {yolo_object_list_str}. "
            "Examine the image visually and confirm which of these items are worth the effort of reselling. "
            "**Be permissive and include all functional electronics (e.g., laptop, keyboard), quality bags, and any items "
            "that appear to be branded or in excellent condition.** "
            
            "that correspond to resellable items. Example format: ['laptop', 'handbag', 'book']. "
            "Do not add any extra text or explanation."
        )

        # 3. Generate content
        response = client.models.generate_content(
            model=MODEL, 
            contents=[uploaded_file, prompt]
        )
        
        # Print Gemini's raw reply for debugging (as requested)
        print(f"  [Gemini Raw Reply]: {response.text.strip()}")
        
        # 4. Clean up the file after use
        client.files.delete(name=uploaded_file.name)
        
        return response.text.strip()

    except Exception as e:
        print(f"[Error] process_image_and_objects_for_resale failed: {e}")
        return "[]" 

# ----------------------------------------------------------------------
# --- Function 2: TEXT PROCESSING (Needed by the main script's import, though unused) ---
# ----------------------------------------------------------------------

def process_text_with_gemini(text_prompt):
    """
    Kept for compatibility with the main script's imports, but now uses the client object.
    (This function is currently unused in the YOLO workflow.)
    """
    if client is None:
        return "[]"

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=text_prompt
        )
        # Return the raw text
        return response.text.strip()
        
    except Exception as e:
        print(f"[Error] process_text_with_gemini failed: {e}")
        return "[]"