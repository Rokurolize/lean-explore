# Potion Problem Integration for Lean-Explore MCP Server

This document describes the custom integration between lean-explore and the potion_problem project, providing enhanced API search and sorry elimination support.

## Overview

The potion_problem integration extends lean-explore with:

1. **API Database Integration**: Direct access to the curated Mathlib4 API database
2. **Sorry-Specific Search**: Find APIs that help eliminate specific sorries
3. **Error Pattern Recognition**: Learn from common API usage mistakes
4. **Hybrid Search**: Combines curated knowledge with comprehensive Lean-Explore search

## Features

### Custom MCP Tools

The integration adds several potion_problem-specific tools:

- **`check_api_exists`**: Quick verification of API existence
- **`get_api_usage`**: Retrieve usage patterns and examples
- **`search_by_sorry`**: Find APIs for specific sorry locations
- **`list_non_existent`**: Check patterns known not to exist
- **`get_error_patterns`**: Learn common mistakes and corrections
- **`api_database_stats`**: View database statistics

### Enhanced Search

The hybrid search system:
1. First searches the curated potion_problem API database
2. Optionally extends search using Lean-Explore's comprehensive index
3. Prioritizes APIs that help with sorry elimination
4. Includes deprecation warnings and replacement suggestions

## Installation

### Prerequisites

1. Python 3.8 or higher
2. The potion_problem repository cloned to `C:\Users\id374\workspace\potion_problem`
3. The API database initialized at `api_database\mathlib_apis.db`

### Setup Steps

1. **Install dependencies**:
   ```bash
   cd C:\Users\id374\mcp-tools\lean-explore
   pip install -e .
   ```

2. **Configure the integration**:
   - The default configuration is in `potion_problem_config.yml`
   - Adjust paths if your setup differs

3. **Optional: Download Lean-Explore data**:
   ```bash
   leanexplore data fetch
   ```
   This enables comprehensive search beyond the curated database.

## Usage

### Running the MCP Server

With potion_problem integration:
```bash
cd C:\Users\id374\mcp-tools\lean-explore
python -m lean_explore.mcp.server --backend local
```

### Using with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "lean-explore-potion": {
      "command": "python",
      "args": [
        "-m",
        "lean_explore.mcp.server",
        "--backend",
        "local"
      ],
      "cwd": "C:\\Users\\id374\\mcp-tools\\lean-explore",
      "env": {
        "PYTHONPATH": "C:\\Users\\id374\\mcp-tools\\lean-explore\\src"
      }
    }
  }
}
```

### Example Usage

1. **Check if an API exists**:
   ```
   Use check_api_exists with api_name="Summable.tsum_add"
   ```

2. **Find APIs for a sorry**:
   ```
   Use search_by_sorry with module="IrwinHallTheory" and sorry_line=173
   ```

3. **Get usage patterns**:
   ```
   Use get_api_usage with api_name="Summable.sum_add_tsum_nat_add"
   ```

## Database Schema

The integration uses the potion_problem API database with tables:
- `apis`: Core API information
- `usage_patterns`: Code examples
- `api_errors`: Common mistakes
- `sorry_contributions`: APIs that help with sorries
- `non_existent_apis`: Patterns that don't exist

## Customization

### Adding New APIs

Use the potion_problem tools:
```bash
cd C:\Users\id374\workspace\potion_problem
./api_database/api_tools.sh api-add "API.name" "signature" "import.path"
```

### Updating Sorry Contributions

After eliminating a sorry, record which APIs helped:
```sql
INSERT INTO sorry_contributions (api_name, module, sorry_line, contribution_level, notes)
VALUES ('API.name', 'ModuleName', line_number, 5, 'Critical for proof');
```

## Troubleshooting

### Database Connection Issues

If the API database cannot be found:
1. Verify the path in `potion_problem_config.yml`
2. Ensure the database file exists
3. Check file permissions

### Missing Lean-Explore Data

If comprehensive search is needed but not available:
```bash
leanexplore data fetch
```

### Import Errors

Ensure the PYTHONPATH includes the src directory:
```bash
export PYTHONPATH="C:\Users\id374\mcp-tools\lean-explore\src:$PYTHONPATH"
```

## Development

### Adding New Tools

1. Add tool functions to `src/lean_explore/potion_problem/tools.py`
2. Use the `@mcp_app.tool()` decorator
3. Access the hybrid service via `get_hybrid_service()`

### Extending the Backend

Modify `src/lean_explore/potion_problem/backend.py` to add new database queries or functionality.

## Future Enhancements

Planned improvements:
1. Automatic API discovery from build errors
2. Integration with Lean 4 language server
3. Real-time sorry tracking
4. API recommendation based on proof context