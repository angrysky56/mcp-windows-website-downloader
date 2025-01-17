# MCP Windows Website Downloader

A Windows-compatible website downloader tool for the Model Context Protocol (MCP). Downloads websites and their assets with configurable depth and concurrent download settings.

![alt text](image-1.png)

## Features

- Asynchronous downloading
- Configurable crawl depth
- Concurrent downloading
- Media file handling
- Windows path handling

## Installation

Clone repository, cd into it, and install dependencies:

```python
uv venv
.venv/Scripts/activate
uv pip install -e .
```

## Usage

Just ask Claude to use the windows-website-downloader to grab a website you want, done instantly.

Tool is accessed through MCP with the following configuration:
Downloads default to downloads folder in the MCP root. My working Claude app JSON, change directory path to yours.
```json
{
    "mcpServers": {
        "mcp-windows-website-downloader": {
            "command": "uv",
            "args": [
                "--directory", 
                "F:/GithubRepos/mcp-windows-website-downloader",
                "run",
                "mcp-windows-website-downloader"
            ]
        }
    }
}
```