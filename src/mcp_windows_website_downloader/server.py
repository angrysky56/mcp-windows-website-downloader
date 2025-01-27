"""
MCP server implementation for website downloader.
"""
import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, Any, List
import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import LoggingCapability, ToolsCapability
import mcp.server.lowlevel.server as server
import mcp.server.stdio
from .downloader import WebsiteDownloader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebsiteDownloaderServer:
    """MCP server for downloading documentation websites"""
    
    def __init__(self, library_dir: Path):
        self.library_dir = library_dir
        logger.info(f"Initializing downloader with library dir: {library_dir}")
        abs_path = library_dir.absolute()
        logger.info(f"Absolute library path: {abs_path}")
        if not abs_path.exists():
            abs_path.mkdir(parents=True)
            logger.info(f"Created library directory at {abs_path}")
        self.downloader = WebsiteDownloader(abs_path)
        self.server = Server("mcp-windows-website-downloader")
        self._tasks = set()
        self._setup_tools()
        logger.info("Server initialized")
        
    def _setup_tools(self):
        """Configure MCP tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            logger.info("Listing tools")
            tools = [
                types.Tool(
                    name="download",
                    description="Download documentation website for RAG indexing",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "Documentation site URL"
                            }
                        },
                        "required": ["url"]
                    }
                )
            ]
            logger.info(f"Returning {len(tools)} tools")
            return tools
            
        @self.server.call_tool()
        async def handle_call_tool(
            name: str,
            arguments: Dict[str, Any] | None,
            progress_callback = None
        ) -> List[types.TextContent]:
            """Handle tool calls"""
            logger.info(f"Tool called: {name} with args {arguments}")
            try:
                if name != "download":
                    raise ValueError(f"Unknown tool: {name}")
                    
                if not arguments or "url" not in arguments:
                    raise ValueError("URL is required")

                url = arguments["url"]
                
                # Create download task with progress tracking
                async def download_with_progress():
                    try:
                        logger.info(f"Starting download of {url}")
                        result = await self.downloader.download(url)
                        logger.info("Download complete")
                        return result
                    except asyncio.CancelledError:
                        logger.info("Download task cancelled")
                        raise
                    except Exception as e:
                        logger.error(f"Download failed: {str(e)}")
                        raise

                task = asyncio.create_task(download_with_progress())
                self._tasks.add(task)
                try:
                    result = await task
                finally:
                    self._tasks.remove(task)
                    
                return [types.TextContent(
                    type="text", 
                    text=str(result)
                )]
                
            except asyncio.CancelledError:
                logger.info("Tool call cancelled")
                raise
            except Exception as e:
                logger.error(f"Tool error: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
                
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting server")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("Got stdio streams")
            try:
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options(
                        notification_options=server.NotificationOptions(
                            tools_changed=False,
                            prompts_changed=False,
                            resources_changed=False
                        ),
                        experimental_capabilities={}
                    )
                )
                
            except asyncio.CancelledError:
                logger.info("Server received cancel signal")
                # Clean shutdown - cancel tasks
                for task in self._tasks:
                    if not task.done():
                        task.cancel()
                # Wait for tasks to finish
                if self._tasks:
                    await asyncio.gather(*self._tasks, return_exceptions=True)
                logger.info("Server shutdown complete")
                raise
            except Exception as e:
                logger.error(f"Server run error: {str(e)}")
                raise            
    async def _notify_completion(self, message: str):
        """Send a notification about task completion"""
        try:
            notification = notification(
                method="notifications/status",
                params={"message": message}
            )
            await self.server.send_notification(notification)
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            
def main():
    """Main entry point"""
    try:
        import argparse
        parser = argparse.ArgumentParser(description="MCP Windows Website Downloader")
        parser.add_argument("--library", type=str, default="website_library",
                           help="Directory for downloaded sites")
        args = parser.parse_args()
        
        # Get the absolute path, keeping relative paths relative to where the script is run
        if os.path.isabs(args.library):
            library_dir = Path(args.library)
        else:
            # Keep relative paths relative to current directory
            library_dir = Path.cwd() / args.library
            
        logger.info(f"Library directory: {library_dir}")
        
        server = WebsiteDownloaderServer(library_dir)
        logger.info("Server created")
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed: {str(e)}", exc_info=True)
        raise
        
if __name__ == "__main__":
    main()