# Agentverse Mailbox Agent Deployment Guide

This guide walks you through deploying your Decluttered.ai agents as mailbox agents on the Fetch.ai Agentverse platform.

## Prerequisites

### 1. Dependencies Installation
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file with required API keys:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
CAPTURE_FOLDER=captures
CROPPED_FOLDER=cropped_resellables
ANALYSIS_DURATION_SECONDS=10
MAX_CAPTURES=6
CAPTURE_COOLDOWN_SECONDS=1.0
WEB_API_PORT=8006
```

### 3. Agentverse Account
- Create an account at [agentverse.ai](https://agentverse.ai)
- Familiarize yourself with the dashboard

## Agent Conversion Summary

✅ **Converted Agents to Mailbox Agents:**
- `camera_agent.py` - Handles camera operations and image capture
- `detection_agent.py` - YOLO-based object detection
- `ai_evaluator_agent.py` - Gemini AI resale value evaluation
- `image_processor_agent.py` - Image cropping and processing
- `report_coordinator_agent.py` - Central coordination and reporting
- `web_api_agent.py` - Web interface and file uploads

All agents now have `mailbox=True` enabled in their configuration.

## Deployment Steps

### Step 1: Quick Deployment (Automated)
```bash
# Run the automated deployment script
python deploy_agents.py
```

This script will:
- Check all dependencies
- Verify environment variables
- Start all agents simultaneously
- Monitor agent health
- Provide shutdown handling

### Step 2: Manual Deployment (Individual Agents)

If you prefer to start agents individually:

```bash
# Terminal 1 - Camera Agent
cd /path/to/Decluttered.ai
python agents/camera_agent.py

# Terminal 2 - Detection Agent
python agents/detection_agent.py

# Terminal 3 - AI Evaluator Agent
python agents/ai_evaluator_agent.py

# Terminal 4 - Image Processor Agent
python agents/image_processor_agent.py

# Terminal 5 - Report Coordinator Agent
python agents/report_coordinator_agent.py

# Terminal 6 - Web API Agent
python agents/web_api_agent.py
```

### Step 3: Verify Agent Registration

Once running, your agents will automatically:
1. Connect to the Agentverse mailbox system
2. Register themselves with their unique addresses
3. Appear in your Agentverse dashboard

**Check the Agentverse Dashboard:**
- Go to [agentverse.ai](https://agentverse.ai)
- Navigate to "My Agents"
- Verify all 6 agents are listed and active

### Step 4: Agent Communication Setup

The agents communicate through the following message flow:
```
Camera Agent → Detection Agent → AI Evaluator → Image Processor → Report Coordinator
                                                        ↕
                                                   Web API Agent
```

## Agent Addresses and Communication

Each agent will have a unique Agentverse address. You can find these in:
- The Agentverse dashboard
- Agent startup logs
- By checking the agent's `address` property

### Inter-Agent Messaging

To enable proper communication, you may need to update the TODO sections in each agent:

**Example for detection_agent.py line 193:**
```python
# Replace this line:
# await ctx.send("ai_evaluator_agent_address", detection_result)

# With the actual Agentverse address:
await ctx.send("agent1qw5v...", detection_result)
```

## Testing the System

### Test 1: Individual Agent Health
```bash
python test_agent_system.py
```

### Test 2: End-to-End Workflow
1. Use the Web API to upload an image
2. Monitor agent logs for message flow
3. Check for generated cropped images
4. Verify analysis report creation

### Test 3: Web Interface
```bash
# Access the web interface
curl http://localhost:8006/health

# Upload test image
curl -X POST -F "files=@test_image.jpg" http://localhost:8006/upload
```

## Production Deployment

### Option 1: Cloud VM Deployment
1. Deploy to a cloud VM (AWS, GCP, Azure)
2. Configure firewall rules for agent ports
3. Set up process monitoring (systemd, supervisord)
4. Configure reverse proxy for web API

### Option 2: Docker Deployment
```bash
# Build Docker images for each agent
docker build -t decluttered-agents .

# Run with docker-compose
docker-compose up -d
```

### Option 3: Agentverse Hosting
Some agents may be suitable for full Agentverse hosting:
- AI Evaluator Agent (lightweight)
- Report Coordinator Agent
- Simple message routing agents

## Monitoring and Maintenance

### Health Checks
```bash
# Check agent status
python -c "
import requests
print('Web API:', requests.get('http://localhost:8006/health').json())
"
```

### Log Monitoring
- Agent logs appear in terminal output
- Consider using centralized logging (ELK stack, Fluentd)

### Performance Monitoring
- Monitor CPU/memory usage
- Track message processing latency
- Set up alerts for agent failures

## Troubleshooting

### Common Issues

**Agent Won't Start:**
- Check Python dependencies
- Verify environment variables
- Check port availability

**Agent Not Appearing in Agentverse:**
- Verify internet connectivity
- Check Agentverse account status
- Ensure mailbox=True is set

**Inter-Agent Communication Fails:**
- Verify agent addresses
- Check message model compatibility
- Monitor Agentverse message logs

**Camera Access Issues:**
- Check camera permissions
- Verify camera index (default: 0)
- Test with `cv2.VideoCapture(0)`

### Debug Mode
Run agents with increased logging:
```bash
export PYTHONPATH="."
python -u agents/camera_agent.py
```

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Network Security**: Use HTTPS in production
3. **File Uploads**: Validate file types and sizes
4. **Agent Authentication**: Use Agentverse security features

## Support and Resources

- [Fetch.ai Documentation](https://docs.fetch.ai)
- [μAgents Framework](https://github.com/fetchai/uAgents)
- [Agentverse Platform](https://agentverse.ai)
- [Project Repository Issues](https://github.com/your-repo/issues)

---

🎉 **Congratulations!** Your Decluttered.ai multi-agent system is now deployed as mailbox agents and ready for production use!