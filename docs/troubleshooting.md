# Troubleshooting Guide

## Common Issues

### MCP Server Not Showing in Claude

1. **Ensure Claude Desktop is fully restarted**
   - Quit Claude Desktop completely (Cmd+Q on Mac)
   - Reopen Claude Desktop

2. **Check configuration location**
   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

3. **Verify server can run**
   ```bash
   cd ~/prisma-airs-mcp-demo
   source venv/bin/activate
   python prisma_airs_mcp_server.py test
   ```

### SSL Certificate Errors

**For Python 3.10+:**
- The truststore library should handle certificates automatically
- If issues persist, update your system certificates

**For Python 3.9:**
- SSL verification is bypassed for development
- Consider upgrading to Python 3.10+ for production use

### API Connection Failed

1. **Check credentials**
   ```bash
   cat ~/prisma-airs-mcp-demo/.env
   ```

2. **Verify API endpoint**
   - Default: `https://service.api.aisecurity.paloaltonetworks.com`
   - Contact Palo Alto Networks for correct endpoint

3. **Test with curl**
   ```bash
   curl -X POST https://service.api.aisecurity.paloaltonetworks.com/v1/scan/sync/request \
     -H "x-pan-token: YOUR_API_KEY" \
     -H "Content-Type: application/json"
   ```

### Tools Not Working

1. **Check if tools are listed**
   ```
   List available MCP tools
   ```

2. **Try explicit tool call**
   ```
   Use pan_inline_scan to check:
   - prompt: "test"
   - response: "test"
   ```

## Getting Help

- Open an issue on [GitHub](https://github.com/your-username/prisma-airs-mcp/issues)
- Check existing issues for solutions
- Include error messages and system info
