"""
Example usage of the MCP website downloader
"""
import asyncio
from pathlib import Path
from mcp.client import Client

async def main():
    # Connect to MCP server
    async with Client() as client:
        # Download documentation
        result = await client.call_tool(
            "download",
            {"url": "https://docs.example.com"}
        )
        print(f"Download result: {result}")

if __name__ == "__main__":
    asyncio.run(main())