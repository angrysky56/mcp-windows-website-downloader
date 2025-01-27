"""
Utility functions for website downloader.
"""
import re
from pathlib import Path

def clean_filename(filename: str) -> str:
    """
    Convert URL or path to safe filename
    
    Args:
        filename: URL or path to clean
        
    Returns:
        Clean filename safe for filesystem
    """
    # Remove query parameters and fragments
    filename = filename.split("?")[0].split("#")[0]
    
    # Replace unsafe characters
    unsafe = '<>:"\\/|?*'
    filename = "".join(c if c not in unsafe else "_" for c in filename)
    
    # Clean up multiple underscores
    filename = re.sub(r"_+", "_", filename)
    
    return filename.strip("_")