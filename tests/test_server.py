"""
Test cases for the MCP Website Downloader server
"""

import pytest
import asyncio
from pathlib import Path
from mcp_windows_website_downloader.server import WebsiteDownloader

@pytest.fixture
def temp_directory(tmp_path):
    """Provide a temporary directory for testing"""
    return tmp_path

def test_downloader_initialization(temp_directory):
    """Test that the downloader initializes correctly"""
    downloader = WebsiteDownloader(str(temp_directory))
    assert downloader.base_directory == temp_directory
    assert downloader.base_directory.exists()

@pytest.mark.asyncio
async def test_tool_registration():
    """Test that tools are registered correctly"""
    from mcp.server import Server
    
    server = Server("website-downloader")
    tools = await server.list_tools()
    
    tool_names = [tool.name for tool in tools]
    assert "download-website" in tool_names
    assert "get-status" in tool_names