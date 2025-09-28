"""
Image Processor Agent for Decluttered.ai
Handles image cropping, manipulation, and file management
Extracted from OD.py cropping and processing logic
"""

from uagents import Agent, Context, Model
import os
from PIL import Image
from typing import Dict, List, Optional, Any


# Message Models for inter-agent communication
class EvaluationResult(Model):
    image_path: str
    timestamp: int
    session_id: str
    original_objects: List[str]
    resellable_items: List[str]
    evaluation_confidence: str
    gemini_raw_response: str
    filtered_detections: Dict[str, str]  # Objects that passed evaluation


class ProcessingResult(Model):
    original_image_path: str
    timestamp: int
    session_id: str
    resellable_objects: List[str]
    cropped_files: List[str]
    processing_summary: Dict[str, Any]
    total_objects_processed: int


class ProcessingStatus(Model):
    images_processed: int
    total_crops_created: int
    current_session: str
    cropped_folder_size: int


# Image Processor Agent Configuration
CROPPED_FOLDER = "cropped_resellables"
CROP_BORDER_PERCENTAGE = 0.3  # 30% border around detected objects

# Create the Image Processor Agent (Mailbox enabled)
image_processor_agent = Agent(
    name="image_processor_agent",
    seed="image_processor_seed_decluttered_ai",
    port=8004,
    mailbox=True
)

# Global state management
class ProcessorState:
    def __init__(self):
        self.images_processed = 0
        self.total_crops_created = 0
        self.current_session = ""
        self.session_crop_count = 0

processor_state = ProcessorState()


def setup_cropped_folder():
    """Create cropped images folder if it doesn't exist."""
    if not os.path.exists(CROPPED_FOLDER):
        os.makedirs(CROPPED_FOLDER, exist_ok=True)
        print(f"[IMAGE_PROCESSOR] Created folder: {CROPPED_FOLDER}")


def parse_coordinates(coords_str: str) -> tuple:
    """Parse coordinate string back to tuple format."""
    try:
        # Remove parentheses and split by comma
        coords_str = coords_str.strip("()")
        coords = tuple(map(int, coords_str.split(", ")))
        return coords
    except Exception as e:
        print(f"[IMAGE_PROCESSOR ERROR] Failed to parse coordinates {coords_str}: {e}")
        return (0, 0, 0, 0)


def calculate_bbox_area(coords: tuple) -> float:
    """Calculate the area of a bounding box."""
    x_min, y_min, x_max, y_max = coords
    return (x_max - x_min) * (y_max - y_min)


def crop_and_save_image(original_img_path: str, coords: tuple, class_name: str,
                       capture_ts: int, crop_index: int) -> Optional[str]:
    """
    Crops the original image using XYXY coordinates with added border and saves it.

    Args:
        original_img_path (str): Path to the original JPEG.
        coords (tuple): Bounding box (x_min, y_min, x_max, y_max).
        class_name (str): The object class (e.g., 'laptop').
        capture_ts (int): The timestamp of the original capture.
        crop_index (int): A unique index for this crop from the image.

    Returns:
        str: Path to the cropped image file, or None if failed.
    """
    try:
        img = Image.open(original_img_path)
        img_width, img_height = img.size

        # Extract original coordinates
        x_min, y_min, x_max, y_max = coords

        # Calculate border size based on object dimensions
        object_width = x_max - x_min
        object_height = y_max - y_min
        border_x = int(object_width * CROP_BORDER_PERCENTAGE)
        border_y = int(object_height * CROP_BORDER_PERCENTAGE)

        # Expand coordinates with border, ensuring they stay within image bounds
        new_x_min = max(0, x_min - border_x)
        new_y_min = max(0, y_min - border_y)
        new_x_max = min(img_width, x_max + border_x)
        new_y_max = min(img_height, y_max + border_y)

        # Create new coordinates tuple
        expanded_coords = (new_x_min, new_y_min, new_x_max, new_y_max)

        # Crop with expanded coordinates
        cropped_img = img.crop(expanded_coords)

        # Create a descriptive filename for the cropped image
        safe_class_name = class_name.replace(" ", "_")
        crop_filename = f"{capture_ts}_{crop_index}_{safe_class_name}.jpg"
        output_path = os.path.join(CROPPED_FOLDER, crop_filename)

        # Save the cropped image
        cropped_img.save(output_path)

        # Print detailed debugging info
        print(f"[IMAGE_PROCESSOR DEBUG] Cropping {class_name}:")
        print(f"  Original image size: {img_width}x{img_height}")
        print(f"  Original coords: {coords}")
        print(f"  Expanded coords: {expanded_coords}")
        print(f"  Border: {border_x}x{border_y}")
        print(f"  Object size: {object_width}x{object_height}")
        print(f"  Cropped size: {cropped_img.size}")
        print(f"  Saved to: {output_path}")

        return output_path

    except Exception as e:
        print(f"[IMAGE_PROCESSOR ERROR] Failed to crop and save image for {class_name}: {e}")
        return None


@image_processor_agent.on_event("startup")
async def setup_image_processor(ctx: Context):
    """Initialize image processor and setup directories on agent startup."""
    ctx.logger.info("[IMAGE_PROCESSOR] Image Processor Agent starting up...")

    # Setup cropped images folder
    setup_cropped_folder()
    ctx.logger.info("[IMAGE_PROCESSOR] Image processor initialized successfully")


@image_processor_agent.on_message(model=EvaluationResult)
async def process_evaluated_objects(ctx: Context, sender: str, msg: EvaluationResult):
    """Process evaluated objects by cropping resellable items from the original image."""
    if not os.path.exists(msg.image_path):
        ctx.logger.error(f"[IMAGE_PROCESSOR] Image file not found: {msg.image_path}")
        return

    # Update session tracking
    if processor_state.current_session != msg.session_id:
        processor_state.current_session = msg.session_id
        processor_state.session_crop_count = 0
        ctx.logger.info(f"[IMAGE_PROCESSOR] Starting processing for session: {msg.session_id}")

    ctx.logger.info(f"[IMAGE_PROCESSOR] Processing image: {os.path.basename(msg.image_path)}")
    ctx.logger.info(f"[IMAGE_PROCESSOR] Resellable items to crop: {msg.resellable_items}")

    if not msg.filtered_detections:
        ctx.logger.info("[IMAGE_PROCESSOR] No resellable objects to process")
        return

    try:
        # Process each resellable object
        cropped_files = []
        crop_index = 0
        resellable_objects_processed = []
        processing_details = {}

        for coords_str, class_name in msg.filtered_detections.items():
            # Parse coordinates from string
            coords = parse_coordinates(coords_str)

            if coords == (0, 0, 0, 0):
                ctx.logger.warning(f"[IMAGE_PROCESSOR] Invalid coordinates for {class_name}")
                continue

            crop_index += 1
            processor_state.session_crop_count += 1

            # Crop and save the image
            output_path = crop_and_save_image(
                msg.image_path,
                coords,
                class_name,
                msg.timestamp,
                crop_index
            )

            if output_path:
                cropped_files.append(os.path.basename(output_path))
                resellable_objects_processed.append(class_name)

                # Store processing details
                processing_details[class_name] = {
                    "coordinates": coords,
                    "area": calculate_bbox_area(coords),
                    "cropped_file": os.path.basename(output_path),
                    "border_percentage": CROP_BORDER_PERCENTAGE
                }

                ctx.logger.info(
                    f"[IMAGE_PROCESSOR] Successfully cropped {class_name} "
                    f"(area: {calculate_bbox_area(coords)}) -> {os.path.basename(output_path)}"
                )
            else:
                ctx.logger.error(f"[IMAGE_PROCESSOR] Failed to crop {class_name}")

        # Update processing stats
        processor_state.images_processed += 1
        processor_state.total_crops_created += len(cropped_files)

        # Create processing result message
        processing_result = ProcessingResult(
            original_image_path=msg.image_path,
            timestamp=msg.timestamp,
            session_id=msg.session_id,
            resellable_objects=resellable_objects_processed,
            cropped_files=cropped_files,
            processing_summary=processing_details,
            total_objects_processed=len(resellable_objects_processed)
        )

        ctx.logger.info(
            f"[IMAGE_PROCESSOR] Processing complete: "
            f"{len(cropped_files)} crops created from {len(msg.filtered_detections)} resellable objects"
        )

        # Send to Report Coordinator Agent
        REPORT_COORDINATOR_ADDRESS = "agent1qvf8rwqhnuj85w9fl7kap6uszlk00gpjed0pq6vh289thwqys0zeq9w9g4y"
        await ctx.send(REPORT_COORDINATOR_ADDRESS, processing_result)

    except Exception as e:
        ctx.logger.error(f"[IMAGE_PROCESSOR] Error processing image {os.path.basename(msg.image_path)}: {e}")


@image_processor_agent.on_interval(period=20.0)
async def status_report(ctx: Context):
    """Send periodic status updates."""
    if processor_state.images_processed > 0:
        # Calculate cropped folder size
        folder_size = 0
        if os.path.exists(CROPPED_FOLDER):
            for filename in os.listdir(CROPPED_FOLDER):
                filepath = os.path.join(CROPPED_FOLDER, filename)
                if os.path.isfile(filepath):
                    folder_size += os.path.getsize(filepath)

        status = ProcessingStatus(
            images_processed=processor_state.images_processed,
            total_crops_created=processor_state.total_crops_created,
            current_session=processor_state.current_session,
            cropped_folder_size=folder_size
        )

        ctx.logger.info(
            f"[IMAGE_PROCESSOR STATUS] Images processed: {status.images_processed}, "
            f"Total crops: {status.total_crops_created}, "
            f"Folder size: {status.cropped_folder_size} bytes, "
            f"Session: {status.current_session}"
        )


@image_processor_agent.on_event("shutdown")
async def cleanup_processor(ctx: Context):
    """Cleanup processor resources on shutdown."""
    ctx.logger.info("[IMAGE_PROCESSOR] Image Processor Agent shutting down")
    ctx.logger.info(f"[IMAGE_PROCESSOR] Final stats - Images: {processor_state.images_processed}, Crops: {processor_state.total_crops_created}")


if __name__ == "__main__":
    print("[IMAGE_PROCESSOR] Starting Image Processor Agent...")
    print("[IMAGE_PROCESSOR] Waiting for EvaluationResult messages from AI Evaluator Agent")
    image_processor_agent.run()