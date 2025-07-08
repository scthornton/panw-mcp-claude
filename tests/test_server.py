import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all required modules can be imported"""
    import prisma_airs_mcp_server
    assert prisma_airs_mcp_server.mcp is not None

def test_ssl_mode():
    """Test SSL mode detection"""
    import prisma_airs_mcp_server
    if sys.version_info >= (3, 10):
        assert prisma_airs_mcp_server.SSL_MODE == "truststore"
    else:
        assert prisma_airs_mcp_server.SSL_MODE == "bypass"
