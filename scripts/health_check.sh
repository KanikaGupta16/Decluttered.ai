#!/bin/bash
# Decluttered.ai Health Check Script
# Monitors the status of all agents

echo "🏥 Decluttered.ai System Health Check"
echo "====================================="

# Agent configuration
declare -A AGENTS
AGENTS[8001]="🎥 Camera Agent"
AGENTS[8002]="🔍 Detection Agent"
AGENTS[8003]="🧠 AI Evaluator Agent"
AGENTS[8004]="✂️ Image Processor Agent"
AGENTS[8005]="📊 Report Coordinator Agent"
AGENTS[8006]="🌐 Web API Agent"

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is not in use
    fi
}

# Function to check agent health via HTTP (if implemented)
check_agent_health() {
    local port=$1
    # Try to connect to the agent (basic connectivity check)
    if nc -z localhost $port 2>/dev/null; then
        return 0  # Agent responding
    else
        return 1  # Agent not responding
    fi
}

echo "🔍 Checking agent status..."
echo ""

healthy_count=0
total_agents=${#AGENTS[@]}

for port in "${!AGENTS[@]}"; do
    agent_name="${AGENTS[$port]}"

    if check_port $port; then
        echo "✅ $agent_name (port $port) - Running"
        ((healthy_count++))
    else
        echo "❌ $agent_name (port $port) - Not running"
    fi
done

echo ""
echo "📊 System Status Summary:"
echo "   Healthy agents: $healthy_count/$total_agents"

if [ $healthy_count -eq $total_agents ]; then
    echo "   Overall status: 🟢 HEALTHY"
    exit_code=0
elif [ $healthy_count -gt 0 ]; then
    echo "   Overall status: 🟡 PARTIAL"
    exit_code=1
else
    echo "   Overall status: 🔴 DOWN"
    exit_code=2
fi

echo ""
echo "📁 System Resources:"

# Check disk space for important directories
if [ -d "captures" ]; then
    captures_size=$(du -sh captures 2>/dev/null | cut -f1)
    echo "   📸 Captures folder: $captures_size"
fi

if [ -d "cropped_resellables" ]; then
    cropped_size=$(du -sh cropped_resellables 2>/dev/null | cut -f1)
    echo "   ✂️ Cropped folder: $cropped_size"
fi

if [ -d "logs" ]; then
    logs_size=$(du -sh logs 2>/dev/null | cut -f1)
    echo "   📝 Logs folder: $logs_size"
fi

# Check memory usage of Python processes
echo ""
echo "💾 Memory Usage:"
if command -v ps &> /dev/null; then
    python_mem=$(ps aux | grep "agents/.*\.py" | grep -v grep | awk '{sum+=$6} END {printf "%.1f MB\n", sum/1024}')
    echo "   🐍 Python agents: $python_mem"
fi

echo ""
echo "🔧 Quick Actions:"
if [ $healthy_count -lt $total_agents ]; then
    echo "   • Start missing agents: ./scripts/start_system.sh"
    echo "   • Check logs: tail -f logs/*.log"
    echo "   • Restart system: ./scripts/stop_system.sh && ./scripts/start_system.sh"
else
    echo "   • View logs: tail -f logs/*.log"
    echo "   • Stop system: ./scripts/stop_system.sh"
fi

exit $exit_code