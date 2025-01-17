"""Core downloader functionality for the website downloader."""
import os
import asyncio
import logging
from typing import List, Dict, Optional
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from ..utils.validators import is_valid_url, is_downloadable_url
from ..utils.file_handlers import save_content, create_directory_structure

logger = logging.getLogger(__name__)

class WebsiteDownloader:
    def __init__(self, base_url: str, output_dir: str, max_depth: int = 2,
                 concurrent_downloads: int = 5, include_media: bool = True):
        """Initialize the website downloader."""
        self.base_url = base_url
        self.output_dir = output_dir
        self.max_depth = max_depth
        self.concurrent_downloads = concurrent_downloads
        self.include_media = include_media
        self.visited_urls = set()
        self.session = None
        self.semaphore = None

    async def __aenter__(self):
        """Set up async context."""
        self.session = aiohttp.ClientSession()
        self.semaphore = asyncio.Semaphore(self.concurrent_downloads)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up async context."""
        if self.session:
            await self.session.close()

    async def download_page(self, url: str, depth: int = 0) -> Optional[str]:
        """Download a single page and its assets."""
        if not is_valid_url(url) or url in self.visited_urls or depth > self.max_depth:
            return None

        self.visited_urls.add(url)
        
        try:
            async with self.semaphore:
                async with self.session.get(url) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to download {url}: {response.status}")
                        return None
                    
                    content = await response.text()
                    
                    # Parse and process content
                    soup = BeautifulSoup(content, 'html.parser')
                    await self._process_assets(soup, url)
                    
                    # Save the modified content
                    relative_path = urlparse(url).path.lstrip('/')
                    save_path = os.path.join(self.output_dir, relative_path)
                    save_content(save_path, str(soup))
                    
                    return content
        except Exception as e:
            logger.error(f"Error downloading {url}: {str(e)}")
            return None

    async def _process_assets(self, soup: BeautifulSoup, base_url: str):
        """Process and download page assets."""
        tasks = []
        
        # Process images
        if self.include_media:
            for img in soup.find_all('img'):
                src = img.get('src')
                if src:
                    absolute_url = urljoin(base_url, src)
                    if is_downloadable_url(absolute_url):
                        tasks.append(self._download_asset(absolute_url))
        
        # Process stylesheets
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                if is_downloadable_url(absolute_url):
                    tasks.append(self._download_asset(absolute_url))
        
        # Process scripts
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                absolute_url = urljoin(base_url, src)
                if is_downloadable_url(absolute_url):
                    tasks.append(self._download_asset(absolute_url))
        
        if tasks:
            await asyncio.gather(*tasks)

    async def _download_asset(self, url: str):
        """Download an asset file."""
        try:
            async with self.semaphore:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        relative_path = urlparse(url).path.lstrip('/')
                        save_path = os.path.join(self.output_dir, 'assets', relative_path)
                        save_content(save_path, content, binary=True)
        except Exception as e:
            logger.error(f"Error downloading asset {url}: {str(e)}")

    async def start(self):
        """Start the download process."""
        logger.info(f"Starting download of {self.base_url}")
        create_directory_structure(self.output_dir)
        await self.download_page(self.base_url)