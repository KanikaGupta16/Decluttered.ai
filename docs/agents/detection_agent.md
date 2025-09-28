# Object Detection Agent Documentation

## Purpose
Handles YOLO-based object detection and classification for the Decluttered.ai system.

## Overview
The Detection Agent is responsible for:
- Loading and managing YOLOv9 model
- Processing captured images for object detection
- Filtering detections by confidence threshold
- Selecting largest instances per object class
- Managing deduplication across images

## Configuration

### Model Configuration
- `YOLO_MODEL_PATH`: "yolov9c.pt" - YOLO model file
- `CONFIDENCE_THRESHOLD`: 0.25 - Minimum detection confidence

### Performance Settings
- Model loaded once at startup for efficiency
- Batch processing capability for missed images
- Automatic coordinate parsing and validation

## Message Types

### Incoming Messages
- **CapturedImage**: From Camera Agent
  ```python
  {
    "filename": str,
    "timestamp": int,
    "file_path": str,
    "capture_index": int,
    "session_id": str
  }
  ```

### Outgoing Messages
- **DetectionResult**: Sent to AI Evaluator Agent
  ```python
  {
    "image_path": str,
    "timestamp": int,
    "session_id": str,
    "detected_objects": Dict[str, str],  # {coordinates_key: class_name}
    "unique_classes": List[str],
    "detection_count": int,
    "largest_instances": Dict[str, str]
  }
  ```

- **DetectionStatus**: Periodic status updates
  ```python
  {
    "model_loaded": bool,
    "images_processed": int,
    "current_session": str
  }
  ```

## Functions Extracted from OD.py

### YOLO Processing Logic
- **Original Location**: OD.py lines 206-236
- **New Location**: detection_agent.py `process_captured_image()`
- **Purpose**: Run YOLO inference and extract bounding boxes

### `select_largest_instances()`
- **Original Location**: OD.py lines 152-174
- **New Location**: detection_agent.py `select_largest_instances()`
- **Purpose**: Filter to largest instance per object class

### `calculate_bbox_area()`
- **Original Location**: OD.py lines 147-150
- **New Location**: detection_agent.py `calculate_bbox_area()`
- **Purpose**: Calculate bounding box areas for comparison

## Agent Behaviors

### Startup Behavior
- Loads YOLOv9 model from file
- Validates model availability
- Initializes detection state

### Image Processing
- Receives CapturedImage messages
- Runs YOLO inference with confidence filtering
- Extracts bounding boxes and class names
- Applies largest-instance filtering
- Sends results to AI Evaluator Agent

### Batch Processing (30s interval)
- Fallback mechanism for missed images
- Processes any remaining files in capture folder
- Ensures no images are lost

### Status Reporting (10s interval)
- Model availability status
- Processing statistics
- Current session tracking

## Technical Details

### Coordinate Handling
- Coordinates stored as string keys for JSON serialization
- Format: "(x_min, y_min, x_max, y_max)"
- Automatic parsing and validation

### Deduplication Strategy
- Tracks objects per session
- Selects largest instance when multiple detections of same class
- Maintains detection history for reporting

### Error Recovery
- Handles model loading failures gracefully
- Validates image file existence
- Continues processing despite individual failures

## Usage Example

```python
# Start the Detection Agent
python agents/detection_agent.py

# Agent automatically processes CapturedImage messages
# from Camera Agent and sends DetectionResult messages
# to AI Evaluator Agent
```

## Port Configuration
- **Port**: 8002
- **Endpoint**: http://localhost:8002/submit

## Dependencies
- ultralytics (YOLO)
- uagents framework
- Standard Python libraries (os, glob, typing)

## Performance Notes
- Model loaded once at startup
- Efficient coordinate string handling
- Batch processing for reliability
- Memory-efficient detection storage
- Session-based state management