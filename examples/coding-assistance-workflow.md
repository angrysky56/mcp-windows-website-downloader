# Comprehensive Coding Assistance Workflow

## Documentation Access and Search Capabilities

### Primary Documentation Search

1. **Brave Search** (`brave_web_search`)
   - Searches across all developer documentation and resources
   - Good for finding relevant documentation, tutorials, and examples
   - Can search for specific error messages or coding patterns
   - Example:

   ```javascript
   brave_web_search({
     query: "mdn javascript array methods documentation",
     count: 3
   })
   ```

### Direct Documentation Access

2. **cURL Requests** (`curl`)
   - Fetch specific documentation pages directly
   - Access raw content from documentation sites
   - Useful for getting detailed API references
   - Example:

   ```javascript
   curl({
     url: "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array",
     method: "GET"
   })
   ```

### Website Downloads

3. **Website Downloader** (`download-website`)
   - Download entire websites
   - Download complete documentation sites for reference
   - Includes assets and related resources
   - Example:

   ```javascript

   download-website({
     url: "https://devdocs.io/",
     include_assets: true
   })
   ```

## Code Analysis and Execution

### JavaScript Analysis

1. **REPL Environment** (`repl`)
   - Execute JavaScript code in real-time
   - Test code snippets and algorithms
   - Access to key libraries:
     - lodash for utility functions
     - papaparse for CSV processing
     - mathjs for mathematical operations
     - sheetjs for Excel file handling

### File Operations

2. **File System Operations**
   - Read files: `window.fs.readFile`
   - Process various file formats
   - Handle uploads and file content

### Database Operations

3. **SQLite Integration**
   - `read_query`: Execute SELECT queries
   - `write_query`: Execute INSERT/UPDATE/DELETE queries
   - `create_table`: Create new tables
   - `list_tables`: View available tables
   - `describe_table`: Get table schema information

## Visualization and Display

### React Components

1. **Interactive Components** (`application/vnd.ant.react`)
   - Create data visualizations
   - Build interactive interfaces
   - Available libraries:
     - Recharts for charts
     - Lucide React for icons
     - Tailwind CSS for styling
     - shadcn/ui components

### SVG Graphics

2. **Vector Graphics** (`image/svg+xml`)
   - Create custom graphics and diagrams
   - Generate visual assets

### Mermaid Diagrams

3. **Technical Diagrams** (`application/vnd.ant.mermaid`)
   - Create flowcharts
   - Generate sequence diagrams
   - Visualize architecture

## Best Practices for Usage

1. **Documentation Flow**
   - Start with Brave Search to find relevant documentation
   - Use cURL to fetch specific details
   - Download complete sites when needed for comprehensive reference

2. **Code Development Flow**
   - Use REPL for initial code testing and development
   - Create artifacts for finalized code and visualizations
   - Leverage SQL database for data persistence and querying

3. **Visualization Flow**
   - Use React components for interactive visualizations
   - Generate SVG for static graphics
   - Create Mermaid diagrams for technical documentation

## Error Handling and Debugging

1. **Documentation Verification**
   - Cross-reference multiple sources
   - Verify current best practices
   - Check browser compatibility

2. **Code Testing**
   - Use REPL for immediate feedback
   - Test edge cases and error conditions
   - Validate output and performance

3. **Resource Management**
   - Monitor memory usage in REPL
   - Handle large files appropriately
   - Optimize database queries

## Additional Resources

### Knowledge Graph

- Create entities: `create_entities`
- Create relations: `create_relations`
- Search nodes: `search_nodes`
- Read graph: `read_graph`

### File Analysis

- Get file info: `get_file_info`
- Search files: `search_files`
- List directories: `list_directory`

### Mathematical Tools

- Wolfram Alpha integration: `query-wolfram-alpha`
- Complex calculations and symbolic math

This workflow provides a comprehensive approach to code assistance, documentation, and development support, leveraging available tools and resources efficiently.

Resources:

<https://github.com/punkpeye/awesome-mcp-servers>
