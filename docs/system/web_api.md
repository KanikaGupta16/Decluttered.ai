# Web API Documentation

## Overview
The Web API Agent provides a RESTful interface for the Decluttered.ai multi-agent system, enabling web applications to upload images/videos and receive processed results.

## Architecture

### Web API Agent (Port 8006)
- **Purpose**: Bridge between web frontend and backend agents
- **Technology**: FastAPI + uAgents framework
- **Features**: File uploads, session management, real-time status monitoring

### Integration Flow
```
Frontend Upload → Web API Agent → Agent Pipeline → Results → Frontend
```

## API Endpoints

### Health Check
```http
GET /
GET /health
```

**Response:**
```json
{
  "service": "Decluttered.ai Web API",
  "status": "healthy",
  "version": "1.0.0",
  "api_status": "healthy",
  "upload_folder": true,
  "supported_formats": [".jpg", ".jpeg", ".png", ".mp4", ".mov", ".avi", ".webm"]
}
```

### File Upload
```http
POST /upload
Content-Type: multipart/form-data
```

**Parameters:**
- `files`: One or more image/video files

**Response:**
```json
{
  "session_id": "web_session_1759035476123",
  "status": "uploaded",
  "files_count": 3,
  "message": "Files uploaded successfully, processing started"
}
```

**Supported Formats:**
- **Images**: .jpg, .jpeg, .png
- **Videos**: .mp4, .mov, .avi, .webm

**Limits:**
- Max file size: 50MB per file
- Max files per upload: Unlimited (reasonable limits apply)

### Session Status
```http
GET /session/{session_id}
```

**Response:**
```json
{
  "session_id": "web_session_1759035476123",
  "status": "processing",
  "uploaded_files_count": 3,
  "processed_files_count": 5,
  "detected_objects": ["laptop", "chair", "mouse"],
  "cropped_objects_count": 4,
  "has_analysis_report": true,
  "created_at": 1759035476.123,
  "completed_at": null,
  "error_message": ""
}
```

**Status Values:**
- `pending`: Files uploaded, waiting to start
- `processing`: Currently being processed by agents
- `completed`: Processing finished successfully
- `failed`: Processing encountered an error

### Session Results
```http
GET /session/{session_id}/results
```

**Response:**
```json
{
  "session_id": "web_session_1759035476123",
  "status": "completed",
  "analysis_report": "--- Declutter Detector Analysis Report ---\n...",
  "cropped_objects": [
    {
      "filename": "1759035476_1_laptop.jpg",
      "size": 45678,
      "download_url": "/download/cropped/1759035476_1_laptop.jpg"
    }
  ],
  "processing_duration": 32.5
}
```

### Download Cropped Object
```http
GET /download/cropped/{filename}
```

**Response:** Binary file download

### List Sessions
```http
GET /sessions
```

**Response:**
```json
{
  "total_sessions": 5,
  "sessions": [
    {
      "session_id": "web_session_1759035476123",
      "status": "completed",
      "files_count": 3,
      "cropped_objects_count": 4,
      "created_at": 1759035476.123,
      "completed_at": 1759035508.456
    }
  ]
}
```

### Delete Session
```http
DELETE /session/{session_id}
```

**Response:**
```json
{
  "message": "Session web_session_1759035476123 deleted successfully"
}
```

## File Processing Pipeline

### Image Processing
1. **Upload**: Images saved to `web_uploads/`
2. **Transfer**: Copied to `captures/` with session prefix
3. **Detection**: YOLO processes images for objects
4. **Evaluation**: Gemini AI assesses resale value
5. **Cropping**: Valuable objects extracted to `cropped_resellables/`
6. **Reporting**: Analysis report generated

### Video Processing
1. **Upload**: Video saved to `web_uploads/`
2. **Frame Extraction**: Up to 10 frames extracted at intervals
3. **Processing**: Frames processed like images through agent pipeline
4. **Results**: Combined results from all frames

## Session Management

### Session Lifecycle
```
Upload → Processing → Completed/Failed → Cleanup (optional)
```

### Session Data
- **Uploaded Files**: Original files from user
- **Processed Files**: Files sent to agent pipeline
- **Detected Objects**: Objects found by YOLO
- **Cropped Objects**: Valuable items extracted
- **Analysis Report**: Final assessment report

### Automatic Cleanup
- Sessions persist until manually deleted
- Uploaded files remain in `web_uploads/`
- Processed results remain in respective folders

## Error Handling

### Upload Errors
- **File too large**: HTTP 400 with size limit message
- **Unsupported format**: HTTP 400 with format error
- **No files**: HTTP 400 with missing files error

### Processing Errors
- **Camera unavailable**: Processing continues without live camera
- **YOLO model failed**: Error logged, session marked failed
- **Gemini API error**: Fallback to basic object detection
- **Disk space**: Error logged with space requirements

### Error Response Format
```json
{
  "detail": "Error message description",
  "status_code": 400
}
```

## Frontend Integration

### Basic Upload Example (JavaScript)
```javascript
const formData = new FormData();
formData.append('files', fileInput.files[0]);

const response = await fetch('http://localhost:8006/upload', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log('Session ID:', result.session_id);
```

### Status Monitoring
```javascript
async function pollStatus(sessionId) {
  while (true) {
    const response = await fetch(`http://localhost:8006/session/${sessionId}`);
    const status = await response.json();

    if (status.status === 'completed') {
      // Get results
      const results = await fetch(`http://localhost:8006/session/${sessionId}/results`);
      return await results.json();
    } else if (status.status === 'failed') {
      throw new Error(status.error_message);
    }

    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}
```

### React Hook Example
```javascript
import { useState, useCallback } from 'react';

export function useDeclutteredAPI() {
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);

  const uploadFiles = useCallback(async (files) => {
    setUploading(true);

    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();
      setUploading(false);
      setProcessing(true);

      return result.session_id;
    } catch (error) {
      setUploading(false);
      throw error;
    }
  }, []);

  return { uploadFiles, uploading, processing };
}
```

## Configuration

### Environment Variables
```bash
# Web API Configuration
WEB_API_PORT=8006              # API server port
MAX_FILE_SIZE=52428800         # 50MB in bytes
UPLOAD_FOLDER=web_uploads      # Upload directory
```

### CORS Settings
- Default: `localhost:3000`, `localhost:3001` (Next.js)
- Configurable for production domains
- Supports credentials and all HTTP methods

## Security Considerations

### File Validation
- Extension whitelist enforcement
- File size limits
- MIME type validation
- Malicious file detection

### API Security
- Rate limiting (production recommendation)
- Input sanitization
- Error message sanitization
- File path traversal prevention

### Data Privacy
- Local processing (no external file uploads)
- Temporary file storage
- Session-based access control
- Optional automatic cleanup

## Performance

### Optimization Features
- Async file operations
- Background processing
- Session-based state management
- Efficient video frame extraction

### Scalability
- Multiple concurrent sessions
- Configurable resource limits
- Agent pipeline parallelization
- Optional distributed deployment

## Testing

### Test with curl
```bash
# Upload test
curl -X POST "http://localhost:8006/upload" \
  -F "files=@test_image.jpg"

# Check status
curl "http://localhost:8006/session/SESSION_ID"

# Get results
curl "http://localhost:8006/session/SESSION_ID/results"
```

### Python Test Script
```bash
python3 test_web_api.py
```

This comprehensive Web API provides a complete bridge between your Next.js frontend and the multi-agent backend system, enabling seamless file uploads and real-time processing monitoring.