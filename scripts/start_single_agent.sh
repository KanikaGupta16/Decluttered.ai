#!/bin/bash
# Single Agent Starter Script for Decluttered.ai
# Usage: ./start_single_agent.sh <agent_name>

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENTS_DIR="$PROJECT_ROOT/agents"

# Agent mapping
declare -A AGENTS=(
    ["camera"]="camera_agent.py"
    ["detection"]="detection_agent.py"
    ["evaluator"]="ai_evaluator_agent.py"
    ["processor"]="image_processor_agent.py"
    ["coordinator"]="report_coordinator_agent.py"
    ["webapi"]="web_api_agent.py"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_usage() {
    echo -e "${BLUE}Usage: $0 <agent_name>${NC}"
    echo ""
    echo "Available agents:"
    for agent in "${!AGENTS[@]}"; do
        echo -e "  ${GREEN}$agent${NC} -> ${AGENTS[$agent]}"
    done
    echo ""
    echo "Examples:"
    echo "  $0 camera    # Start camera agent"
    echo "  $0 detection # Start detection agent"
    echo "  $0 webapi    # Start web API agent"
}

check_dependencies() {
    echo -e "${BLUE}Checking dependencies...${NC}"

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 not found${NC}"
        exit 1
    fi

    # Check virtual environment (recommended)
    if [[ -z "$VIRTUAL_ENV" ]]; then
        echo -e "${YELLOW}Warning: No virtual environment detected${NC}"
        echo "Consider using: python -m venv venv && source venv/bin/activate"
    fi

    # Check required packages
    python3 -c "import uagents" 2>/dev/null || {
        echo -e "${RED}Error: uagents not installed. Run: pip install -r requirements.txt${NC}"
        exit 1
    }

    echo -e "${GREEN}Dependencies OK${NC}"
}

check_environment() {
    echo -e "${BLUE}Checking environment...${NC}"

    # Check .env file
    if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
        echo -e "${YELLOW}Warning: .env file not found${NC}"
        echo "Create one with required environment variables"
    fi

    # Check critical directories
    mkdir -p "$PROJECT_ROOT/captures"
    mkdir -p "$PROJECT_ROOT/cropped_resellables"
    mkdir -p "$PROJECT_ROOT/logs"

    echo -e "${GREEN}Environment OK${NC}"
}

start_agent() {
    local agent_name="$1"
    local agent_file="${AGENTS[$agent_name]}"
    local agent_path="$AGENTS_DIR/$agent_file"

    if [[ ! -f "$agent_path" ]]; then
        echo -e "${RED}Error: Agent file not found: $agent_path${NC}"
        exit 1
    fi

    echo -e "${BLUE}Starting $agent_name agent...${NC}"
    echo "Agent file: $agent_file"
    echo "Working directory: $PROJECT_ROOT"
    echo ""

    # Change to project root and start agent
    cd "$PROJECT_ROOT"

    # Create log file
    LOG_FILE="logs/${agent_name}_agent.log"

    echo -e "${GREEN}Agent starting... (logs: $LOG_FILE)${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    echo ""

    # Start the agent with logging
    python3 "$agent_path" 2>&1 | tee "$LOG_FILE"
}

# Main script
main() {
    # Check arguments
    if [[ $# -ne 1 ]]; then
        print_usage
        exit 1
    fi

    local agent_name="$1"

    # Validate agent name
    if [[ ! "${AGENTS[$agent_name]+isset}" ]]; then
        echo -e "${RED}Error: Unknown agent '$agent_name'${NC}"
        echo ""
        print_usage
        exit 1
    fi

    # Run checks
    check_dependencies
    check_environment

    echo ""
    echo -e "${GREEN}🚀 Starting Decluttered.ai Agent${NC}"
    echo "=================================="

    # Start the agent
    start_agent "$agent_name"
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}Agent stopped by user${NC}"; exit 0' INT

# Run main function
main "$@"