# Decluttered.ai - Multi-Agent Decluttering System

🤖 **AI-Powered Space Analysis using Fetch.ai Multi-Agent Architecture**

Decluttered.ai transforms your monolithic decluttering application into a modular, autonomous multi-agent system using Fetch.ai's uAgents framework. The system uses computer vision and AI to identify valuable items in cluttered spaces.

## 🌟 Features

- **Modular Architecture**: 5 specialized autonomous agents
- **Real-time Object Detection**: YOLOv9-based computer vision
- **AI-Powered Assessment**: Gemini AI for resale value evaluation
- **Automated Processing**: Image cropping and analysis pipeline
- **Comprehensive Reporting**: Detailed analysis reports
- **Distributed Deployment**: Scalable across multiple machines

## 🏗️ System Architecture

```
Camera Agent → Detection Agent → AI Evaluator → Image Processor → Report Coordinator
    8001          8002             8003            8004             8005
```

### Agent Responsibilities

| Agent | Port | Purpose |
|-------|------|---------|
| **Camera Agent** | 8001 | Camera capture and image acquisition |
| **Detection Agent** | 8002 | YOLO-based object detection |
| **AI Evaluator Agent** | 8003 | Gemini AI resale assessment |
| **Image Processor Agent** | 8004 | Image cropping and file management |
| **Report Coordinator Agent** | 8005 | System coordination and reporting |

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Camera (webcam or built-in)
- Google Gemini API key
- 8GB+ RAM (16GB recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Decluttered.ai
cd Decluttered.ai
```

2. **Install dependencies**
```bash
pip install uagents ultralytics google-generativeai opencv-python python-dotenv Pillow
```

3. **Set up environment**
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

4. **Test the system**
```bash
python test_agent_system.py
```

### Running the System

#### Option 1: Start All Agents Manually
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

#### Option 2: Use Startup Script (Coming Soon)
```bash
./scripts/start_system.sh
```

### Using the System

1. **Start all agents** using one of the methods above
2. **Send StartSystem message** to the Report Coordinator Agent (port 8005)
3. **Monitor the live camera feed** and capture process
4. **Review generated reports** in the project directory

## 📁 Project Structure

```
Decluttered.ai/
├── agents/                     # Agent implementations
│   ├── camera_agent.py         # Camera capture and management
│   ├── detection_agent.py      # YOLO object detection
│   ├── ai_evaluator_agent.py   # Gemini AI evaluation
│   ├── image_processor_agent.py # Image cropping and processing
│   └── report_coordinator_agent.py # System coordination
├── docs/                       # Comprehensive documentation
│   ├── agents/                 # Agent-specific documentation
│   ├── system/                 # System architecture docs
│   └── development/            # Development guidelines
├── captures/                   # Captured images (auto-created)
├── cropped_resellables/        # Processed object images (auto-created)
├── .env.example               # Environment template
├── test_agent_system.py       # Integration test script
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional (with defaults)
CAMERA_INDEX=0
ANALYSIS_DURATION_SECONDS=10
MAX_CAPTURES=6
CAPTURE_COOLDOWN_SECONDS=1.0
CONFIDENCE_THRESHOLD=0.25
CROP_BORDER_PERCENTAGE=0.3
```

### Agent Ports
- Camera Agent: 8001
- Detection Agent: 8002
- AI Evaluator Agent: 8003
- Image Processor Agent: 8004
- Report Coordinator Agent: 8005

## 📊 System Flow

1. **Initialization**: Report Coordinator receives StartSystem message
2. **Capture**: Camera Agent captures images at intervals
3. **Detection**: Detection Agent runs YOLO on captured images
4. **Evaluation**: AI Evaluator uses Gemini to assess resale value
5. **Processing**: Image Processor crops valuable objects
6. **Reporting**: Report Coordinator generates final analysis

## 🧪 Testing

### Run Integration Tests
```bash
python test_agent_system.py
```

### Manual Testing
1. Start all agents
2. Point camera at objects
3. Send StartSystem message
4. Observe processing pipeline
5. Check generated reports

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[System Architecture](docs/system/architecture.md)** - Complete system design
- **[Configuration Guide](docs/system/configuration.md)** - Setup and tuning
- **[Deployment Guide](docs/system/deployment.md)** - Production deployment
- **[Agent Documentation](docs/agents/)** - Individual agent details
- **[Development Guide](docs/development/contributing.md)** - Contributing guidelines

## 🔍 Monitoring and Health Checks

### Agent Status
Each agent provides health information on its port:
```bash
curl http://localhost:8001/health  # Camera Agent
curl http://localhost:8002/health  # Detection Agent
# ... etc for all agents
```

### System Logs
Agents log to console and optionally to files. Monitor logs for:
- Agent startup/shutdown
- Message processing
- Error conditions
- Performance metrics

## 🚀 Deployment Options

### Single Machine
All agents run on one machine (development/testing)

### Distributed
- **Edge Device**: Camera Agent (Raspberry Pi/Jetson)
- **GPU Server**: Detection Agent (for YOLO acceleration)
- **Cloud Server**: AI Evaluator, Image Processor, Report Coordinator

### Docker
```bash
docker-compose up -d
```

## 🛠️ Development

### Adding New Agents
1. Create agent file in `agents/`
2. Follow naming conventions
3. Implement required message handlers
4. Add documentation
5. Update tests

### Message Flow
Agents communicate via uAgents framework with typed message models:
- CapturedImage
- DetectionResult
- EvaluationResult
- ProcessingResult

## 🔐 Security

- API keys stored in environment variables
- Cryptographically secured agent communication
- Local image processing (privacy-preserving)
- No sensitive data logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow code standards in [docs/development/contributing.md](docs/development/contributing.md)
4. Add tests and documentation
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/Decluttered.ai/issues)
- **Documentation**: [docs/](docs/)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Decluttered.ai/discussions)

## 🙏 Acknowledgments

- **Fetch.ai** for the uAgents framework
- **Ultralytics** for YOLOv9 implementation
- **Google** for Gemini AI API
- **OpenCV** for computer vision capabilities

---

**Made with ❤️ for MHacks 2025**

*Transform your cluttered space into organized value with AI-powered multi-agent intelligence.*