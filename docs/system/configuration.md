# Configuration Management

## Environment Variables

### Required Environment Variables

#### AI Evaluator Agent
```bash
# Gemini API Configuration
GOOGLE_API_KEY=your_gemini_api_key_here
```

#### System-Wide Configuration
```bash
# Optional: Override default ports
CAMERA_AGENT_PORT=8001
DETECTION_AGENT_PORT=8002
AI_EVALUATOR_PORT=8003
IMAGE_PROCESSOR_PORT=8004
COORDINATOR_PORT=8005

# Optional: Override default directories
CAPTURE_FOLDER=captures
CROPPED_FOLDER=cropped_resellables
```

### Configuration File Setup

#### .env File Template
```bash
# Decluttered.ai Configuration
# Copy this to .env and fill in your values

# Gemini AI API
GOOGLE_API_KEY=your_google_api_key_here

# Camera Configuration
CAMERA_INDEX=0
ANALYSIS_DURATION_SECONDS=10
MAX_CAPTURES=6
CAPTURE_COOLDOWN_SECONDS=1.0

# YOLO Configuration
YOLO_MODEL_PATH=yolov9c.pt
CONFIDENCE_THRESHOLD=0.25

# Image Processing
CROP_BORDER_PERCENTAGE=0.3

# Directories
CAPTURE_FOLDER=captures
CROPPED_FOLDER=cropped_resellables
REPORT_FILENAME=analysis_report_resellables.txt

# Agent Network
CAMERA_AGENT_HOST=localhost
DETECTION_AGENT_HOST=localhost
AI_EVALUATOR_HOST=localhost
IMAGE_PROCESSOR_HOST=localhost
COORDINATOR_HOST=localhost
```

## Runtime Parameters

### Camera Agent Configuration

#### Capture Settings
```python
CAPTURE_FOLDER = "captures"                    # Image storage directory
ANALYSIS_DURATION_SECONDS = 10                # Session length
CAMERA_INDEX = 0                              # Camera device index
MAX_CAPTURES = 6                              # Maximum images per session
CAPTURE_COOLDOWN_SECONDS = 1.0                # Time between captures
```

#### Camera Quality Settings
```python
# Optional OpenCV camera properties
CAP_PROP_FRAME_WIDTH = 1920                   # Camera resolution width
CAP_PROP_FRAME_HEIGHT = 1080                  # Camera resolution height
CAP_PROP_FPS = 30                             # Frames per second
CAP_PROP_BRIGHTNESS = 0                       # Camera brightness (-1 to 1)
CAP_PROP_CONTRAST = 0                         # Camera contrast (-1 to 1)
```

### Detection Agent Configuration

#### YOLO Model Settings
```python
YOLO_MODEL_PATH = "yolov9c.pt"                # Model file path
CONFIDENCE_THRESHOLD = 0.25                   # Minimum detection confidence
```

#### Available YOLO Models
```python
# Performance vs Accuracy Trade-offs
YOLO_MODELS = {
    "yolov9s.pt": "Speed optimized",          # Fast, lower accuracy
    "yolov9c.pt": "Balanced",                 # Default, good balance
    "yolov9e.pt": "Accuracy optimized"        # Slow, higher accuracy
}
```

### AI Evaluator Configuration

#### Gemini Model Settings
```python
GEMINI_MODEL_NAME = 'gemini-2.5-flash'       # Vision-capable model
GEMINI_TEMPERATURE = 0.3                     # Response consistency (0.0-1.0)
GEMINI_MAX_TOKENS = 100                      # Response length limit
```

#### Evaluation Prompt Templates
```python
# Permissive evaluation prompt
EVALUATION_PROMPT_TEMPLATE = """
You are an expert in decluttering and second-hand resale.
Here is a list of generic objects detected in the image: {object_list}.
Examine the image visually and confirm which of these items are worth the effort of reselling.
**Be permissive and include all functional electronics (e.g., laptop, keyboard), quality bags, and any items
that appear to be branded or in excellent condition.**
Return a Python list of the object names from the provided list
that correspond to resellable items. Example format: ['laptop', 'handbag', 'book'].
Do not add any extra text or explanation.
"""

# Conservative evaluation prompt (alternative)
CONSERVATIVE_PROMPT_TEMPLATE = """
You are a conservative resale expert. Only identify items that are clearly valuable,
branded, or in excellent condition from this list: {object_list}.
Return a Python list format: ['item1', 'item2'].
"""
```

### Image Processor Configuration

#### Cropping Settings
```python
CROPPED_FOLDER = "cropped_resellables"        # Output directory
CROP_BORDER_PERCENTAGE = 0.3                 # 30% border around objects
```

#### File Management
```python
# Image output settings
OUTPUT_FORMAT = "JPEG"                       # Image format
OUTPUT_QUALITY = 95                          # JPEG quality (1-100)
MAX_CROP_SIZE = (1024, 1024)                # Maximum crop dimensions
MIN_CROP_SIZE = (32, 32)                    # Minimum crop dimensions
```

### Report Coordinator Configuration

#### Report Settings
```python
REPORT_FILENAME = "analysis_report_resellables.txt"
INTERIM_REPORT_INTERVAL = 30.0               # Seconds between interim reports
SESSION_TIMEOUT = 30                        # Extra seconds before session timeout
```

#### System Health Monitoring
```python
STATUS_REPORT_INTERVAL = 15.0               # System status update frequency
HEALTH_CHECK_TIMEOUT = 5.0                  # Agent response timeout
MAX_RETRY_ATTEMPTS = 3                      # Failed message retry count
```

## Agent Network Configuration

### Port Assignments
```python
AGENT_PORTS = {
    "camera_agent": 8001,
    "detection_agent": 8002,
    "ai_evaluator_agent": 8003,
    "image_processor_agent": 8004,
    "report_coordinator_agent": 8005
}
```

### Host Configuration
```python
# Single machine deployment
AGENT_HOSTS = {
    "camera_agent": "localhost:8001",
    "detection_agent": "localhost:8002",
    "ai_evaluator_agent": "localhost:8003",
    "image_processor_agent": "localhost:8004",
    "report_coordinator_agent": "localhost:8005"
}

# Distributed deployment example
DISTRIBUTED_HOSTS = {
    "camera_agent": "edge-device.local:8001",
    "detection_agent": "gpu-server.local:8002",
    "ai_evaluator_agent": "cloud-api.com:8003",
    "image_processor_agent": "storage-server.local:8004",
    "report_coordinator_agent": "main-server.local:8005"
}
```

## Performance Tuning

### Memory Management
```python
# Detection Agent memory settings
YOLO_DEVICE = "auto"                         # "cpu", "cuda", "auto"
BATCH_SIZE = 1                               # Images processed per batch
MAX_CACHE_SIZE = 100                         # Maximum cached results

# Image Processor memory settings
PIL_MAX_IMAGE_PIXELS = 89478485              # PIL safety limit
PROCESSING_WORKERS = 1                       # Parallel processing threads
```

### Processing Intervals
```python
# Agent update frequencies (seconds)
CAMERA_CAPTURE_INTERVAL = 0.1               # Camera frame checking
DETECTION_BATCH_INTERVAL = 30.0             # Batch processing fallback
AI_EVALUATOR_STATUS_INTERVAL = 15.0         # Status reporting
IMAGE_PROCESSOR_STATUS_INTERVAL = 20.0      # Processing statistics
COORDINATOR_STATUS_INTERVAL = 15.0          # System health monitoring
```

### Timeout Settings
```python
# Agent communication timeouts
MESSAGE_TIMEOUT = 30.0                      # Inter-agent message timeout
API_TIMEOUT = 60.0                          # External API call timeout
FILE_OPERATION_TIMEOUT = 10.0               # File I/O operations
STARTUP_TIMEOUT = 120.0                     # Agent initialization timeout
```

## Logging Configuration

### Log Levels
```python
# Per-agent log levels
LOG_LEVELS = {
    "camera_agent": "INFO",
    "detection_agent": "INFO",
    "ai_evaluator_agent": "DEBUG",           # More detailed for API debugging
    "image_processor_agent": "INFO",
    "report_coordinator_agent": "INFO"
}
```

### Log Output
```python
# Log file configuration
LOG_DIR = "logs"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_SIZE = 10 * 1024 * 1024             # 10MB per log file
LOG_BACKUP_COUNT = 5                        # Keep 5 backup files
```

## Configuration Validation

### Required Files Checklist
```bash
# Ensure these files exist before starting
✓ .env file with GOOGLE_API_KEY
✓ yolov9c.pt model file (downloaded automatically)
✓ captures/ directory (created automatically)
✓ cropped_resellables/ directory (created automatically)
✓ logs/ directory (created if logging enabled)
```

### Startup Validation
```python
# Configuration validation functions
def validate_api_keys():
    """Ensure all required API keys are present"""

def validate_model_files():
    """Check YOLO model availability"""

def validate_directories():
    """Ensure required directories exist or can be created"""

def validate_camera_access():
    """Test camera device availability"""

def validate_network_ports():
    """Check port availability for agents"""
```

## Dynamic Configuration Updates

### Runtime Configuration Changes
- Agent parameters can be updated via message passing
- Configuration changes apply to current session
- Persistent changes require .env file updates

### Hot-Reload Capabilities
- Most settings support runtime updates
- Model changes require agent restart
- Network configuration changes require system restart