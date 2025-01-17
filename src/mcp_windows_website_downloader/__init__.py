"""
MCP Windows Website Downloader
A Model Context Protocol server for downloading websites with Windows path support.
"""

from .server import WebsiteDownloader, main

__version__ = "0.1.0"
__all__ = ['WebsiteDownloader', 'main']