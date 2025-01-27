"""
MCP Windows Website Downloader
A simple MCP server for downloading website documentation.
"""
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

__version__ = "0.1.0"