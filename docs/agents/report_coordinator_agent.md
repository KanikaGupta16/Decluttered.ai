# Report Coordinator Agent Documentation

## Purpose
Central coordination, reporting, and state management for the Decluttered.ai system.

## Overview
The Report Coordinator Agent is responsible for:
- Coordinating the entire multi-agent system
- Managing session lifecycles and state
- Generating comprehensive analysis reports
- Tracking global statistics and deduplication
- System health monitoring and status reporting

## Configuration

### Report Configuration
- `REPORT_FILENAME`: "analysis_report_resellables.txt" - Report file template
- Session-based report naming: `{session_id}_{REPORT_FILENAME}`

### System Coordination
- Manages 5-agent system coordination
- Tracks session timeouts and finalization
- Handles system-wide error recovery

## Message Types

### Incoming Messages
- **ProcessingResult**: From Image Processor Agent
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

- **StartSystem**: System initialization command
  ```python
  {
    "duration_seconds": int,
    "max_captures": int,
    "cooldown_seconds": float
  }
  ```

### Outgoing Messages
- **SystemStatus**: Periodic system status
  ```python
  {
    "active_agents": int,
    "processing_queue_size": int,
    "system_health": str,
    "total_sessions": int,
    "current_session": str
  }
  ```

- **ReportData**: Final session reports
  ```python
  {
    "session_id": str,
    "total_images_processed": int,
    "total_unique_objects": int,
    "total_cropped_files": int,
    "final_report_path": str,
    "session_summary": Dict[str, any]
  }
  ```

## Functions Extracted from OD.py

### `write_analysis_report()`
- **Original Location**: OD.py lines 71-86
- **New Location**: report_coordinator_agent.py `write_analysis_report()`
- **Purpose**: Generate final analysis reports with statistics

### Global Deduplication Logic
- **Original Location**: OD.py lines 302-324
- **New Location**: report_coordinator_agent.py session management
- **Purpose**: Track unique objects across entire system

### Report Generation Logic
- **Original Location**: Scattered throughout OD.py
- **New Location**: Centralized in coordinator agent
- **Purpose**: Consistent report formatting and content

## Agent Behaviors

### Startup Behavior
- Initializes system-wide state tracking
- Sets system start timestamp
- Prepares for session coordination

### System Coordination
- Manages session lifecycles
- Coordinates message flow between agents
- Handles system initialization and shutdown

### Report Generation
- **Interim Reports** (30s interval): Progress tracking
- **Final Reports**: Comprehensive session summaries
- **Status Reports** (15s interval): System health monitoring

### Session Management
- **Session Creation**: Unique ID generation and configuration
- **Session Tracking**: State management across all agents
- **Session Finalization**: Timeout handling and cleanup

## Session Data Structure

```python
session_data = {
    "start_time": float,
    "duration_seconds": int,
    "max_captures": int,
    "cooldown_seconds": float,
    "images_processed": int,
    "total_objects_found": int,
    "unique_objects": set,
    "cropped_files": List[str],
    "status": str  # "active" or "completed"
}
```

## Report Format

### Header Section
```
--- Declutter Detector Analysis Report ---

Session ID: session_1640995200
Generated: 2024-01-01 12:00:00
```

### Per-Image Entries
```
Capture: frame_1640995200.jpg
  - Resellable Objects: laptop, book, handbag
  - Cropped Files: 1640995200_1_laptop.jpg, 1640995200_2_book.jpg
  - Location (First Item): XYXY (100, 150, 300, 400)
  - Processing Summary: 3 items processed
----------------------------------------
```

### Summary Statistics
```
--- Session Summary ---
Total Images Processed: 5
Total Unique Object Types: 8
Session Duration: 12.3 seconds
```

## System Health Monitoring

### Health States
- **"idle"**: No active processing
- **"healthy"**: Normal operation
- **"degraded"**: Some agent issues
- **"error"**: System-wide problems

### Monitoring Metrics
- Agent connectivity status
- Processing queue sizes
- Session completion rates
- Error frequencies

## Session Lifecycle Management

### Session States
1. **Creation**: StartSystem message received
2. **Active**: Processing incoming results
3. **Timeout Check**: Monitor duration limits
4. **Finalization**: Generate final reports
5. **Cleanup**: Release resources

### Timeout Handling
- Configured duration + 30-second buffer
- Automatic session finalization
- Graceful degradation on timeouts

## Error Recovery

### Agent Failure Handling
- Continues operation with reduced functionality
- Logs missing agent communications
- Attempts automatic recovery

### Data Consistency
- Session state validation
- Message ordering guarantees
- Rollback capabilities for failed operations

## Usage Example

```python
# Start the Report Coordinator Agent
python agents/report_coordinator_agent.py

# Send StartSystem message to initialize
start_msg = StartSystem(
    duration_seconds=20,
    max_captures=10,
    cooldown_seconds=2.0
)
```

## Port Configuration
- **Port**: 8005
- **Endpoint**: http://localhost:8005/submit

## Dependencies
- uagents framework
- Standard Python libraries (os, time, typing)

## Performance Notes
- Efficient session state management
- Scalable report generation
- Memory-conscious data tracking
- Configurable timeout handling
- Comprehensive logging and monitoring

## Integration Points
- **Camera Agent**: Sends StartCapture commands
- **Detection Agent**: Receives processing statistics
- **AI Evaluator Agent**: Monitors evaluation metrics
- **Image Processor Agent**: Aggregates processing results
- **Frontend Systems**: Provides status and report APIs