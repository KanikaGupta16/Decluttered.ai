"""
AI Evaluator Agent for Decluttered.ai
Handles Gemini AI integration for resale value assessment
Extracted from gemini_ACCESS.py
"""

from uagents import Agent, Context, Model
import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict, List, Optional


# Message Models for inter-agent communication
class DetectionResult(Model):
    image_path: str
    timestamp: int
    session_id: str
    detected_objects: Dict[str, str]  # {coordinates_key: class_name}
    unique_classes: List[str]
    detection_count: int
    largest_instances: Dict[str, str]


class EvaluationResult(Model):
    image_path: str
    timestamp: int
    session_id: str
    original_objects: List[str]
    resellable_items: List[str]
    evaluation_confidence: str
    gemini_raw_response: str
    filtered_detections: Dict[str, str]  # Objects that passed evaluation


class EvaluationStatus(Model):
    model_available: bool
    images_evaluated: int
    current_session: str
    api_calls_made: int


# AI Evaluator Agent Configuration
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL_NAME = 'gemini-2.5-flash'

# Create the AI Evaluator Agent (Mailbox enabled)
ai_evaluator_agent = Agent(
    name="ai_evaluator_agent",
    seed="ai_evaluator_seed_decluttered_ai",
    port=8003,
    mailbox=True
)

# Global state management
class EvaluatorState:
    def __init__(self):
        self.gemini_model: Optional[genai.GenerativeModel] = None
        self.images_evaluated = 0
        self.current_session = ""
        self.api_calls_made = 0
        self.api_available = False

evaluator_state = EvaluatorState()


def setup_gemini_model() -> bool:
    """Initialize Gemini AI model."""
    try:
        if not GOOGLE_API_KEY:
            print("[AI_EVALUATOR ERROR] GOOGLE_API_KEY not found in environment variables")
            return False

        # Configure the API key
        genai.configure(api_key=GOOGLE_API_KEY)

        # Use a vision-capable model for both tasks
        evaluator_state.gemini_model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        evaluator_state.api_available = True
        print("[AI_EVALUATOR] Gemini client initialized successfully")
        return True

    except Exception as e:
        print(f"[AI_EVALUATOR FATAL] Gemini client initialization failed: {e}")
        evaluator_state.gemini_model = None
        evaluator_state.api_available = False
        return False


def process_image_and_objects_for_resale(image_path: str, yolo_object_list: List[str]) -> str:
    """
    Analyzes the image for resellable items, using the YOLO list as context.
    Returns a Python-style list of the original YOLO class names that correspond
    to resellable items.
    """
    if evaluator_state.gemini_model is None:
        return "[]"

    try:
        # Convert list to string representation for the prompt
        yolo_object_list_str = str(yolo_object_list)

        # Enhanced, Permissive Prompt
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

        # Generate content using the image and prompt
        evaluator_state.api_calls_made += 1
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        response = evaluator_state.gemini_model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_data}
        ])

        # Print Gemini's raw reply for debugging
        raw_response = response.text.strip()
        print(f"[AI_EVALUATOR] Gemini Raw Reply: {raw_response}")

        return raw_response

    except Exception as e:
        print(f"[AI_EVALUATOR ERROR] process_image_and_objects_for_resale failed: {e}")
        return "[]"


@ai_evaluator_agent.on_event("startup")
async def setup_ai_evaluator(ctx: Context):
    """Initialize Gemini AI model on agent startup."""
    ctx.logger.info("[AI_EVALUATOR] AI Evaluator Agent starting up...")

    success = setup_gemini_model()
    if success:
        ctx.logger.info("[AI_EVALUATOR] Gemini model initialized successfully")
    else:
        ctx.logger.error("[AI_EVALUATOR] Failed to initialize Gemini model")


@ai_evaluator_agent.on_message(model=DetectionResult)
async def evaluate_resellability(ctx: Context, sender: str, msg: DetectionResult):
    """Evaluate detected objects for resale value using Gemini AI."""
    if evaluator_state.gemini_model is None:
        ctx.logger.error("[AI_EVALUATOR] Gemini model not available, cannot evaluate")
        return

    if not os.path.exists(msg.image_path):
        ctx.logger.error(f"[AI_EVALUATOR] Image file not found: {msg.image_path}")
        return

    # Update session tracking
    if evaluator_state.current_session != msg.session_id:
        evaluator_state.current_session = msg.session_id
        ctx.logger.info(f"[AI_EVALUATOR] Starting evaluation for session: {msg.session_id}")

    ctx.logger.info(f"[AI_EVALUATOR] Evaluating objects in: {os.path.basename(msg.image_path)}")
    ctx.logger.info(f"[AI_EVALUATOR] Objects to evaluate: {msg.unique_classes}")

    try:
        # Call Gemini API for evaluation
        gemini_raw_result = process_image_and_objects_for_resale(
            msg.image_path,
            msg.unique_classes
        )

        # Parse the expected list output from Gemini
        try:
            # Use eval() to convert the string list into an actual Python list
            resellable_names = eval(gemini_raw_result)
            # Basic safety check
            if not isinstance(resellable_names, list):
                resellable_names = []
        except Exception as e:
            ctx.logger.warning(f"[AI_EVALUATOR] Failed to parse Gemini response: {e}")
            resellable_names = []

        # Normalize names to lowercase for robust matching
        resellable_names_normalized = [name.lower() for name in resellable_names]

        if not resellable_names_normalized:
            ctx.logger.info("[AI_EVALUATOR] No items identified as resellable")
        else:
            ctx.logger.info(f"[AI_EVALUATOR] Resellable items identified: {resellable_names}")

        # Filter the original detections to only include resellable items
        filtered_detections = {}
        for coords_key, class_name in msg.largest_instances.items():
            if class_name.lower() in resellable_names_normalized:
                filtered_detections[coords_key] = class_name

        # Update processing stats
        evaluator_state.images_evaluated += 1

        # Create evaluation result message
        evaluation_result = EvaluationResult(
            image_path=msg.image_path,
            timestamp=msg.timestamp,
            session_id=msg.session_id,
            original_objects=msg.unique_classes,
            resellable_items=resellable_names,
            evaluation_confidence="high",  # Could be enhanced with actual confidence scoring
            gemini_raw_response=gemini_raw_result,
            filtered_detections=filtered_detections
        )

        ctx.logger.info(
            f"[AI_EVALUATOR] Evaluation complete: "
            f"{len(resellable_names)}/{len(msg.unique_classes)} items deemed resellable"
        )

        # Send to Image Processor Agent
        IMAGE_PROCESSOR_ADDRESS = "agent1qwgxuc8z9nsafsl30creg2hhykclaw4pnwm7ge9e5l3qakrx4r6nu67p2au"
        await ctx.send(IMAGE_PROCESSOR_ADDRESS, evaluation_result)

    except Exception as e:
        ctx.logger.error(f"[AI_EVALUATOR] Error evaluating image {os.path.basename(msg.image_path)}: {e}")


@ai_evaluator_agent.on_interval(period=15.0)
async def status_report(ctx: Context):
    """Send periodic status updates."""
    if evaluator_state.images_evaluated > 0:
        status = EvaluationStatus(
            model_available=evaluator_state.api_available,
            images_evaluated=evaluator_state.images_evaluated,
            current_session=evaluator_state.current_session,
            api_calls_made=evaluator_state.api_calls_made
        )

        ctx.logger.info(
            f"[AI_EVALUATOR STATUS] Model available: {status.model_available}, "
            f"Images evaluated: {status.images_evaluated}, "
            f"API calls: {status.api_calls_made}, "
            f"Session: {status.current_session}"
        )


@ai_evaluator_agent.on_event("shutdown")
async def cleanup_evaluator(ctx: Context):
    """Cleanup evaluator resources on shutdown."""
    ctx.logger.info("[AI_EVALUATOR] AI Evaluator Agent shutting down")
    # Gemini API cleanup is handled automatically


# Additional function for text-only processing (compatibility with original code)
def process_text_with_gemini(text_prompt: str) -> str:
    """
    Text-only processing function for compatibility.
    Currently unused in the YOLO workflow but kept for potential future use.
    """
    if evaluator_state.gemini_model is None:
        return "[]"

    try:
        response = evaluator_state.gemini_model.generate_content(text_prompt)
        return response.text.strip()

    except Exception as e:
        print(f"[AI_EVALUATOR ERROR] process_text_with_gemini failed: {e}")
        return "[]"


if __name__ == "__main__":
    print("[AI_EVALUATOR] Starting AI Evaluator Agent...")
    print("[AI_EVALUATOR] Waiting for DetectionResult messages from Detection Agent")
    ai_evaluator_agent.run()