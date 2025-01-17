"""MCP request handlers."""
from typing import Dict, Any
from mcp import MCPError
from .downloader import WebsiteDownloader

class Handlers:
    """Website downloader request handlers."""
    
    def __init__(self, downloader: WebsiteDownloader):
        self.downloader = downloader
        
    async def download_website(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle website download requests."""
        url = params.get("url")
        if not url:
            raise MCPError("URL parameter is required")
            
        include_assets = params.get("include_assets", True)
        
        result = await self.downloader.download_website(
            url=url,
            include_assets=include_assets
        )
        
        if not result["success"]:
            raise MCPError(result.get("error", "Download failed"))
            
        return result