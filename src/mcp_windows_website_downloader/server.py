"""
MCP Website Downloader - Windows
Downloads websites and their assets with proper Windows path handling
"""
import os
from pathlib import Path
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from pathlib import Path
import logging
from typing import Any, Dict
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('website_downloader')

class WebsiteDownloader:
    def __init__(self, save_dir: Path):
        self.save_dir = save_dir
        self.session = None

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    def _clean_filename(self, url: str) -> str:
        """Create valid Windows filename from URL"""
        parsed = urlparse(url)
        name = parsed.netloc + parsed.path.replace('/', '_')
        # Remove invalid Windows filename chars
        return ''.join(c for c in name if c not in '<>:"/\\|?*')

    async def download(self, url: str, include_assets: bool = True) -> Dict[str, Any]:
        await self.init_session()
        if not self.session:
            return {"status": "error", "message": "Failed to initialize session"}

        try:
            # Download main page
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {
                        "status": "error",
                        "message": f"HTTP {response.status}: {response.reason}"
                    }
                content = await response.text()

            # Setup save directory
            site_dir = self.save_dir / self._clean_filename(url)
            site_dir.mkdir(parents=True, exist_ok=True)

            soup = BeautifulSoup(content, 'html.parser')
            assets = []

            if include_assets:
                # Handle images
                os.makedirs(site_dir / 'images', exist_ok=True)
                for img in soup.find_all('img', src=True):
                    try:
                        src = urljoin(url, img['src'])
                        filename = self._clean_filename(src)
                        save_path = site_dir / 'images' / filename
                        
                        async with self.session.get(src) as resp:
                            if resp.status == 200:
                                with open(save_path, 'wb') as f:
                                    f.write(await resp.read())
                                img['src'] = f'images/{filename}'
                                assets.append(src)
                    except Exception as e:
                        logger.warning(f"Failed to download image {src}: {e}")

                # Handle CSS
                os.makedirs(site_dir / 'css', exist_ok=True)
                for css in soup.find_all('link', rel='stylesheet', href=True):
                    try:
                        href = urljoin(url, css['href'])
                        filename = self._clean_filename(href)
                        save_path = site_dir / 'css' / filename
                        
                        async with self.session.get(href) as resp:
                            if resp.status == 200:
                                with open(save_path, 'w', encoding='utf-8') as f:
                                    f.write(await resp.text())
                                css['href'] = f'css/{filename}'
                                assets.append(href)
                    except Exception as e:
                        logger.warning(f"Failed to download CSS {href}: {e}")

                # Handle JavaScript
                os.makedirs(site_dir / 'js', exist_ok=True)
                for script in soup.find_all('script', src=True):
                    try:
                        src = urljoin(url, script['src'])
                        filename = self._clean_filename(src)
                        save_path = site_dir / 'js' / filename
                        
                        async with self.session.get(src) as resp:
                            if resp.status == 200:
                                with open(save_path, 'w', encoding='utf-8') as f:
                                    f.write(await resp.text())
                                script['src'] = f'js/{filename}'
                                assets.append(src)
                    except Exception as e:
                        logger.warning(f"Failed to download JS {src}: {e}")

            # Save processed HTML
            with open(site_dir / 'index.html', 'w', encoding='utf-8') as f:
                f.write(str(soup))

            return {
                "status": "success",
                "url": url,
                "saved_to": str(site_dir),
                "assets_downloaded": len(assets)
            }

        except Exception as e:
            logger.error(f"Download failed: {e}")
            return {
                "status": "error",
                "url": url,
                "message": str(e)
            }

def main():
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Website Downloader MCP Server')
    parser.add_argument('--directory', type=str, default='downloads',
                       help='Directory to save downloaded sites')
    args = parser.parse_args()

    save_dir = Path(args.directory).resolve()
    save_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Saving downloads to: {save_dir}")

    downloader = WebsiteDownloader(save_dir)
    server = Server("website-downloader")

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="download-website",
                description="Download a website with its assets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Website URL to download"
                        },
                        "include_assets": {
                            "type": "boolean",
                            "description": "Download images, CSS, JS",
                            "default": True
                        }
                    },
                    "required": ["url"]
                }
            )
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, 
        arguments: Dict[str, Any] | None
    ) -> list[types.TextContent]:
        try:
            if not arguments:
                raise ValueError("Arguments required")

            if name == "download-website":
                result = await downloader.download(
                    arguments["url"],
                    arguments.get("include_assets", True)
                )
                return [types.TextContent(
                    type="text",
                    text=str(result)
                )]
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            logger.error(f"Tool error: {e}")
            return [types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]

    async def run_server():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            try:
                await server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="website-downloader",
                        server_version="0.1.0",
                        capabilities=server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )
            finally:
                await downloader.close()

    asyncio.run(run_server())

if __name__ == '__main__':
    main()