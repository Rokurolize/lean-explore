# Quick Start Guide: Potion Problem + Lean-Explore Integration

## Overview

This integration combines:
- **Potion Problem's curated API database** (81 APIs with usage patterns and error examples)
- **Lean-Explore's MCP server** for Claude Desktop integration
- **Custom tools** specifically for sorry elimination

## Installation Complete! ✅

The following has been set up:
1. ✅ lean-explore repository cloned to `C:\Users\id374\mcp-tools\lean-explore`
2. ✅ Virtual environment created with `uv`
3. ✅ All dependencies installed
4. ✅ Custom backend integrated with potion_problem database
5. ✅ Custom MCP tools implemented
6. ✅ Integration tests passing

## Testing the MCP Server

### Local Backend (Recommended)
Uses your potion_problem API database:
```bash
cd C:\Users\id374\mcp-tools\lean-explore
.venv\Scripts\python -m lean_explore.mcp.server --backend local
```

### API Backend
Uses the remote Lean-Explore API:
```bash
cd C:\Users\id374\mcp-tools\lean-explore
.venv\Scripts\python -m lean_explore.mcp.server --backend api --api-key JeNgKAjzDtOMAexvdXCY6Utrgh6RYEOPUnQBSDxV5VI
```

## Claude Desktop Integration

1. **Find your Claude Desktop config file**:
   - Windows: `%APPDATA%\Claude\config.json`
   - Usually: `C:\Users\id374\AppData\Roaming\Claude\config.json`

2. **Add the MCP server configuration**:
   ```json
   {
     "mcpServers": {
       "lean-explore-potion": {
         "command": "C:\\Users\\id374\\mcp-tools\\lean-explore\\.venv\\Scripts\\python.exe",
         "args": [
           "-m",
           "lean_explore.mcp.server",
           "--backend",
           "local"
         ],
         "cwd": "C:\\Users\\id374\\mcp-tools\\lean-explore"
       }
     }
   }
   ```

3. **Restart Claude Desktop**

## Available Tools in Claude

Once integrated, you can use these tools:

### Standard Lean-Explore Tools
- **`search`**: Search for Lean 4 declarations
  - Example: `search query="Summable" limit=10`

### Potion Problem Custom Tools
- **`check_api_exists`**: Quick check if an API exists
  - Example: `check_api_exists api_name="Summable.tsum_add"`

- **`get_api_usage`**: Get usage patterns and error examples
  - Example: `get_api_usage api_name="Summable.sum_add_tsum_nat_add"`

- **`search_by_sorry`**: Find APIs for specific sorries
  - Example: `search_by_sorry module="IrwinHallTheory" sorry_line=173`

- **`list_non_existent`**: Check patterns known not to exist
  - Example: `list_non_existent search_context="conditional sum"`

- **`get_error_patterns`**: Get common mistakes for an API
  - Example: `get_error_patterns api_name="Summable.sum_add_tsum_nat_add"`

- **`api_database_stats`**: View database statistics
  - Example: `api_database_stats`

## Usage Example in Claude

After integration, in Claude Desktop you can:

```
Use the search_by_sorry tool to find APIs that help with line 233 in IrwinHallTheory
```

Claude will use the MCP server to query your database and return relevant APIs.

## Troubleshooting

### If MCP server doesn't start:
1. Check Python path is correct in config
2. Ensure virtual environment is intact
3. Check logs: `--log-level DEBUG`

### If tools aren't available in Claude:
1. Ensure Claude Desktop is fully restarted
2. Check config.json syntax (proper escaping of backslashes)
3. Look for errors in Claude's developer console

## Next Steps

1. **Optional**: Download full Lean-Explore data for comprehensive search:
   ```bash
   cd C:\Users\id374\mcp-tools\lean-explore
   .venv\Scripts\leanexplore data fetch
   ```

2. **Extend the database**: As you eliminate sorries, add successful APIs:
   ```bash
   cd C:\Users\id374\workspace\potion_problem
   ./api_database/api_tools.sh api-add "New.API" "signature" "import.path"
   ```

3. **Contribute back**: Push your customizations to your fork:
   ```bash
   cd C:\Users\id374\mcp-tools\lean-explore
   git add -A
   git commit -m "Add potion_problem integration"
   git push origin main
   ```

## Summary

You now have a powerful integration that combines:
- 81 curated APIs with detailed metadata
- Usage patterns and error examples
- Sorry-specific search capabilities
- Direct integration with Claude Desktop
- Extensible framework for adding more APIs

Happy sorry hunting! 🎯