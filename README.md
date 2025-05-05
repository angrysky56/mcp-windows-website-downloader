[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/angrysky56-mcp-windows-website-downloader-badge.png)](https://mseep.ai/app/angrysky56-mcp-windows-website-downloader)

# MCP Website Downloader

Simple MCP server for downloading documentation websites and preparing them for RAG indexing.

## Features

- Downloads complete documentation sites, well big chunks anyway.
- Maintains link structure and navigation, not really. lol
- Downloads and organizes assets (CSS, JS, images), but isn't really AI friendly and it all probably needs some kind of parsing or vectorizing into a db or something.
- Creates clean index for RAG systems, currently seems to make an index in each folder, not even looked at it.
- Simple single-purpose MCP interface, yup.

## Installation

Fork and download, cd to the repository.
```bash
uv venv
./venv/Scripts/activate
pip install -e .
```

Put this in your claude_desktop_config.json with your own paths:

```json
   "mcp-windows-website-downloader": {
     "command": "uv",
     "args": [
       "--directory",
       "F:/GithubRepos/mcp-windows-website-downloader",
       "run",
       "mcp-windows-website-downloader",
       "--library",
       "F:/GithubRepos/mcp-windows-website-downloader/website_library"
     ]
   },
```

![alt text]({52E8102D-678C-44FE-9B0E-491483808EB6}.png)

## Other Usage you don't need to worry about and may be hallucinatory lol:

1. Start the server:
```bash
python -m mcp_windows_website_downloader.server --library docs_library
```

2. Use through Claude Desktop or other MCP clients:
```python
result = await server.call_tool("download", {
    "url": "https://docs.example.com"
})
```

## Output Structure

```
docs_library/
  domain_name/
    index.html
    about.html
    docs/
      getting-started.html
      ...
    assets/
      css/
      js/
      images/
      fonts/
    rag_index.json
```

## Development

The server follows standard MCP architecture:

```
src/
  mcp_windows_website_downloader/
    __init__.py
    server.py    # MCP server implementation
    core.py      # Core downloader functionality
    utils.py     # Helper utilities
```

### Components

- `server.py`: Main MCP server implementation that handles tool registration and requests
- `core.py`: Core website downloading functionality with proper asset handling
- `utils.py`: Helper utilities for file handling and URL processing

### Design Principles

1. Single Responsibility
   - Each module has one clear purpose
   - Server handles MCP interface
   - Core handles downloading
   - Utils handles common operations

2. Clean Structure
   - Maintains original site structure
   - Organizes assets by type
   - Creates clear index for RAG systems

3. Robust Operation
   - Proper error handling
   - Reasonable depth limits
   - Asset download verification
   - Clean URL/path processing

### RAG Index

The `rag_index.json` file contains:
```json
{
  "url": "https://docs.example.com",
  "domain": "docs.example.com", 
  "pages": 42,
  "path": "/path/to/site"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file

## Error Handling

The server handles common issues:

- Invalid URLs
- Network errors
- Asset download failures  
- Malformed HTML
- Deep recursion
- File system errors

Error responses follow the format:
```json
{
  "status": "error",
  "error": "Detailed error message"
}
```

Success responses:
```json
{
  "status": "success",
  "path": "/path/to/downloaded/site",
  "pages": 42
}
```