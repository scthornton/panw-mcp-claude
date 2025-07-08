#!/usr/bin/env python3
"""
Palo Alto Networks Prisma AIRS MCP Server
Real-time AI security scanning for Claude Desktop
"""

import asyncio
import json
import os
import sys
import uuid
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, TypedDict

# Handle SSL based on Python version
if sys.version_info >= (3, 10):
    # Python 3.10+ - use truststore for proper SSL
    import truststore
    truststore.inject_into_ssl()
    SSL_MODE = "truststore"
    VERIFY_SSL = True
else:
    # Python < 3.10 - disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    SSL_MODE = "bypass"
    VERIFY_SSL = False

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("prisma-airs-mcp")

# Configuration
API_KEY = os.getenv("PAN_AIRS_API_KEY")
PROFILE = os.getenv("PAN_AIRS_PROFILE", "default")
API_URL = os.getenv("PAN_AIRS_API_URL", "https://service.api.aisecurity.paloaltonetworks.com")

# Constants
MAX_NUMBER_OF_BATCH_SCAN_OBJECTS = 5
MAX_NUMBER_OF_SCAN_IDS = 20

# Type definitions
class SimpleScanContent(TypedDict):
    prompt: str
    response: str

@asynccontextmanager
async def lifespan(mcp: FastMCP):
    """Lifespan manager for the MCP server"""
    logger.info("🚀 Palo Alto Networks Prisma AIRS MCP Server")
    logger.info(f"📍 Profile: {PROFILE}")
    logger.info(f"🌐 Endpoint: {API_URL}")
    logger.info(f"🔒 SSL Mode: {SSL_MODE}")
    logger.info(f"🐍 Python: {sys.version.split()[0]}")
    
    if not API_KEY:
        logger.warning("⚠️  No API key found! Set PAN_AIRS_API_KEY in .env file")
    
    yield
    logger.info("👋 Shutting down Prisma AIRS MCP Server...")

mcp.lifespan = lifespan

def make_api_request(endpoint: str, payload: Dict, timeout: int = 30) -> Dict[str, Any]:
    """
    Make API request with appropriate SSL handling
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-pan-token": API_KEY,
        "User-Agent": "PAN-AI-Security-MCP/1.0"
    }
    
    try:
        response = requests.post(
            f"{API_URL}{endpoint}",
            headers=headers,
            json=payload,
            verify=VERIFY_SSL,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.SSLError as e:
        logger.error(f"SSL Error: {e}")
        if SSL_MODE == "truststore":
            logger.info("Try updating your system certificates or upgrading Python")
        return {"error": f"SSL Error: {str(e)}", "success": False}
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return {"error": str(e), "success": False}

@mcp.tool()
async def pan_inline_scan(prompt: str, response: str) -> Dict[str, Any]:
    """
    Scan a single prompt/response pair for security threats
    
    This tool analyzes AI interactions for various security risks including:
    - Prompt injection attacks
    - Malicious code generation requests
    - Data exfiltration attempts
    - Toxic or harmful content
    - Policy violations
    
    Args:
        prompt: The user's input message to scan
        response: The AI's response message to scan
        
    Returns:
        Dictionary containing:
        - success: Whether the scan completed successfully
        - scan_id: Unique identifier for this scan
        - verdict: "benign" or "malicious"
        - action: "allow" or "block"
        - threats: List of detected threat types
    """
    payload = {
        "tr_id": str(uuid.uuid4()),
        "ai_profile": {"profile_name": PROFILE},
        "contents": [{"prompt": prompt, "response": response}]
    }
    
    result = await asyncio.get_event_loop().run_in_executor(
        None, make_api_request, "/v1/scan/sync/request", payload
    )
    
    if "error" in result:
        return {"success": False, "error": result["error"]}
    
    # Extract and format results
    scan_data = {
        "success": True,
        "scan_id": result.get("scan_id"),
        "verdict": result.get("category", "unknown"),
        "action": result.get("action", "unknown"),
        "threats": []
    }
    
    # Extract specific threats
    if result.get("prompt_detected"):
        for threat, detected in result["prompt_detected"].items():
            if detected:
                scan_data["threats"].append(f"prompt:{threat}")
    
    if result.get("response_detected"):
        for threat, detected in result["response_detected"].items():
            if detected:
                scan_data["threats"].append(f"response:{threat}")
    
    return scan_data

@mcp.tool()
async def pan_batch_scan(scan_objects: List[SimpleScanContent]) -> Dict[str, Any]:
    """
    Perform batch scanning of multiple prompt/response pairs
    
    More efficient than multiple inline scans when analyzing conversations
    or multiple interactions at once.
    
    Args:
        scan_objects: List of prompt/response pairs (max 5)
                     Each object should have 'prompt' and 'response' fields
        
    Returns:
        Dictionary containing:
        - success: Whether the batch scan was submitted successfully
        - scan_ids: List of scan IDs for retrieving results later
        - count: Number of scans submitted
    """
    if len(scan_objects) > MAX_NUMBER_OF_BATCH_SCAN_OBJECTS:
        return {
            "success": False,
            "error": f"Maximum {MAX_NUMBER_OF_BATCH_SCAN_OBJECTS} objects allowed per batch"
        }
    
    # Build batch request
    scan_requests = []
    for i, obj in enumerate(scan_objects):
        scan_requests.append({
            "req_id": i,  # Must be integer
            "scan_req": {  # Must be "scan_req" not "scan_request"
                "ai_profile": {"profile_name": PROFILE},
                "contents": [{
                    "prompt": obj["prompt"],
                    "response": obj["response"]
                }]
            }
        })
    
    payload = {"scan_objects": scan_requests}
    
    result = await asyncio.get_event_loop().run_in_executor(
        None, make_api_request, "/v1/scan/async/request", payload
    )
    
    if "error" in result:
        return {"success": False, "error": result["error"]}
    
    return {
        "success": True,
        "scan_ids": result.get("scan_ids", []),
        "count": len(result.get("scan_ids", []))
    }

@mcp.tool()
async def pan_get_scan_results(scan_ids: List[str]) -> Dict[str, Any]:
    """
    Retrieve scan results by scan IDs
    
    Use this to get results from batch scans after submission.
    
    Args:
        scan_ids: List of scan IDs to retrieve (max 20)
        
    Returns:
        Scan results for each ID including verdicts and threats
    """
    # Note: This endpoint implementation depends on API documentation
    return {
        "success": False,
        "error": "Result retrieval endpoint not yet implemented",
        "note": "This feature requires additional API endpoint documentation"
    }

@mcp.tool()
async def pan_get_scan_reports(scan_ids: List[str]) -> Dict[str, Any]:
    """
    Get detailed threat analysis reports for scan IDs
    
    Provides comprehensive threat intelligence and remediation guidance.
    
    Args:
        scan_ids: List of scan IDs to get detailed reports for
        
    Returns:
        Detailed threat analysis and recommendations
    """
    # Note: This endpoint implementation depends on API documentation
    return {
        "success": False,
        "error": "Report retrieval endpoint not yet implemented",
        "note": "This feature requires additional API endpoint documentation"
    }

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("\n🧪 Testing Prisma AIRS connection...")
        print(f"   SSL Mode: {SSL_MODE}")
        print(f"   Endpoint: {API_URL}")
        
        if not API_KEY:
            print("❌ No API key found! Please set PAN_AIRS_API_KEY in .env file")
            sys.exit(1)
        
        test_result = make_api_request("/v1/scan/sync/request", {
            "tr_id": f"test-{uuid.uuid4()}",
            "ai_profile": {"profile_name": PROFILE},
            "contents": [{"prompt": "test", "response": "test"}]
        })
        
        if "error" not in test_result:
            print("✅ Connection successful!")
            print(f"   Verdict: {test_result.get('category', 'unknown')}")
            print(f"   Profile: {PROFILE}")
        else:
            print(f"❌ Connection failed: {test_result['error']}")
    else:
        mcp.run(transport="stdio")
