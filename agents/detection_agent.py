"""
Object Detection Agent for Decluttered.ai
Handles YOLO-based object detection and classification
Extracted from OD.py YOLO processing logic
"""

from uagents import Agent, Context, Model
import glob
import os
import time
from typing import Dict, List, Tuple, Optional
from ultralytics import YOLO


# Message Models for inter-agent communication
class CapturedImage(Model):
    filename: str
    timestamp: int
    file_path: str
    capture_index: int
    session_id: str


class DetectionResult(Model):
    image_path: str
    timestamp: int
    session_id: str
    detected_objects: Dict[str, str]  # {coordinates_key: class_name}
    unique_classes: List[str]
    detection_count: int
    largest_instances: Dict[str, str]  # Filtered largest instances per class


class DetectionStatus(Model):
    model_loaded: bool
    images_processed: int
    current_session: str


# Detection Agent Configuration
CONFIDENCE_THRESHOLD = 0.25
YOLO_MODEL_PATH = "yolov9c.pt"

# Create the Detection Agent (Mailbox enabled)
detection_agent = Agent(
    name="detection_agent",
    seed="detection_agent_seed_decluttered_ai",
    port=8002,
    mailbox=True
)

# Global state management
class DetectionState:
    def __init__(self):
        self.yolo_model: Optional[YOLO] = None
        self.images_processed = 0
        self.current_session = ""
        self.global_seen_objects = set()  # Track objects across images for deduplication
        self.processed_files = set()  # Track processed files to avoid reprocessing

detection_state = DetectionState()


def calculate_bbox_area(coords_str: str) -> float:
    """Calculate the area of a bounding box from coordinate string."""
    try:
        # Parse coordinates string back to tuple
        coords_str = coords_str.strip("()")
        coords = tuple(map(int, coords_str.split(", ")))
        x_min, y_min, x_max, y_max = coords
        return (x_max - x_min) * (y_max - y_min)
    except Exception:
        return 0.0


def select_largest_instances(all_detections: Dict[str, str]) -> Dict[str, str]:
    """
    For each object class, select only the instance with the largest bounding box area.
    Returns a filtered dictionary with only the largest instances.
    """
    class_largest = {}  # class_name -> (coords_key, area)

    for coords_key, class_name in all_detections.items():
        area = calculate_bbox_area(coords_key)

        if class_name not in class_largest:
            class_largest[class_name] = (coords_key, area)
        else:
            current_coords_key, current_area = class_largest[class_name]
            if area > current_area:
                class_largest[class_name] = (coords_key, area)

    # Convert back to the original format
    filtered_detections = {}
    for class_name, (coords_key, area) in class_largest.items():
        filtered_detections[coords_key] = class_name

    return filtered_detections


@detection_agent.on_event("startup")
async def setup_yolo_model(ctx: Context):
    """Initialize YOLO model on agent startup."""
    ctx.logger.info("[DETECTION] Detection Agent starting up...")

    try:
        detection_state.yolo_model = YOLO(YOLO_MODEL_PATH)
        ctx.logger.info("[DETECTION] YOLOv9 model loaded successfully")
    except Exception as e:
        ctx.logger.error(f"[DETECTION FATAL] Could not load YOLOv9 model: {e}")
        detection_state.yolo_model = None


@detection_agent.on_message(model=CapturedImage)
async def process_captured_image(ctx: Context, sender: str, msg: CapturedImage):
    """Process captured image for object detection."""
    if detection_state.yolo_model is None:
        ctx.logger.error("[DETECTION] YOLO model not loaded, cannot process image")
        return

    if not os.path.exists(msg.file_path):
        ctx.logger.error(f"[DETECTION] Image file not found: {msg.file_path}")
        return

    # Check if already processed
    if msg.file_path in detection_state.processed_files:
        ctx.logger.info(f"[DETECTION] Image already processed: {msg.filename}")
        return

    # Mark as processed
    detection_state.processed_files.add(msg.file_path)

    # Update session tracking
    if detection_state.current_session != msg.session_id:
        detection_state.current_session = msg.session_id
        detection_state.global_seen_objects.clear()  # Reset for new session
        ctx.logger.info(f"[DETECTION] Starting new session: {msg.session_id}")

    ctx.logger.info(f"[DETECTION] Processing image: {msg.filename}")

    try:
        # YOLO Detection with confidence threshold
        results = detection_state.yolo_model.predict(
            source=msg.file_path,
            conf=CONFIDENCE_THRESHOLD,
            save=False,
            verbose=False
        )

        # Dictionary to store all detected objects and their coordinates
        # Key: Coordinates (as string for JSON serialization) | Value: Class Name
        all_detections = {}

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                class_name = detection_state.yolo_model.names[class_id]
                coords = tuple(int(c) for c in box.xyxy[0].tolist())
                confidence = float(box.conf[0].item())

                # Convert coordinates to string for JSON serialization
                coords_key = str(coords)
                all_detections[coords_key] = class_name

                # Debug output
                print(f"[DETECTION DEBUG] Found {class_name} (conf: {confidence:.2f}) at {coords}")
                print(f"  Coords key: {coords_key}")

        if not all_detections:
            ctx.logger.info(f"[DETECTION] No objects detected with confidence >= {CONFIDENCE_THRESHOLD}")
            return

        # Select largest instances for each object class within this image
        filtered_detections = select_largest_instances(all_detections)

        if len(filtered_detections) != len(all_detections):
            ctx.logger.info(
                f"[DETECTION] Filtered to largest instances: "
                f"{len(all_detections)} -> {len(filtered_detections)} objects"
            )

        # Prepare the list of unique object names
        unique_object_names = list(set(filtered_detections.values()))
        ctx.logger.info(
            f"[DETECTION] Detected unique objects ({len(unique_object_names)}): {unique_object_names}"
        )

        # Update processing stats
        detection_state.images_processed += 1

        # Create detection result message
        detection_result = DetectionResult(
            image_path=msg.file_path,
            timestamp=msg.timestamp,
            session_id=msg.session_id,
            detected_objects=all_detections,  # All detections
            unique_classes=unique_object_names,
            detection_count=len(filtered_detections),
            largest_instances=filtered_detections  # Filtered largest instances
        )

        ctx.logger.info(
            f"[DETECTION] Sending detection results to AI Evaluator: "
            f"{len(unique_object_names)} unique classes detected"
        )

        # Send to AI Evaluator Agent
        AI_EVALUATOR_ADDRESS = "agent1q0vgqkwxlz7lfve6tqyse6z7m3zccv4uv7kt484jlc77dutxngzy62ea92p"
        await ctx.send(AI_EVALUATOR_ADDRESS, detection_result)

    except Exception as e:
        ctx.logger.error(f"[DETECTION] Error processing image {msg.filename}: {e}")


@detection_agent.on_interval(period=30.0)
async def process_batch_images(ctx: Context):
    """
    Process any remaining images in the capture folder.
    This handles cases where images might be missed during real-time processing.
    """
    if detection_state.yolo_model is None:
        return

    # Get all captured images that haven't been processed
    capture_folder = "captures"
    if not os.path.exists(capture_folder):
        return

    image_paths = sorted(glob.glob(os.path.join(capture_folder, "*.jpg")))

    if not image_paths:
        return

    ctx.logger.info(f"[DETECTION] Checking for unprocessed images in {capture_folder}")

    # Process any images (this is a fallback mechanism)
    for image_path in image_paths:
        # Skip if already processed
        if image_path in detection_state.processed_files:
            continue

        filename = os.path.basename(image_path)

        # Handle different filename patterns
        try:
            if filename.startswith('frame_'):
                # Original format: frame_timestamp.jpg
                timestamp = int(filename.split('_')[1].split('.')[0])
            elif filename.startswith('test_'):
                # Web API format: test_session_timestamp_filename.jpg
                # Use current time as timestamp
                timestamp = int(time.time())
            else:
                # Default: use current time
                timestamp = int(time.time())
        except (ValueError, IndexError):
            # If parsing fails, use current time
            timestamp = int(time.time())

        # Create a mock CapturedImage message for batch processing
        mock_msg = CapturedImage(
            filename=filename,
            timestamp=timestamp,
            file_path=image_path,
            capture_index=0,
            session_id="batch_processing"
        )

        # Process the image
        await process_captured_image(ctx, "self", mock_msg)


@detection_agent.on_interval(period=10.0)
async def status_report(ctx: Context):
    """Send periodic status updates."""
    if detection_state.images_processed > 0:
        status = DetectionStatus(
            model_loaded=detection_state.yolo_model is not None,
            images_processed=detection_state.images_processed,
            current_session=detection_state.current_session
        )

        ctx.logger.info(
            f"[DETECTION STATUS] Model loaded: {status.model_loaded}, "
            f"Images processed: {status.images_processed}, "
            f"Session: {status.current_session}"
        )


@detection_agent.on_event("shutdown")
async def cleanup_detection(ctx: Context):
    """Cleanup detection resources on shutdown."""
    ctx.logger.info("[DETECTION] Detection Agent shutting down")
    # YOLO model cleanup is handled automatically


if __name__ == "__main__":
    print("[DETECTION] Starting Object Detection Agent...")
    print("[DETECTION] Waiting for CapturedImage messages from Camera Agent")
    detection_agent.run()