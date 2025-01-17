"""File handling utilities for the website downloader."""
import os
import logging
from typing import Union
from pathlib import Path

logger = logging.getLogger(__name__)

def create_directory_structure(base_dir: str) -> None:
    """Create the necessary directory structure for downloaded content."""
    try:
        # Create main directory
        os.makedirs(base_dir, exist_ok=True)
        
        # Create subdirectories for different content types
        subdirs = ['assets', 'images', 'scripts', 'styles']
        for subdir in subdirs:
            os.makedirs(os.path.join(base_dir, subdir), exist_ok=True)
            
        logger.info(f"Created directory structure in {base_dir}")
    except Exception as e:
        logger.error(f"Error creating directory structure: {str(e)}")
        raise

def save_content(filepath: str, content: Union[str, bytes], binary: bool = False) -> None:
    """Save content to a file, creating directories as needed."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save the content
        mode = 'wb' if binary else 'w'
        encoding = None if binary else 'utf-8'
        
        with open(filepath, mode, encoding=encoding) as f:
            f.write(content)
            
        logger.debug(f"Saved content to {filepath}")
    except Exception as e:
        logger.error(f"Error saving content to {filepath}: {str(e)}")
        raise

def get_unique_filename(filepath: str) -> str:
    """Generate a unique filename by appending a number if the file exists."""
    if not os.path.exists(filepath):
        return filepath
        
    path = Path(filepath)
    directory = path.parent
    filename = path.stem
    extension = path.suffix
    counter = 1
    
    while True:
        new_filepath = os.path.join(directory, f"{filename}_{counter}{extension}")
        if not os.path.exists(new_filepath):
            return new_filepath
        counter += 1

def clean_filename(filename: str) -> str:
    """Clean a filename by removing invalid characters."""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Ensure filename is not too long
    max_length = 255
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length-len(ext)] + ext
    
    return filename