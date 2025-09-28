# Deployment Guide

## Prerequisites

### System Requirements

#### Minimum Hardware
- **CPU**: 4+ cores, 2.0GHz+
- **RAM**: 8GB (16GB recommended)
- **Storage**: 10GB free space
- **Camera**: USB webcam or built-in camera
- **Network**: Internet connection for Gemini API

#### Recommended Hardware
- **CPU**: 8+ cores, 3.0GHz+ (Intel i7/AMD Ryzen 7)
- **RAM**: 16GB+
- **GPU**: NVIDIA GPU with 4GB+ VRAM (for YOLO acceleration)
- **Storage**: 50GB+ SSD
- **Camera**: HD webcam (1080p)

### Software Requirements

#### Python Environment
```bash
# Python 3.10-3.13 required
python --version  # Should be 3.10+

# Virtual environment recommended
python -m venv decluttered_env
source decluttered_env/bin/activate  # Linux/Mac
# OR
decluttered_env\Scripts\activate     # Windows
```

#### Required Dependencies
```bash
# Core dependencies
pip install uagents>=0.20.1
pip install ultralytics>=8.0.0
pip install google-generativeai>=0.3.0
pip install opencv-python>=4.8.0
pip install python-dotenv>=1.0.0
pip install Pillow>=10.0.0

# Optional GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### API Keys and Authentication

#### Google Gemini API Setup
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file:
```bash
GOOGLE_API_KEY=your_api_key_here
```

## Single Machine Deployment

### Quick Start Setup

#### 1. Project Setup
```bash
# Clone or download the project
cd /path/to/Decluttered.ai

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys
```

#### 2. Environment Configuration
```bash
# .env file contents
GOOGLE_API_KEY=your_google_api_key_here
CAMERA_INDEX=0
ANALYSIS_DURATION_SECONDS=10
MAX_CAPTURES=6
```

#### 3. Start All Agents
```bash
# Terminal 1: Camera Agent
python agents/camera_agent.py

# Terminal 2: Detection Agent
python agents/detection_agent.py

# Terminal 3: AI Evaluator Agent
python agents/ai_evaluator_agent.py

# Terminal 4: Image Processor Agent
python agents/image_processor_agent.py

# Terminal 5: Report Coordinator Agent
python agents/report_coordinator_agent.py
```

### Automated Startup Script

#### `start_system.sh`
```bash
#!/bin/bash
# Decluttered.ai System Startup Script

echo "Starting Decluttered.ai Multi-Agent System..."

# Check prerequisites
python --version || { echo "Python not found"; exit 1; }
[ -f .env ] || { echo ".env file not found"; exit 1; }

# Start agents in background
echo "Starting Camera Agent..."
python agents/camera_agent.py &
CAMERA_PID=$!

echo "Starting Detection Agent..."
python agents/detection_agent.py &
DETECTION_PID=$!

echo "Starting AI Evaluator Agent..."
python agents/ai_evaluator_agent.py &
AI_PID=$!

echo "Starting Image Processor Agent..."
python agents/image_processor_agent.py &
PROCESSOR_PID=$!

echo "Starting Report Coordinator Agent..."
python agents/report_coordinator_agent.py &
COORDINATOR_PID=$!

# Save PIDs for cleanup
echo $CAMERA_PID > .camera.pid
echo $DETECTION_PID > .detection.pid
echo $AI_PID > .ai.pid
echo $PROCESSOR_PID > .processor.pid
echo $COORDINATOR_PID > .coordinator.pid

echo "All agents started. Use stop_system.sh to shutdown."
echo "Send StartSystem message to Report Coordinator to begin processing."
```

#### `stop_system.sh`
```bash
#!/bin/bash
# Decluttered.ai System Shutdown Script

echo "Stopping Decluttered.ai Multi-Agent System..."

# Kill all agent processes
for pidfile in .*.pid; do
    if [ -f "$pidfile" ]; then
        PID=$(cat "$pidfile")
        echo "Stopping process $PID..."
        kill $PID 2>/dev/null
        rm "$pidfile"
    fi
done

echo "System stopped."
```

## Distributed Deployment

### Multi-Machine Setup

#### Architecture Overview
```
Edge Device (Camera)    GPU Server (Detection)    Cloud Server (AI + Coordination)
┌─────────────────┐    ┌─────────────────┐       ┌─────────────────┐
│  Camera Agent   │    │ Detection Agent │       │ AI Evaluator    │
│  Port: 8001     │    │ Port: 8002      │       │ Port: 8003      │
└─────────────────┘    └─────────────────┘       │                 │
                                                  │ Image Processor │
                                                  │ Port: 8004      │
                                                  │                 │
                                                  │ Report Coord.   │
                                                  │ Port: 8005      │
                                                  └─────────────────┘
```

#### Machine-Specific Configuration

##### Edge Device (Raspberry Pi/Jetson)
```bash
# .env file for edge device
GOOGLE_API_KEY=your_api_key_here
CAMERA_INDEX=0

# Network configuration
DETECTION_AGENT_HOST=gpu-server.local:8002
AI_EVALUATOR_HOST=cloud-server.com:8003
```

##### GPU Server
```bash
# .env file for GPU server
YOLO_MODEL_PATH=yolov9c.pt
CONFIDENCE_THRESHOLD=0.25

# Network configuration
CAMERA_AGENT_HOST=edge-device.local:8001
AI_EVALUATOR_HOST=cloud-server.com:8003
```

##### Cloud Server
```bash
# .env file for cloud server
GOOGLE_API_KEY=your_api_key_here

# Network configuration
DETECTION_AGENT_HOST=gpu-server.local:8002
```

### Network Configuration

#### Firewall Rules
```bash
# Allow agent ports
sudo ufw allow 8001  # Camera Agent
sudo ufw allow 8002  # Detection Agent
sudo ufw allow 8003  # AI Evaluator Agent
sudo ufw allow 8004  # Image Processor Agent
sudo ufw allow 8005  # Report Coordinator Agent
```

#### Agent Discovery Configuration
```python
# agents/config.py
AGENT_REGISTRY = {
    "camera_agent": "http://edge-device.local:8001",
    "detection_agent": "http://gpu-server.local:8002",
    "ai_evaluator_agent": "http://cloud-server.com:8003",
    "image_processor_agent": "http://cloud-server.com:8004",
    "report_coordinator_agent": "http://cloud-server.com:8005"
}
```

## Docker Containerization

### Dockerfile Templates

#### Base Dockerfile
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agents/ ./agents/
COPY docs/ ./docs/
COPY .env .

# Default command
CMD ["python", "agents/camera_agent.py"]
```

#### Camera Agent Dockerfile
```dockerfile
FROM decluttered-base

# Install camera dependencies
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Expose camera agent port
EXPOSE 8001

CMD ["python", "agents/camera_agent.py"]
```

#### Detection Agent Dockerfile
```dockerfile
FROM decluttered-base

# Download YOLO model
RUN python -c "from ultralytics import YOLO; YOLO('yolov9c.pt')"

# Expose detection agent port
EXPOSE 8002

CMD ["python", "agents/detection_agent.py"]
```

### Docker Compose Configuration

#### `docker-compose.yml`
```yaml
version: '3.8'

services:
  camera-agent:
    build:
      context: .
      dockerfile: dockerfiles/Dockerfile.camera
    ports:
      - "8001:8001"
    devices:
      - "/dev/video0:/dev/video0"  # Camera access
    environment:
      - CAMERA_INDEX=0
    volumes:
      - ./captures:/app/captures

  detection-agent:
    build:
      context: .
      dockerfile: dockerfiles/Dockerfile.detection
    ports:
      - "8002:8002"
    volumes:
      - ./captures:/app/captures
    depends_on:
      - camera-agent

  ai-evaluator-agent:
    build:
      context: .
      dockerfile: dockerfiles/Dockerfile.ai
    ports:
      - "8003:8003"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    depends_on:
      - detection-agent

  image-processor-agent:
    build:
      context: .
      dockerfile: dockerfiles/Dockerfile.processor
    ports:
      - "8004:8004"
    volumes:
      - ./captures:/app/captures
      - ./cropped_resellables:/app/cropped_resellables
    depends_on:
      - ai-evaluator-agent

  report-coordinator-agent:
    build:
      context: .
      dockerfile: dockerfiles/Dockerfile.coordinator
    ports:
      - "8005:8005"
    volumes:
      - ./reports:/app/reports
    depends_on:
      - image-processor-agent

networks:
  default:
    driver: bridge
```

#### Docker Deployment Commands
```bash
# Build all images
docker-compose build

# Start the system
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the system
docker-compose down

# Restart specific agent
docker-compose restart detection-agent
```

## Cloud Deployment Options

### AWS Deployment

#### EC2 Instance Setup
```bash
# Launch EC2 instance (t3.medium minimum)
# Install Docker and Docker Compose
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker

# Clone project and deploy
git clone https://github.com/yourusername/Decluttered.ai
cd Decluttered.ai
docker-compose up -d
```

#### ECS Deployment
```json
{
  "family": "decluttered-ai",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "camera-agent",
      "image": "your-repo/decluttered-camera:latest",
      "portMappings": [{"containerPort": 8001}],
      "environment": [
        {"name": "CAMERA_INDEX", "value": "0"}
      ]
    }
  ]
}
```

### Google Cloud Platform

#### Cloud Run Deployment
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: decluttered-ai
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containers:
      - image: gcr.io/your-project/decluttered-ai
        ports:
        - containerPort: 8001
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: google-api-key
```

## Monitoring and Maintenance

### Health Checks

#### Agent Health Monitoring
```bash
#!/bin/bash
# health_check.sh

AGENTS=("8001" "8002" "8003" "8004" "8005")
AGENT_NAMES=("Camera" "Detection" "AI-Evaluator" "Image-Processor" "Report-Coordinator")

for i in "${!AGENTS[@]}"; do
    PORT=${AGENTS[$i]}
    NAME=${AGENT_NAMES[$i]}

    if curl -s http://localhost:$PORT/health > /dev/null; then
        echo "✓ $NAME Agent (port $PORT) - Healthy"
    else
        echo "✗ $NAME Agent (port $PORT) - Unhealthy"
    fi
done
```

#### System Performance Monitoring
```bash
# Monitor system resources
top -p $(pgrep -f "agents/.*\.py" | tr '\n' ',' | sed 's/,$//')

# Monitor disk usage
du -sh captures/ cropped_resellables/ logs/

# Monitor network connections
netstat -tulpn | grep -E ":(800[1-5])"
```

### Log Management

#### Log Rotation
```bash
# /etc/logrotate.d/decluttered-ai
/path/to/Decluttered.ai/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        systemctl reload decluttered-ai || true
    endscript
}
```

### Backup and Recovery

#### Data Backup Script
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/decluttered-ai/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

# Backup configurations
cp .env "$BACKUP_DIR/"
cp -r agents/ "$BACKUP_DIR/"

# Backup data (optional - can be large)
tar -czf "$BACKUP_DIR/captures.tar.gz" captures/
tar -czf "$BACKUP_DIR/cropped.tar.gz" cropped_resellables/
tar -czf "$BACKUP_DIR/reports.tar.gz" *.txt

echo "Backup completed: $BACKUP_DIR"
```

## Troubleshooting

### Common Issues

#### Agent Startup Failures
```bash
# Check Python environment
python --version
pip list | grep uagents

# Check port availability
netstat -tulpn | grep 8001

# Check camera access
ls /dev/video*
```

#### Communication Issues
```bash
# Test agent connectivity
curl http://localhost:8001/health
curl http://localhost:8002/health

# Check firewall
sudo ufw status
```

#### Performance Issues
```bash
# Monitor CPU/RAM usage
htop

# Check disk space
df -h

# Monitor YOLO model loading
tail -f logs/detection_agent.log
```

### Log Analysis
```bash
# Check for errors across all agents
grep -r "ERROR" logs/

# Monitor message flow
grep -r "Sending\|Received" logs/

# Check API status
grep -r "API\|Gemini" logs/ai_evaluator.log
```