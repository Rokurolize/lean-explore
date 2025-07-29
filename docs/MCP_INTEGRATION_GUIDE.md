# LeanExplore MCP Integration Guide

## Overview

LeanExplore provides a **Model Context Protocol (MCP) server** that enables AI agents and applications to access Lean 4 mathematical data through standardized tools. This document provides comprehensive guidance for setting up, configuring, and using the MCP server.

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Available Tools](#available-tools)
- [Backend Types](#backend-types)
- [Integration Examples](#integration-examples)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## Quick Start

### Prerequisites

1. **Data Setup** (for local backend):
   ```bash
   uv run leanexplore data fetch
   ```

2. **Claude Code Integration**:
   Create `.mcp.json` in your project root:
   ```json
   {
     "mcpServers": {
       "lean-explore": {
         "command": "C:\\\\users\\\\id374\\\\.local\\\\bin\\\\uv.EXE",
         "args": [
           "run",
           "--project",
           "C:\\\\Users\\\\id374\\\\mcp-tools\\\\lean-explore",
           "python",
           "-m",
           "lean_explore.mcp.server",
           "--backend",
           "local"
         ],
         "env": {}
       }
     }
   }
   ```

3. **Verify Connection**:
   ```bash
   claude --debug
   # Check that lean-explore shows as "connected" in /mcp
   ```

## Architecture

### MCP Server Components

```
lean_explore/mcp/
├── app.py          # FastMCP application and lifespan management
├── server.py       # Main server entry point and CLI
└── tools.py        # MCP tool implementations
```

### Data Flow

```
Client (Claude Code)
    ↓ MCP Protocol
MCP Server (FastMCP)
    ↓ Backend Selection
Local Service OR API Client
    ↓ Data Access
SQLite + FAISS OR Remote API
```

## Installation

### Method 1: Claude Desktop (Recommended)

```bash
uv run mcp install src/lean_explore/mcp/server.py -v BACKEND=local -n lean-explore
```

### Method 2: Manual Configuration

Create appropriate `.mcp.json` configuration files as shown in the Quick Start section.

### Method 3: Direct Execution

```bash
uv run python -m lean_explore.mcp.server --backend local
```

## Configuration

### Command Line Options

```bash
python -m lean_explore.mcp.server [OPTIONS]

Options:
  --backend {api,local}    Backend type (required)
  --api-key TEXT          API key for remote backend
  --log-level TEXT        Logging level (DEBUG|INFO|WARNING|ERROR|CRITICAL)
```

### Environment Variables

- `BACKEND`: Backend type (local|api)
- `LEAN_EXPLORE_API_KEY`: API key for remote backend
- `MCP_TIMEOUT`: Server startup timeout in milliseconds

### Configuration Files

#### Windows (Claude Code)
```json
{
  "mcpServers": {
    "lean-explore": {
      "command": "C:\\\\users\\\\id374\\\\.local\\\\bin\\\\uv.EXE",
      "args": [
        "run",
        "--project", 
        "C:\\\\Users\\\\id374\\\\mcp-tools\\\\lean-explore",
        "python",
        "-m",
        "lean_explore.mcp.server",
        "--backend",
        "local"
      ],
      "env": {}
    }
  }
}
```

#### Cross-Platform (Generic)
```json
{
  "mcpServers": {
    "lean-explore": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/path/to/lean-explore",
        "python",
        "-m",
        "lean_explore.mcp.server",
        "--backend",
        "local"
      ],
      "env": {}
    }
  }
}
```

## Available Tools

### 1. search

**Purpose**: Search Lean statement groups by natural language queries

**Parameters**:
- `query` (required): String or list of search queries
- `package_filters` (optional): List of package names to filter results
- `limit` (optional, default=10): Maximum number of results

**Example Usage**:
```python
# Single query
result = await session.call_tool("search", {
    "query": "continuous function",
    "limit": 5
})

# Multiple queries with filters
result = await session.call_tool("search", {
    "query": ["ring definition", "group theory"],
    "package_filters": ["Mathlib.Algebra", "Mathlib.GroupTheory"],
    "limit": 10
})
```

**Response Format**:
```json
{
  "query": "continuous function",
  "packages_applied": ["Mathlib.Analysis"],
  "results": [
    {
      "id": 12345,
      "primary_declaration": {
        "lean_name": "Continuous"
      },
      "source_file": "Mathlib/Topology/Basic.lean",
      "range_start_line": 150,
      "statement_text": "def Continuous ...",
      "docstring": "A function is continuous if...",
      "informal_description": "Defines continuity for functions"
    }
  ],
  "count": 1,
  "total_candidates_considered": 50,
  "processing_time_ms": 125
}
```

### 2. get_by_id

**Purpose**: Retrieve specific statement groups by their unique identifiers

**Parameters**:
- `group_id` (required): Integer ID or list of IDs

**Example Usage**:
```python
# Single ID
result = await session.call_tool("get_by_id", {
    "group_id": 12345
})

# Multiple IDs
result = await session.call_tool("get_by_id", {
    "group_id": [12345, 67890, 11111]
})
```

### 3. get_dependencies

**Purpose**: Fetch direct dependencies (citations) for statement groups

**Parameters**:
- `group_id` (required): Integer ID or list of IDs

**Example Usage**:
```python
result = await session.call_tool("get_dependencies", {
    "group_id": 12345
})
```

**Response Format**:
```json
{
  "source_group_id": 12345,
  "citations": [
    {
      "id": 67890,
      "primary_declaration": {
        "lean_name": "TopologicalSpace"
      },
      "source_file": "Mathlib/Topology/Basic.lean",
      "statement_text": "class TopologicalSpace ..."
    }
  ],
  "count": 1
}
```

## Backend Types

### Local Backend

**Advantages**:
- ✅ Offline operation
- ✅ No API key required
- ✅ Full control over data
- ✅ Faster response times

**Requirements**:
- Local data toolchain: `uv run leanexplore data fetch`
- SQLite database (~3.5GB)
- FAISS index (~2.5GB)
- Sentence transformer models

**Data Location**:
```
~/.lean_explore/data/toolchains/0.2.0/
├── lean_explore_data.db     # SQLite database
├── main_faiss.index         # FAISS vector index
└── faiss_ids_map.json       # ID mapping
```

### API Backend

**Advantages**:
- ✅ No local storage required
- ✅ Always up-to-date data
- ✅ Reduced computational load

**Requirements**:
- LeanExplore API key
- Internet connection

**Configuration**:
```bash
python -m lean_explore.mcp.server --backend api --api-key YOUR_API_KEY
```

## Integration Examples

### Claude Code Integration

1. **Project-Scoped** (Recommended):
   ```bash
   # Create .mcp.json in project root
   claude mcp add lean-explore-local -s project ...
   ```

2. **User-Scoped** (Global):
   ```bash
   # Available across all projects
   claude mcp add lean-explore-global -s user ...
   ```

### Claude Desktop Integration

```json
{
  "mcpServers": {
    "lean-explore": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/path/to/lean-explore",
        "python",
        "-m",
        "lean_explore.mcp.server",
        "--backend",
        "local"
      ]
    }
  }
}
```

### Custom MCP Client

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "lean_explore.mcp.server", "--backend", "local"],
        env={"PYTHONPATH": "/path/to/lean-explore/src"}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Search for mathematical concepts
            result = await session.call_tool("search", {
                "query": "prime number",
                "limit": 3
            })
            
            print(f"Found {len(result.content)} results")

if __name__ == "__main__":
    asyncio.run(main())
```

## Troubleshooting

### Common Issues

#### 1. "Connection closed" Error

**Symptoms**:
```
[ERROR] MCP server "lean-explore" Server stderr: ModuleNotFoundError: No module named 'sentence_transformers'
```

**Solution**:
- Ensure correct virtual environment is used
- Install dependencies: `uv sync`
- Use absolute paths in configuration

#### 2. "Essential data files missing"

**Symptoms**:
```
Error: Essential data files for the local backend are missing.
```

**Solution**:
```bash
uv run leanexplore data fetch
```

#### 3. "Backend service not configured"

**Symptoms**:
```
RuntimeError: Backend service not configured or available for MCP tool.
```

**Solution**:
- Verify `--backend` parameter is specified
- Check API key for API backend
- Ensure data files exist for local backend

### Debug Mode

Enable detailed logging:
```bash
python -m lean_explore.mcp.server --backend local --log-level DEBUG
```

### Path Issues (Windows)

Use double-escaped backslashes in JSON:
```json
{
  "command": "C:\\\\users\\\\id374\\\\.local\\\\bin\\\\uv.EXE",
  "args": ["run", "--project", "C:\\\\Users\\\\id374\\\\mcp-tools\\\\lean-explore", ...]
}
```

## Development

### Server Architecture

```python
# app.py - FastMCP application
mcp_app = FastMCP(
    "LeanExploreMCPServer",
    version="0.1.0",
    lifespan=app_lifespan
)

# server.py - Entry point and backend initialization
def main():
    args = parse_arguments()
    
    if args.backend == "local":
        backend_service = LocalService()
    elif args.backend == "api":
        backend_service = APIClient(api_key=args.api_key)
    
    mcp_app._lean_explore_backend_service = backend_service
    mcp_app.run(transport="stdio")
```

### Adding New Tools

1. **Define Tool Function**:
   ```python
   @mcp_app.tool()
   async def new_tool(ctx: MCPContext, param: str) -> List[Dict[str, Any]]:
       backend = await _get_backend_from_context(ctx)
       result = backend.new_operation(param)
       return [result.model_dump(exclude_none=True)]
   ```

2. **Update Backend Services**:
   - Add method to `LocalService` class
   - Add method to `APIClient` class
   - Ensure consistent interface

3. **Add Tests**:
   ```python
   # tests/lean_explore/mcp/test_tools.py
   async def test_new_tool():
       # Test implementation
   ```

### Testing

```bash
# Run MCP-specific tests
uv run pytest tests/lean_explore/mcp/

# Test server startup
uv run python -m lean_explore.mcp.server --backend local --log-level DEBUG

# Test with MCP Inspector
uv run mcp dev src/lean_explore/mcp/server.py --backend local
```

## Performance Considerations

### Local Backend Optimization

- **Startup Time**: ~5-10 seconds for model loading
- **Memory Usage**: ~2-3GB for FAISS index and models
- **Query Response**: ~100-500ms depending on complexity

### Scaling Recommendations

- Use API backend for high-volume applications
- Consider caching for frequently accessed results
- Monitor memory usage with large result sets

## Security Notes

- Local backend has no external dependencies after data fetch
- API backend requires secure API key management
- MCP protocol uses stdio transport for secure communication
- No sensitive data is logged by default

## License

This MCP integration is part of the LeanExplore project and follows the same licensing terms.

## Contributing

1. Fork the repository
2. Create feature branch for MCP enhancements
3. Add tests for new functionality
4. Update this documentation
5. Submit pull request

For questions or issues, please create an issue in the LeanExplore repository with the "MCP" label.