#!/bin/bash
# Decluttered.ai System Shutdown Script
# Stops all running agents

echo "🛑 Stopping Decluttered.ai Multi-Agent System..."
echo "==============================================="

# Function to stop agent by PID file
stop_agent() {
    local pid_file=$1
    local agent_name=$2

    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if kill -0 $PID 2>/dev/null; then
            echo "🛑 Stopping $agent_name (PID: $PID)..."
            kill $PID
            sleep 1

            # Force kill if still running
            if kill -0 $PID 2>/dev/null; then
                echo "   Force stopping $agent_name..."
                kill -9 $PID
            fi
            echo "   ✅ $agent_name stopped"
        else
            echo "   ⚠️ $agent_name was not running"
        fi
        rm "$pid_file"
    else
        echo "   ❓ No PID file found for $agent_name"
    fi
}

# Stop all agents
stop_agent ".camera.pid" "Camera Agent"
stop_agent ".detection.pid" "Detection Agent"
stop_agent ".ai.pid" "AI Evaluator Agent"
stop_agent ".processor.pid" "Image Processor Agent"
stop_agent ".coordinator.pid" "Report Coordinator Agent"
stop_agent ".webapi.pid" "Web API Agent"

# Clean up any remaining processes
echo ""
echo "🧹 Cleaning up any remaining processes..."
pkill -f "agents/.*\.py" 2>/dev/null

echo ""
echo "✅ All agents stopped successfully!"
echo ""
echo "📁 Files preserved:"
echo "   📸 Captured images: captures/"
echo "   ✂️ Cropped images: cropped_resellables/"
echo "   📄 Reports: *.txt files"
echo "   📝 Logs: logs/"
echo ""
echo "🔄 To restart the system: ./scripts/start_system.sh"