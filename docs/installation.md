# Installation Guide

## Prerequisites

Before installing the Prisma AIRS MCP integration, ensure you have:

1. **Claude Desktop** - Download from [claude.ai/desktop](https://claude.ai/desktop)
2. **Python 3.9 or higher** - We recommend 3.10+ for better SSL support
3. **Palo Alto Networks API credentials** - Contact your account representative

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/prisma-airs-mcp.git
cd prisma-airs-mcp
```

### 2. Run the Setup Script

```bash
./setup.sh
```

This script will:
- Check your Python version
- Create a virtual environment
- Install dependencies
- Configure Claude Desktop
- Set up the MCP server

### 3. Configure API Credentials

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```
PAN_AIRS_API_KEY=your_actual_api_key
PAN_AIRS_PROFILE=your_profile_name
```

### 4. Test the Connection

```bash
source ~/prisma-airs-mcp-demo/venv/bin/activate
python ~/prisma-airs-mcp-demo/prisma_airs_mcp_server.py test
```

### 5. Restart Claude Desktop

Completely quit and restart Claude Desktop for the changes to take effect.

## Verification

In Claude Desktop, type:
```
List available MCP tools
```

You should see the Prisma AIRS tools listed.

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for common issues and solutions.
