# Camera Agent Documentation

## Purpose
Handles camera capture, image acquisition, and live feed management for the Decluttered.ai system.

## Overview
The Camera Agent is responsible for:
- Camera initialization and management
- Timed image capture with configurable intervals
- Live feed display with OpenCV
- File cleanup and directory management
- Coordinating capture sessions

## Configuration

### Environment Variables
- `CAMERA_INDEX`: Camera device index (default: 0)
- `CAPTURE_COOLDOWN_SECONDS`: Time between captures (default: 1.0)
- `MAX_CAPTURES`: Maximum images per session (default: 6)
- `ANALYSIS_DURATION_SECONDS`: Session duration (default: 10)

### Directories
- `CAPTURE_FOLDER`: "captures" - Directory for captured images

## Message Types

### Outgoing Messages
- **CapturedImage**: Sent to Detection Agent
  ```python
  {
    "filename": str,
    "timestamp": int,
    "file_path": str,
    "capture_index": int,
    "session_id": str
  }
  ```

- **CameraStatus**: Periodic status updates
  ```python
  {
    "is_active": bool,
    "captures_remaining": int,
    "elapsed_time": float,
    "camera_connected": bool
  }
  ```

### Incoming Messages
- **StartCapture**: Begin capture session
  ```python
  {
    "duration_seconds": int,
    "max_captures": int,
    "cooldown_seconds": float
  }
  ```

- **StopCapture**: End capture session
  ```python
  {
    "reason": str
  }
  ```

## Functions Extracted from OD.py

### `cleanup_folders()` → `setup_camera()`
- **Original Location**: OD.py lines 42-68
- **New Location**: camera_agent.py `setup_camera()` event handler
- **Purpose**: Initialize directories and camera resources

### `capture_and_analyze()` main loop → `capture_cycle()`
- **Original Location**: OD.py lines 327-398
- **New Location**: camera_agent.py `capture_cycle()` interval handler
- **Purpose**: Handle timed captures and live feed display

## Agent Behaviors

### Startup Behavior
- Initializes camera connection
- Creates necessary directories
- Cleans up previous session files

### Capture Cycle (100ms interval)
- Reads frames from camera
- Checks capture timing and limits
- Saves images when conditions are met
- Displays live feed with status overlay
- Sends captured images to Detection Agent

### Status Reporting (2s interval)
- Reports capture progress
- Camera connection status
- Remaining capture capacity

## Error Handling
- Camera connection failures
- File system errors
- Invalid capture parameters
- Graceful shutdown on errors

## Usage Example

```python
# Start the Camera Agent
python agents/camera_agent.py

# Send StartCapture message to begin
start_msg = StartCapture(
    duration_seconds=15,
    max_captures=8,
    cooldown_seconds=1.5
)
```

## Port Configuration
- **Port**: 8001
- **Endpoint**: http://localhost:8001/submit

## Dependencies
- OpenCV (cv2)
- uagents framework
- Standard Python libraries (os, time, glob)

## Performance Notes
- Uses 100ms interval for responsive capture
- Optimized for real-time operation
- Minimal memory footprint
- Automatic resource cleanup