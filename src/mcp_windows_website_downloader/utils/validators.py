"""URL and file validation utilities."""
import os
from typing import Optional
from urllib.parse import urlparse
import mimetypes
import re

def is_valid_url(url: str) -> bool:
    """Check if a URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def is_downloadable_url(url: str) -> bool:
    """Check if a URL points to downloadable content."""
    # List of allowed schemes
    ALLOWED_SCHEMES = {'http', 'https'}
    
    # List of excluded extensions
    EXCLUDED_EXTENSIONS = {
        '.exe', '.dll', '.bat', '.sh', '.app',
        '.dmg', '.pkg', '.deb', '.rpm', '.msi'
    }
    
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme.lower() not in ALLOWED_SCHEMES:
            return False
            
        # Check file extension
        ext = get_extension(url)
        if ext and ext.lower() in EXCLUDED_EXTENSIONS:
            return False
            
        return True
    except Exception:
        return False

def get_extension(url: str) -> Optional[str]:
    """Get the file extension from a URL."""
    parsed = urlparse(url)
    path = parsed.path
    
    # Try to get extension from path
    ext = os.path.splitext(path)[1]
    if ext:
        return ext
        
    # Try to guess from mimetype
    guessed_type = mimetypes.guess_type(url)[0]
    if guessed_type:
        return mimetypes.guess_extension(guessed_type)
        
    return None

def is_binary_content(content_type: str) -> bool:
    """Check if content type indicates binary data."""
    binary_types = {
        'image/', 'audio/', 'video/',
        'application/octet-stream',
        'application/pdf',
        'application/zip'
    }
    
    return any(btype in content_type.lower() for btype in binary_types)