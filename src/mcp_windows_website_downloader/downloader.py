"""
Core website downloading functionality.
"""
import logging
import asyncio
from pathlib import Path
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
import json
import re
from typing import Dict, Any, Optional, Set
from .utils import clean_filename

logger = logging.getLogger(__name__)

class WebsiteDownloader:
    """Downloads and processes documentation websites"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        logger.info(f"Downloader initialized with output directory: {self.output_dir}")
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True)
            logger.info(f"Created output directory at {self.output_dir}")
        self.visited_urls = set()
        self.current_domain = None
        self.site_dir = None
        self.max_depth = 2  # Default, will be adjusted based on site analysis

    async def _analyze_site_structure(self, session: aiohttp.ClientSession, url: str) -> int:
        """
        Analyze the site structure to determine appropriate crawl depth.
        Returns recommended max depth.
        """
        try:
            logger.info("Analyzing site structure...")
            async with session.get(url) as response:
                if response.status != 200:
                    return self.max_depth
                    
                content = await response.text()
                soup = BeautifulSoup(content, "html.parser")
                
                # Look for common documentation patterns
                nav_elements = soup.find_all(['nav', 'sidebar', 'menu', 'toc'])
                has_nav = len(nav_elements) > 0
                
                # Check URL patterns
                path = urlparse(url).path
                is_docs_url = any(x in path.lower() for x in ['/docs/', '/documentation/', '/guide/', '/tutorial/'])
                
                # Check for documentation frameworks
                is_sphinx = bool(soup.find('div', {'class': 'sphinxsidebar'}))
                is_mkdocs = bool(soup.find('nav', {'class': 'md-nav'}))
                is_docusaurus = bool(soup.find('nav', {'class': 'menu'}))
                
                # Analyze link structure
                links = set()
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if not href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                        full_url = urljoin(url, href)
                        if urlparse(full_url).netloc == self.current_domain:
                            links.add(full_url)
                
                # Determine appropriate depth
                if is_sphinx or is_mkdocs or is_docusaurus:
                    # Known documentation sites usually need more depth
                    depth = 4
                elif is_docs_url and has_nav:
                    # Looks like structured documentation
                    depth = 3
                elif len(links) > 100:
                    # Large site, be conservative
                    depth = 2
                else:
                    # Small or unknown site structure
                    depth = 2
                    
                logger.info(f"Site analysis complete. Recommended depth: {depth}")
                return depth
                
        except Exception as e:
            logger.warning(f"Site analysis failed: {str(e)}")
            return self.max_depth

    async def download(self, url: str) -> Dict[str, Any]:
        """Download a documentation website"""
        try:
            # Reset state
            self.visited_urls.clear()
            self.current_domain = urlparse(url).netloc
            
            # Ensure we're using the configured output directory
            logger.info(f"Using output directory: {self.output_dir}")
            
            # Create site directory inside the output directory
            self.site_dir = self.output_dir / clean_filename(self.current_domain)
            logger.info(f"Creating site directory at: {self.site_dir}")
            self.site_dir.mkdir(exist_ok=True)
            
            logger.info(f"Starting download of {url} to {self.site_dir}")
            
            # Create clean directory structure
            assets_dir = self.site_dir / "assets"
            assets_dir.mkdir(exist_ok=True)
            for dir_name in ["css", "js", "images", "fonts", "other"]:
                (assets_dir / dir_name).mkdir(exist_ok=True)

            # Configure session            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }
            
            async with aiohttp.ClientSession(headers=headers) as session:
                # Analyze site and set depth
                self.max_depth = await self._analyze_site_structure(session, url)
                logger.info(f"Using max depth of {self.max_depth} for this site")
                
                # Start download
                await self._process_page(session, url)
                
            # Create index
            index = {
                "url": url,
                "domain": self.current_domain,
                "pages": len(self.visited_urls),
                "path": str(self.site_dir),
                "max_depth_used": self.max_depth
            }
            
            index_path = self.site_dir / "rag_index.json"
            with open(index_path, "w") as f:
                json.dump(index, f, indent=2)
            
            logger.info(f"Download complete. {len(self.visited_urls)} pages saved to {self.site_dir}")
            
            return {
                "status": "success",
                "path": str(self.site_dir),
                "pages": len(self.visited_urls),
                "depth_used": self.max_depth
            }
            
        except asyncio.CancelledError:
            logger.info("Download cancelled")
            raise
        except Exception as e:
            logger.error(f"Download failed: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }

    async def _process_page(self, session: aiohttp.ClientSession, url: str, depth: int = 0) -> Optional[str]:
        """Process a single page and its assets"""
        if url in self.visited_urls or depth > self.max_depth:
            return None
            
        self.visited_urls.add(url)
        logger.info(f"Processing {url} (depth {depth}/{self.max_depth})")
        
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to get {url}: {response.status}")
                    return None
                    
                content = await response.text()
                soup = BeautifulSoup(content, "html.parser")
                
                # Save processed page first
                save_path = self._get_save_path(url)
                if not save_path:
                    logger.warning(f"Invalid save path for {url}")
                    return None
                    
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Handle assets before saving page
                await self._handle_assets(session, soup, url)
                
                # Process internal links
                await self._process_links(session, soup, url, depth)
                
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(str(soup))
                    
                return str(save_path.relative_to(self.site_dir))
                
        except Exception as e:
            logger.warning(f"Error processing {url}: {str(e)}")
            return None

    async def _handle_assets(self, session: aiohttp.ClientSession, soup: BeautifulSoup, base_url: str):
        """Download and update page assets"""
        for tag, attr in [("link", "href"), ("script", "src"), ("img", "src")]:
            for elem in soup.find_all(tag, {attr: True}):
                src = elem[attr]
                if src.startswith(("data:", "blob:", "javascript:", "#", "mailto:")):
                    continue
                    
                try:
                    full_url = urljoin(base_url, src)
                    if urlparse(full_url).netloc != self.current_domain:
                        continue
                        
                    async with session.get(full_url) as response:
                        if response.status == 200:
                            content = await response.read()
                            save_path = self._save_asset(full_url, content)
                            if save_path:
                                elem[attr] = str(save_path)
                except Exception as e:
                    logger.warning(f"Asset error ({src}): {str(e)}")

    async def _process_links(self, session: aiohttp.ClientSession, soup: BeautifulSoup, url: str, depth: int):
        """Process and update page links"""
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
                
            try:
                full_url = urljoin(url, href)
                if urlparse(full_url).netloc == self.current_domain:
                    if new_path := await self._process_page(session, full_url, depth + 1):
                        a["href"] = f"/{new_path}"
            except Exception as e:
                logger.warning(f"Link error ({href}): {str(e)}")

    def _save_asset(self, url: str, content: bytes) -> Optional[Path]:
        """Save an asset file"""
        try:
            # Get clean filename from URL
            path = urlparse(url).path.lstrip("/")
            if not path:
                return None
                
            filename = clean_filename(unquote(path))
            
            # Determine asset type and directory
            if url.endswith((".css", ".scss")):
                asset_dir = "css"
            elif url.endswith((".js", ".mjs")):
                asset_dir = "js"
            elif url.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")):
                asset_dir = "images"
            elif url.endswith((".woff", ".woff2", ".ttf", ".eot")):
                asset_dir = "fonts"
            else:
                asset_dir = "other"
                
            # Create relative asset path ensuring it's under the configured directory
            rel_path = Path("assets") / asset_dir / filename
            full_path = self.site_dir / rel_path
            
            # Ensure we're not trying to write outside the site directory
            if not str(full_path).startswith(str(self.site_dir)):
                logger.warning(f"Attempted to write asset outside site directory: {full_path}")
                return None
            
            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            with open(full_path, "wb") as f:
                f.write(content)
                
            return rel_path
            
        except Exception as e:
            logger.warning(f"Failed to save asset {url}: {str(e)}")
            return None

    def _get_save_path(self, url: str) -> Optional[Path]:
        """Get file system path for saving page"""
        try:
            # Get clean path from URL
            path = urlparse(url).path.lstrip("/")
            if not path:
                path = "index.html"
            elif not path.endswith((".html", ".htm")):
                path = f"{path}.html"
                
            # Clean the path and create Path object
            clean_path = clean_filename(unquote(path))
            save_path = self.site_dir / clean_path
            # user is able to save wherever they write in their app json- this is unneeded:
            # Safety check - ensure we're not trying to write outside site directory
            if not str(save_path).startswith(str(self.site_dir)):
                logger.warning(f"Attempted to save page outside site directory: {save_path}")
                return None
                
            return save_path
            
        except Exception as e:
            logger.warning(f"Invalid save path for {url}: {str(e)}")
            return None