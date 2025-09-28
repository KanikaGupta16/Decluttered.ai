# AI Evaluator Agent Documentation

## Purpose
Handles Gemini AI integration for resale value assessment in the Decluttered.ai system.

## Overview
The AI Evaluator Agent is responsible for:
- Managing Gemini API connection and authentication
- Processing images with detected objects for resale assessment
- Applying intelligent filtering for valuable items
- Providing confidence scoring for evaluations

## Configuration

### API Configuration
- `GOOGLE_API_KEY`: Environment variable for Gemini API access
- `GEMINI_MODEL_NAME`: "gemini-2.5-flash" - Vision-capable model

### Authentication
- Loads API key from .env file using python-dotenv
- Validates API availability at startup
- Handles authentication errors gracefully

## Message Types

### Incoming Messages
- **DetectionResult**: From Detection Agent
  ```python
  {
    "image_path": str,
    "timestamp": int,
    "session_id": str,
    "detected_objects": Dict[str, str],
    "unique_classes": List[str],
    "detection_count": int,
    "largest_instances": Dict[str, str]
  }
  ```

### Outgoing Messages
- **EvaluationResult**: Sent to Image Processor Agent
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

- **EvaluationStatus**: Periodic status updates
  ```python
  {
    "model_available": bool,
    "images_evaluated": int,
    "current_session": str,
    "api_calls_made": int
  }
  ```

## Functions Extracted from gemini_ACCESS.py

### `process_image_and_objects_for_resale()`
- **Original Location**: gemini_ACCESS.py lines 27-60
- **New Location**: ai_evaluator_agent.py `process_image_and_objects_for_resale()`
- **Purpose**: Send image and object list to Gemini for evaluation

### Gemini Client Initialization
- **Original Location**: gemini_ACCESS.py lines 10-21
- **New Location**: ai_evaluator_agent.py `setup_gemini_model()`
- **Purpose**: Initialize and configure Gemini API client

### `process_text_with_gemini()`
- **Original Location**: gemini_ACCESS.py lines 66-81
- **New Location**: ai_evaluator_agent.py `process_text_with_gemini()`
- **Purpose**: Text-only processing (compatibility function)

## Agent Behaviors

### Startup Behavior
- Loads and validates Gemini API credentials
- Initializes vision-capable model
- Tests API connectivity

### Evaluation Processing
- Receives DetectionResult messages
- Constructs permissive evaluation prompts
- Sends image + object list to Gemini API
- Parses and validates responses
- Filters original detections based on AI assessment

### Status Reporting (15s interval)
- API availability status
- Processing statistics
- Current session tracking
- API call monitoring

## Evaluation Prompt Strategy

### Permissive Approach
The agent uses a carefully crafted prompt that:
- Emphasizes functional electronics (laptops, keyboards)
- Includes quality bags and branded items
- Considers condition and resale potential
- Provides clear output format requirements

### Example Prompt Structure
```
"You are an expert in decluttering and second-hand resale.
Here is a list of generic objects detected in the image: [object_list].
Examine the image visually and confirm which of these items are worth the effort of reselling.
**Be permissive and include all functional electronics...**
Return a Python list of the object names... ['laptop', 'handbag', 'book']."
```

## Response Processing

### Parsing Strategy
- Expects Python list format from Gemini
- Uses eval() for string-to-list conversion
- Includes safety checks for response validation
- Handles malformed responses gracefully

### Filtering Logic
- Normalizes object names to lowercase
- Matches against original YOLO detections
- Creates filtered detection dictionary
- Preserves coordinate information

## Error Handling
- API authentication failures
- Network connectivity issues
- Malformed API responses
- Image file access errors
- Session management errors

## Usage Example

```python
# Start the AI Evaluator Agent
python agents/ai_evaluator_agent.py

# Ensure .env file contains GOOGLE_API_KEY
# Agent automatically processes DetectionResult messages
# and sends EvaluationResult messages to Image Processor Agent
```

## Port Configuration
- **Port**: 8003
- **Endpoint**: http://localhost:8003/submit

## Dependencies
- google-generativeai (Gemini API)
- python-dotenv (environment variables)
- uagents framework
- Standard Python libraries (os, typing)

## Performance Notes
- API call tracking for monitoring
- Efficient response caching potential
- Session-based state management
- Graceful degradation on API failures
- Comprehensive logging for debugging

## Security Considerations
- API key stored in environment variables
- No sensitive data logged
- Secure image transmission to Gemini
- Error messages don't expose credentials