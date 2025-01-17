"""
Content Processor Module
Handles processing and transformation of downloaded content.

This module provides functionality to:
- Parse HTML content
- Extract and process resources (CSS, JS, images)
- Transform URLs to local paths
- Optimize content for local storage
"""

import asyncio
from pathlib import Path
from typing import Set, Dict, List
from bs4 import BeautifulSoup
import logging
import re
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class ContentProcessor:
    """Processes downloaded website content"""
    
    def __init__(self, base_url: str, save_path: Path):
        self.base_url = base_url
        self.save_path = save_path
        self.processed_urls: Set[str] = set()
        self.resource_map: Dict[str, str] = {}
        
    def process_html(self, content: str, url: str) -> tuple[str, List[str]]:
        """
        Process HTML content and extract resources
        
        Args:
            content: HTML content string
            url: Source URL of the content
            
        Returns:
            Tuple of (processed_html, resource_urls)
        """
        soup = BeautifulSoup(content, 'html.parser')
        resources = []
        
        # Process various resource types
        resources.extend(self._process_links(soup))
        resources.extend(self._process_scripts(soup))
        resources.extend(self._process_images(soup))
        resources.extend(self._process_styles(soup))
        
        return str(soup), list(set(resources))
        
    def _process_links(self, soup: BeautifulSoup) -> List[str]:
        """Process link tags for CSS and other resources"""
        resources = []
        for link in soup.find_all('link', href=True):
            href = link['href']
            absolute_url = urljoin(self.base_url, href)
            if self._should_download_resource(absolute_url):
                resources.append(absolute_url)
                link['href'] = self._get_local_path(absolute_url)
        return resources
        
    def _process_scripts(self, soup: BeautifulSoup) -> List[str]:
        """Process script tags"""
        resources = []
        for script in soup.find_all('script', src=True):
            src = script['src']
            absolute_url = urljoin(self.base_url, src)
            if self._should_download_resource(absolute_url):
                resources.append(absolute_url)
                script['src'] = self._get_local_path(absolute_url)
        return resources
        
    def _process_images(self, soup: BeautifulSoup) -> List[str]:
        """Process image tags"""
        resources = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            absolute_url = urljoin(self.base_url, src)
            if self._should_download_resource(absolute_url):
                resources.append(absolute_url)
                img['src'] = self._get_local_path(absolute_url)
        return resources
        
    def _process_styles(self, soup: BeautifulSoup) -> List[str]:
        """Process style tags and CSS content"""
        resources = []
        for style in soup.find_all('style'):
            urls = re.findall(r'url\([\'"]?([^\'"())]+)[\'"]?\)', style.string or '')
            for url in urls:
                absolute_url = urljoin(self.base_url, url)
                if self._should_download_resource(absolute_url):
                    resources.append(absolute_url)
                    style.string = style.string.replace(
                        url,
                        self._get_local_path(absolute_url)
                    )
        return resources
        
    def _should_download_resource(self, url: str) -> bool:
        """Determine if resource should be downloaded"""
        if url in self.processed_urls:
            return False
            
        parsed = urlparse(url)
        return (
            parsed.scheme in ('http', 'https') and
            not any(ext in url for ext in ['.php', '.asp', '.jsp']) and
            not any(pattern in url for pattern in ['?', '#'])
        )
        
    def _get_local_path(self, url: str) -> str:
        """Generate local path for resource"""
        parsed = urlparse(url)
        path = parsed.path.lstrip('/')
        if not path:
            path = 'index.html'
        return str(Path('resources') / path)

    def process_css(self, content: str, url: str) -> tuple[str, List[str]]:
        """Process CSS content and extract referenced resources"""
        resources = []
        urls = re.findall(r'url\([\'"]?([^\'"())]+)[\'"]?\)', content)
        
        for resource_url in urls:
            absolute_url = urljoin(url, resource_url)
            if self._should_download_resource(absolute_url):
                resources.append(absolute_url)
                local_path = self._get_local_path(absolute_url)
                content = content.replace(resource_url, local_path)
                
        return content, resources
