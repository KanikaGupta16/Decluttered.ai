# Image Processor Agent Documentation

## Purpose
Handles image cropping, manipulation, and file management for the Decluttered.ai system.

## Overview
The Image Processor Agent is responsible for:
- Cropping resellable objects from original images
- Adding configurable borders around detected objects
- Managing cropped image files and directories
- Calculating object areas and processing statistics

## Configuration

### Processing Configuration
- `CROPPED_FOLDER`: "cropped_resellables" - Output directory
- `CROP_BORDER_PERCENTAGE`: 0.3 (30%) - Border size around objects

### File Management
- Automatic directory creation
- Descriptive filename generation
- Image format standardization (JPEG)

## Message Types

### Incoming Messages
- **EvaluationResult**: From AI Evaluator Agent
  ```python
  {
    "image_path": str,
    "timestamp": int,
    "session_id": str,
    "original_objects": List[str],
    "resellable_items": List[str],
    "evaluation_confidence": str,
    "gemini_raw_response": str,
    "filtered_detections": Dict[str, str]
  }
  ```

### Outgoing Messages
- **ProcessingResult**: Sent to Report Coordinator Agent
  ```python
  {
    "original_image_path": str,
    "timestamp": int,
    "session_id": str,
    "resellable_objects": List[str],
    "cropped_files": List[str],
    "processing_summary": Dict[str, any],
    "total_objects_processed": int
  }
  ```

- **ProcessingStatus**: Periodic status updates
  ```python
  {
    "images_processed": int,
    "total_crops_created": int,
    "current_session": str,
    "cropped_folder_size": int
  }
  ```

## Functions Extracted from OD.py

### `crop_and_save_image()`
- **Original Location**: OD.py lines 89-139
- **New Location**: image_processor_agent.py `crop_and_save_image()`
- **Purpose**: Crop objects with borders and save to files

### `calculate_bbox_area()`
- **Original Location**: OD.py lines 147-150
- **New Location**: image_processor_agent.py `calculate_bbox_area()`
- **Purpose**: Calculate bounding box areas for statistics

### Coordinate Parsing
- **New Function**: `parse_coordinates()`
- **Purpose**: Convert string coordinates back to tuple format

## Agent Behaviors

### Startup Behavior
- Creates cropped images directory
- Initializes processing state
- Validates directory permissions

### Image Processing
- Receives EvaluationResult messages
- Parses coordinate information
- Crops each resellable object with borders
- Saves individual item images
- Generates processing summaries

### Status Reporting (20s interval)
- Processing statistics
- Folder size monitoring
- Session tracking
- Error reporting

## Cropping Algorithm

### Border Calculation
```python
# Calculate border based on object dimensions
object_width = x_max - x_min
object_height = y_max - y_min
border_x = int(object_width * CROP_BORDER_PERCENTAGE)
border_y = int(object_height * CROP_BORDER_PERCENTAGE)
```

### Boundary Validation
- Ensures crops stay within image bounds
- Handles edge cases near image borders
- Maintains aspect ratios

### Filename Generation
Format: `{timestamp}_{crop_index}_{safe_class_name}.jpg`
- Timestamp for temporal ordering
- Index for uniqueness within image
- Sanitized class names (spaces → underscores)

## Processing Summary Structure

```python
processing_details[class_name] = {
    "coordinates": tuple,      # Original bounding box
    "area": float,            # Calculated area
    "cropped_file": str,      # Output filename
    "border_percentage": float # Applied border size
}
```

## Error Handling
- Invalid coordinate parsing
- Image file access errors
- Disk space limitations
- Permission issues
- Malformed evaluation results

## File Management

### Directory Structure
```
cropped_resellables/
├── 1640995200_1_laptop.jpg
├── 1640995200_2_book.jpg
├── 1640995210_1_handbag.jpg
└── ...
```

### File Naming Convention
- Timestamp ensures chronological ordering
- Index prevents filename collisions
- Class name provides immediate identification

## Usage Example

```python
# Start the Image Processor Agent
python agents/image_processor_agent.py

# Agent automatically processes EvaluationResult messages
# and sends ProcessingResult messages to Report Coordinator Agent
```

## Port Configuration
- **Port**: 8004
- **Endpoint**: http://localhost:8004/submit

## Dependencies
- PIL (Python Imaging Library)
- uagents framework
- Standard Python libraries (os, typing)

## Performance Notes
- Efficient coordinate parsing
- Memory-conscious image processing
- Batch processing capabilities
- Automatic garbage collection
- Session-based state management

## Quality Considerations
- Preserves image quality during cropping
- Maintains original aspect ratios
- Consistent border application
- Robust error recovery
- Comprehensive logging