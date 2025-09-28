# Development Guidelines

## Code Structure

### Project Organization
```
Decluttered.ai/
├── agents/                          # Agent implementations
│   ├── camera_agent.py
│   ├── detection_agent.py
│   ├── ai_evaluator_agent.py
│   ├── image_processor_agent.py
│   └── report_coordinator_agent.py
├── docs/                            # Documentation
│   ├── agents/                      # Agent-specific docs
│   ├── system/                      # System architecture docs
│   └── development/                 # Development guides
├── tests/                           # Test suite
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   └── fixtures/                    # Test data
├── scripts/                         # Utility scripts
│   ├── start_system.sh
│   ├── stop_system.sh
│   └── health_check.sh
├── .env.example                     # Environment template
├── requirements.txt                 # Python dependencies
└── README.md                        # Project overview
```

### Agent Naming Conventions

#### File Naming
- Agent files: `{purpose}_agent.py` (e.g., `camera_agent.py`)
- Test files: `test_{agent_name}.py` (e.g., `test_camera_agent.py`)
- Documentation: `{agent_name}.md` (e.g., `camera_agent.md`)

#### Variable Naming
```python
# Agent instances
agent_name = Agent(name="agent_name", seed="agent_seed", port=PORT)

# State classes
class AgentState:
    def __init__(self):
        self.property_name = initial_value

# Message models
class RequestMessage(Model):
    field_name: type
    another_field: type

class ResponseMessage(Model):
    result_field: type
    status_field: type
```

#### Function Naming
```python
# Event handlers
@agent.on_event("startup")
async def setup_agent(ctx: Context):
    """Initialize agent resources"""

# Message handlers
@agent.on_message(model=MessageType)
async def handle_message_type(ctx: Context, sender: str, msg: MessageType):
    """Process incoming message"""

# Interval handlers
@agent.on_interval(period=INTERVAL_SECONDS)
async def periodic_task(ctx: Context):
    """Execute recurring task"""

# Utility functions
def process_data(input_data: DataType) -> OutputType:
    """Process data and return result"""
```

### Message Model Definitions

#### Standard Message Structure
```python
from uagents import Model
from typing import Dict, List, Optional, Any

class StandardMessage(Model):
    # Required fields
    timestamp: int
    session_id: str

    # Data fields
    data_field: str
    optional_field: Optional[str] = None

    # Collections
    items_list: List[str] = []
    metadata: Dict[str, Any] = {}
```

#### Message Validation
```python
def validate_message(msg: StandardMessage) -> bool:
    """Validate message format and content"""
    if not msg.session_id:
        return False
    if msg.timestamp <= 0:
        return False
    return True
```

### Error Handling Patterns

#### Standard Error Handling
```python
@agent.on_message(model=InputMessage)
async def process_message(ctx: Context, sender: str, msg: InputMessage):
    """Process message with comprehensive error handling"""
    try:
        # Validate input
        if not validate_message(msg):
            ctx.logger.error(f"Invalid message from {sender}: {msg}")
            return

        # Process message
        result = await process_data(msg)

        # Send response
        response = ResponseMessage(
            timestamp=int(time.time()),
            session_id=msg.session_id,
            result=result
        )
        await ctx.send(target_agent_address, response)

    except Exception as e:
        ctx.logger.error(f"Error processing message: {e}")
        # Optional: Send error response
        error_response = ErrorMessage(
            timestamp=int(time.time()),
            session_id=msg.session_id,
            error=str(e)
        )
        await ctx.send(sender, error_response)
```

#### Resource Management
```python
@agent.on_event("startup")
async def setup_resources(ctx: Context):
    """Initialize resources with cleanup on failure"""
    try:
        # Initialize resources
        resource = initialize_resource()
        agent_state.resource = resource
        ctx.logger.info("Resources initialized successfully")

    except Exception as e:
        ctx.logger.error(f"Failed to initialize resources: {e}")
        await cleanup_resources()
        raise

@agent.on_event("shutdown")
async def cleanup_resources(ctx: Context):
    """Clean up resources on shutdown"""
    try:
        if hasattr(agent_state, 'resource') and agent_state.resource:
            agent_state.resource.cleanup()
        ctx.logger.info("Resources cleaned up successfully")

    except Exception as e:
        ctx.logger.error(f"Error during cleanup: {e}")
```

## Testing Framework

### Unit Testing Structure

#### Test File Template
```python
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from agents.camera_agent import camera_agent, CapturedImage, CameraState

class TestCameraAgent:
    """Unit tests for Camera Agent"""

    @pytest.fixture
    def mock_context(self):
        """Mock uAgents context for testing"""
        context = Mock()
        context.logger = Mock()
        context.send = AsyncMock()
        return context

    @pytest.fixture
    def sample_message(self):
        """Sample message for testing"""
        return CapturedImage(
            filename="test_frame.jpg",
            timestamp=1640995200,
            file_path="/test/path/test_frame.jpg",
            capture_index=1,
            session_id="test_session"
        )

    def test_camera_state_initialization(self):
        """Test camera state initialization"""
        state = CameraState()
        assert state.is_capturing == False
        assert state.capture_count == 0
        assert state.session_id == ""

    @pytest.mark.asyncio
    async def test_message_processing(self, mock_context, sample_message):
        """Test message processing functionality"""
        # Setup
        with patch('cv2.VideoCapture') as mock_camera:
            mock_camera.return_value.isOpened.return_value = True

            # Execute
            await camera_agent.setup_camera(mock_context)

            # Verify
            assert mock_context.logger.info.called
            mock_camera.assert_called_once()
```

#### Integration Testing
```python
import pytest
import tempfile
import os
from agents.camera_agent import camera_agent
from agents.detection_agent import detection_agent

class TestAgentIntegration:
    """Integration tests for agent communication"""

    @pytest.fixture
    def temp_directory(self):
        """Create temporary directory for test files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.mark.asyncio
    async def test_camera_to_detection_flow(self, temp_directory):
        """Test message flow from camera to detection agent"""
        # Create test image
        test_image_path = os.path.join(temp_directory, "test_frame.jpg")
        # ... create test image ...

        # Setup agents
        # ... agent setup ...

        # Test message flow
        captured_msg = CapturedImage(
            filename="test_frame.jpg",
            timestamp=1640995200,
            file_path=test_image_path,
            capture_index=1,
            session_id="test_session"
        )

        # Send message and verify processing
        # ... test implementation ...
```

### Test Data and Fixtures

#### Test Image Generation
```python
import numpy as np
from PIL import Image
import cv2

def create_test_image(width=640, height=480, objects=None):
    """Create test image with optional objects"""
    # Create base image
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    img_array.fill(128)  # Gray background

    # Add objects if specified
    if objects:
        for obj in objects:
            x, y, w, h = obj['bbox']
            color = obj.get('color', (255, 255, 255))
            cv2.rectangle(img_array, (x, y), (x+w, y+h), color, -1)

    return Image.fromarray(img_array)

def save_test_image(image, path):
    """Save test image to specified path"""
    image.save(path, 'JPEG')
```

#### Mock Data
```python
SAMPLE_DETECTION_RESULT = {
    "image_path": "/test/image.jpg",
    "timestamp": 1640995200,
    "session_id": "test_session",
    "detected_objects": {"(100,150,300,400)": "laptop"},
    "unique_classes": ["laptop"],
    "detection_count": 1,
    "largest_instances": {"(100,150,300,400)": "laptop"}
}

SAMPLE_EVALUATION_RESULT = {
    "image_path": "/test/image.jpg",
    "timestamp": 1640995200,
    "session_id": "test_session",
    "original_objects": ["laptop", "cup"],
    "resellable_items": ["laptop"],
    "evaluation_confidence": "high",
    "gemini_raw_response": "['laptop']",
    "filtered_detections": {"(100,150,300,400)": "laptop"}
}
```

### Performance Testing

#### Benchmark Tests
```python
import time
import asyncio
from memory_profiler import profile

class TestPerformance:
    """Performance and benchmark tests"""

    @profile
    def test_memory_usage(self):
        """Profile memory usage during processing"""
        # ... memory profiling test ...

    def test_processing_speed(self):
        """Benchmark processing speed"""
        start_time = time.time()

        # ... processing operations ...

        end_time = time.time()
        processing_time = end_time - start_time

        # Assert reasonable performance
        assert processing_time < 5.0  # Should complete in under 5 seconds

    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """Test concurrent message processing"""
        tasks = []
        for i in range(10):
            task = asyncio.create_task(process_test_message(i))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        assert len(results) == 10
```

## Debugging and Monitoring

### Logging Standards

#### Log Message Format
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Usage examples
logger.info("[AGENT] Starting processing session: %s", session_id)
logger.warning("[AGENT] High memory usage detected: %d MB", memory_usage)
logger.error("[AGENT] Failed to process image: %s", error_message)
logger.debug("[AGENT] Detailed state: %s", state_dict)
```

#### Structured Logging
```python
import json

def log_structured(logger, level, event, **kwargs):
    """Log structured data for better analysis"""
    log_data = {
        "event": event,
        "timestamp": time.time(),
        **kwargs
    }
    logger.log(level, json.dumps(log_data))

# Usage
log_structured(logger, logging.INFO, "message_sent",
               agent="camera", target="detection", message_type="CapturedImage")
```

### Health Check Implementation

#### Agent Health Endpoints
```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
async def health_check():
    """Standard health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "agent": "camera_agent",
        "version": "1.0.0",
        "checks": {
            "camera_connected": check_camera_connection(),
            "memory_usage": get_memory_usage(),
            "disk_space": check_disk_space()
        }
    }

    overall_healthy = all(health_status["checks"].values())
    status_code = 200 if overall_healthy else 503

    return JSONResponse(content=health_status, status_code=status_code)
```

### Performance Monitoring Tools

#### Custom Metrics Collection
```python
import time
from collections import defaultdict

class MetricsCollector:
    """Collect and report agent metrics"""

    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
        self.gauges = defaultdict(float)

    def increment(self, metric_name: str, value: int = 1):
        """Increment a counter metric"""
        self.counters[metric_name] += value

    def time_operation(self, operation_name: str):
        """Context manager for timing operations"""
        return TimingContext(self, operation_name)

    def set_gauge(self, metric_name: str, value: float):
        """Set a gauge metric value"""
        self.gauges[metric_name] = value

    def get_metrics(self) -> dict:
        """Get all collected metrics"""
        return {
            "counters": dict(self.counters),
            "timers": {k: {"count": len(v), "avg": sum(v)/len(v) if v else 0}
                      for k, v in self.timers.items()},
            "gauges": dict(self.gauges)
        }

class TimingContext:
    """Context manager for timing operations"""

    def __init__(self, collector: MetricsCollector, operation_name: str):
        self.collector = collector
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.collector.timers[self.operation_name].append(duration)

# Usage
metrics = MetricsCollector()

@agent.on_message(model=CapturedImage)
async def process_image(ctx: Context, sender: str, msg: CapturedImage):
    metrics.increment("images_received")

    with metrics.time_operation("image_processing"):
        # ... process image ...
        pass

    metrics.set_gauge("queue_size", get_queue_size())
```

## Code Quality Standards

### Pre-commit Hooks

#### `.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile, black]
```

### Code Review Checklist

#### Pull Request Requirements
- [ ] All tests pass
- [ ] Code coverage > 80%
- [ ] Documentation updated
- [ ] Performance impact assessed
- [ ] Error handling implemented
- [ ] Logging added for debugging
- [ ] Security considerations reviewed
- [ ] Backward compatibility maintained

#### Code Quality Checks
- [ ] Type hints provided
- [ ] Docstrings for public functions
- [ ] No hardcoded values
- [ ] Proper exception handling
- [ ] Resource cleanup implemented
- [ ] Thread safety considered
- [ ] Memory leaks prevented

## Contributing Workflow

### Development Process
1. **Fork Repository**: Create personal fork
2. **Create Branch**: `git checkout -b feature/new-agent`
3. **Implement Changes**: Follow coding standards
4. **Add Tests**: Ensure test coverage
5. **Update Documentation**: Keep docs current
6. **Submit PR**: Include detailed description
7. **Code Review**: Address feedback
8. **Merge**: After approval and tests pass

### Commit Message Format
```
type(scope): brief description

Detailed explanation of changes made and why.

Fixes #issue_number
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
Scopes: `camera`, `detection`, `ai`, `processor`, `coordinator`, `system`