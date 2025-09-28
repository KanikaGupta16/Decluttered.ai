#!/bin/bash
# Decluttered.ai System Startup Script
# Starts all agents in the background

echo "🤖 Starting Decluttered.ai Multi-Agent System..."
echo "================================================"

# Check prerequisites
if ! python3 --version &> /dev/null && ! python --version &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.10+"
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure"
    exit 1
fi

# Create logs directory
mkdir -p logs

echo "📋 Starting agents..."

# Start agents in background with logging
echo "🎥 Starting Camera Agent..."
$PYTHON_CMD agents/camera_agent.py > logs/camera_agent.log 2>&1 &
CAMERA_PID=$!
echo "   Camera Agent PID: $CAMERA_PID"

sleep 2

echo "🔍 Starting Detection Agent..."
$PYTHON_CMD agents/detection_agent.py > logs/detection_agent.log 2>&1 &
DETECTION_PID=$!
echo "   Detection Agent PID: $DETECTION_PID"

sleep 2

echo "🧠 Starting AI Evaluator Agent..."
$PYTHON_CMD agents/ai_evaluator_agent.py > logs/ai_evaluator_agent.log 2>&1 &
AI_PID=$!
echo "   AI Evaluator Agent PID: $AI_PID"

sleep 2

echo "✂️ Starting Image Processor Agent..."
$PYTHON_CMD agents/image_processor_agent.py > logs/image_processor_agent.log 2>&1 &
PROCESSOR_PID=$!
echo "   Image Processor Agent PID: $PROCESSOR_PID"

sleep 2

echo "📊 Starting Report Coordinator Agent..."
$PYTHON_CMD agents/report_coordinator_agent.py > logs/report_coordinator_agent.log 2>&1 &
COORDINATOR_PID=$!
echo "   Report Coordinator Agent PID: $COORDINATOR_PID"

sleep 2

echo "🌐 Starting Web API Agent..."
$PYTHON_CMD agents/web_api_agent.py > logs/web_api_agent.log 2>&1 &
WEB_API_PID=$!
echo "   Web API Agent PID: $WEB_API_PID"

# Save PIDs for cleanup
echo $CAMERA_PID > .camera.pid
echo $DETECTION_PID > .detection.pid
echo $AI_PID > .ai.pid
echo $PROCESSOR_PID > .processor.pid
echo $COORDINATOR_PID > .coordinator.pid
echo $WEB_API_PID > .webapi.pid

echo ""
echo "✅ All agents started successfully!"
echo ""
echo "📊 Agent Status:"
echo "   🎥 Camera Agent:        http://localhost:8001 (PID: $CAMERA_PID)"
echo "   🔍 Detection Agent:     http://localhost:8002 (PID: $DETECTION_PID)"
echo "   🧠 AI Evaluator Agent:  http://localhost:8003 (PID: $AI_PID)"
echo "   ✂️ Image Processor:     http://localhost:8004 (PID: $PROCESSOR_PID)"
echo "   📊 Report Coordinator:  http://localhost:8005 (PID: $COORDINATOR_PID)"
echo "   🌐 Web API Agent:       http://localhost:8006 (PID: $WEB_API_PID)"
echo ""
echo "📝 Log files saved to logs/ directory"
echo ""
echo "🚀 Next Steps:"
echo "   1. Check agent logs: tail -f logs/camera_agent.log"
echo "   2. Monitor all logs: tail -f logs/*.log"
echo "   3. Send StartSystem message to port 8005 to begin processing"
echo "   4. Use scripts/stop_system.sh to shutdown all agents"
echo ""
echo "💡 Tips:"
echo "   • Camera feed will appear when capture starts"
echo "   • Check logs for any startup errors"
echo "   • Use scripts/health_check.sh to monitor agent status"
echo ""
echo "🎯 System ready for processing!"