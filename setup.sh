#!/bin/bash

# =============================================================================
# Palo Alto Networks Prisma AIRS MCP Demo - Complete Setup Script
# =============================================================================
# This script sets up the complete Prisma AIRS integration with Claude Desktop
# using proper SSL handling via truststore (Python 3.10+)
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
DEMO_DIR="$HOME/prisma-airs-mcp-demo"
VENV_DIR="$DEMO_DIR/venv"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Palo Alto Networks Prisma AIRS MCP Demo Setup          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.10 or later.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')

echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Check if Python 3.10+ for truststore
if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
    echo -e "${GREEN}✅ Python 3.10+ detected - will use truststore for proper SSL${NC}"
    USE_TRUSTSTORE=true
else
    echo -e "${YELLOW}⚠️  Python $PYTHON_VERSION detected (< 3.10)${NC}"
    echo -e "${YELLOW}   Will use alternative SSL handling${NC}"
    USE_TRUSTSTORE=false
fi

# Check Claude Desktop config directory
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
if [[ ! -d "$CLAUDE_CONFIG_DIR" ]]; then
    echo -e "${YELLOW}⚠️  Claude Desktop config directory not found at expected location${NC}"
    echo "   Trying alternative locations..."
    
    for dir in "$HOME/.config/claude" "$HOME/.claude"; do
        if [[ -d "$dir" ]]; then
            CLAUDE_CONFIG_DIR="$dir"
            echo -e "${GREEN}✅ Found config directory at: $dir${NC}"
            break
        fi
    done
    
    if [[ ! -d "$CLAUDE_CONFIG_DIR" ]]; then
        echo -e "${RED}❌ Could not find Claude Desktop config directory${NC}"
        echo "   Please ensure Claude Desktop is installed"
        exit 1
    fi
fi

# Create demo directory
echo -e "\n${YELLOW}📁 Creating demo directory...${NC}"
mkdir -p "$DEMO_DIR"
cd "$DEMO_DIR"

# Copy server file from repository
echo -e "\n${YELLOW}📋 Copying server file...${NC}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cp "$SCRIPT_DIR/prisma_airs_mcp_server.py" "$DEMO_DIR/"

# Create virtual environment
echo -e "\n${YELLOW}🐍 Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --quiet --upgrade pip

# Install dependencies based on Python version
echo -e "\n${YELLOW}📦 Installing dependencies...${NC}"

if [ "$USE_TRUSTSTORE" = true ]; then
    # Python 3.10+ with truststore
    pip install --quiet --index-url https://pypi.org/simple --trusted-host pypi.org:443 truststore
    pip install --quiet requests python-dotenv fastmcp
    echo -e "${GREEN}✅ Installed with truststore support${NC}"
else
    # Python < 3.10 without truststore
    pip install --quiet requests python-dotenv fastmcp urllib3
    echo -e "${YELLOW}⚠️  Installed without truststore (using alternative SSL handling)${NC}"
fi

# Create .env.example
echo -e "\n${YELLOW}🔐 Creating configuration template...${NC}"
cat > .env.example << 'ENVEOF'
# Palo Alto Networks AI Security API Credentials
# Get these from your Palo Alto Networks account
PAN_AIRS_API_KEY=your_api_key_here
PAN_AIRS_PROFILE=your_profile_name
PAN_AIRS_API_URL=https://service.api.aisecurity.paloaltonetworks.com
ENVEOF

# Configure Claude Desktop
echo -e "\n${YELLOW}⚙️  Configuring Claude Desktop...${NC}"

VENV_PYTHON="$VENV_DIR/bin/python"
SERVER_PATH="$DEMO_DIR/prisma_airs_mcp_server.py"

cat > "$CLAUDE_CONFIG_DIR/claude_desktop_config.json" << CONFIGEOF
{
  "mcpServers": {
    "prisma-airs": {
      "command": "$VENV_PYTHON",
      "args": ["$SERVER_PATH"],
      "env": {
        "PAN_AIRS_API_KEY": "\${PAN_AIRS_API_KEY:-your_api_key_here}",
        "PAN_AIRS_PROFILE": "\${PAN_AIRS_PROFILE:-default}",
        "PAN_AIRS_API_URL": "\${PAN_AIRS_API_URL:-https://service.api.aisecurity.paloaltonetworks.com}"
      }
    }
  }
}
CONFIGEOF

# Create or copy .env file
if [[ -f ".env" ]]; then
    echo -e "${GREEN}✅ Using existing .env file${NC}"
else
    cp .env.example .env
    echo -e "${YELLOW}📝 Created .env file - please add your credentials${NC}"
fi

# Success message
echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ Setup Complete!                        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${MAGENTA}📋 Next Steps:${NC}"
echo -e "1. ${BLUE}Edit .env${NC} with your Palo Alto Networks API credentials"
echo -e "2. ${BLUE}Test connection:${NC} source venv/bin/activate && python prisma_airs_mcp_server.py test"
echo -e "3. ${BLUE}Restart Claude Desktop${NC}"
echo -e "4. ${BLUE}Test in Claude:${NC} 'List available MCP tools'"

echo -e "\n${BLUE}Demo location:${NC} $DEMO_DIR"
echo ""
