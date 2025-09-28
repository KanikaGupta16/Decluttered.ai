#!/bin/bash
# Agent Process Killer Script for Decluttered.ai
# Kills all agent processes and frees up ports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 Decluttered.ai Agent Killer${NC}"
echo "================================"

# Agent ports
PORTS=(8001 8002 8003 8004 8005 8006)

echo -e "${YELLOW}Checking for processes on agent ports...${NC}"

# Find processes using agent ports
PIDS=$(lsof -ti:${PORTS[*]} 2>/dev/null || true)

if [ -n "$PIDS" ]; then
    echo -e "${RED}Found processes on ports: ${PORTS[*]}${NC}"
    echo "PIDs: $PIDS"

    echo -e "${YELLOW}Killing processes...${NC}"
    for PID in $PIDS; do
        if kill -9 $PID 2>/dev/null; then
            echo -e "  ✅ Killed PID: $PID"
        else
            echo -e "  ⚠️  PID $PID already dead"
        fi
    done
else
    echo -e "${GREEN}No processes found on agent ports${NC}"
fi

# Kill any remaining Python agent processes
echo -e "${YELLOW}Checking for Python agent processes...${NC}"
AGENT_PIDS=$(pgrep -f "python.*agent" 2>/dev/null || true)

if [ -n "$AGENT_PIDS" ]; then
    echo -e "${RED}Found Python agent processes:${NC}"
    echo "$AGENT_PIDS"

    echo -e "${YELLOW}Killing Python agent processes...${NC}"
    pkill -f "python.*agent" 2>/dev/null || true
    echo -e "${GREEN}Python agent processes killed${NC}"
else
    echo -e "${GREEN}No Python agent processes found${NC}"
fi

# Verify ports are free
echo -e "${YELLOW}Verifying ports are free...${NC}"
for PORT in "${PORTS[@]}"; do
    if lsof -ti:$PORT >/dev/null 2>&1; then
        echo -e "  ❌ Port $PORT still in use"
    else
        echo -e "  ✅ Port $PORT is free"
    fi
done

echo ""
echo -e "${GREEN}🎉 Agent cleanup complete!${NC}"
echo "You can now start agents with:"
echo "  python3 deploy_agents.py"
echo "  or python3 agents/camera_agent.py"