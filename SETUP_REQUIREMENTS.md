# Setup Requirements

## Environment Setup

### 1. Directory Structure
```
C:\Users\id374\
├── mcp-tools\
│   └── lean-explore-potionassist\    # This repository (after rename)
└── workspace\
    └── potion_problem\                # Target project
        └── api_database\
            └── mathlib_apis.db        # Required API database
```

### 2. Required Software
- Python 3.12+
- uv (package manager)
- Git
- SQLite3 (for database access)

### 3. Installation Steps

```bash
# 1. Clone and setup this repository
git clone <repository-url> lean-explore-potionassist
cd lean-explore-potionassist

# 2. Install dependencies
uv sync

# 3. (Optional) Download LeanExplore data for full search
uv run leanexplore data fetch

# 4. Verify installation
uv run python -c "from lean_explore.potion_problem.backend import PotionProblemBackend; print('✓ Import successful')"
```

### 4. Environment Variables

No environment variables are strictly required, but you may set:

```bash
# Optional: Override potion_problem location
export POTION_PROBLEM_PATH="C:/Users/id374/workspace/potion_problem"

# Optional: Python path (usually handled by uv)
export PYTHONPATH="C:/Users/id374/mcp-tools/lean-explore-potionassist/src:$PYTHONPATH"
```

### 5. MCP Server Configuration

For Claude Code integration, add to `.mcp.json`:

```json
{
  "mcpServers": {
    "lean-explore-potion": {
      "command": "C:\\\\users\\\\id374\\\\.local\\\\bin\\\\uv.EXE",
      "args": [
        "run",
        "--project",
        "C:\\\\Users\\\\id374\\\\mcp-tools\\\\lean-explore-potionassist",
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

### 6. Verification

Run these commands to verify setup:

```bash
# Check API database connection
uv run python -c "
from lean_explore.potion_problem.backend import PotionProblemBackend, PotionProblemConfig
from pathlib import Path
config = PotionProblemConfig(
    api_database_path=Path('C:/Users/id374/workspace/potion_problem/api_database/mathlib_apis.db'),
    workspace_path=Path('C:/Users/id374/workspace/potion_problem')
)
backend = PotionProblemBackend(config)
print('✓ Database connected')
"

# Test MCP server
uv run python -m lean_explore.mcp.server --backend local --log-level DEBUG
# (Press Ctrl+C to exit)

# Run auto-solver
uv run python run_auto_solver.py
```

## Troubleshooting

### "Database not found" Error
1. Ensure potion_problem repository is cloned to the correct location
2. Check that `mathlib_apis.db` exists in `api_database/` directory
3. Verify file permissions

### "Module not found" Error
1. Ensure `uv sync` completed successfully
2. Check that you're in the correct directory
3. Try `uv run` prefix for all Python commands

### MCP Connection Issues
1. Verify `.mcp.json` paths use double backslashes on Windows
2. Check that uv.exe path is correct
3. Look at Claude Code debug logs for detailed errors

## Data Requirements

### Required Files
- **API Database**: `potion_problem/api_database/mathlib_apis.db` (required)
- **LeanExplore Data**: `~/.lean_explore/data/toolchains/0.2.0/` (optional, for full search)

### Database Schema
The API database must contain these tables:
- `apis`: Core API information
- `usage_patterns`: Code examples
- `api_errors`: Common mistakes
- `sorry_contributions`: APIs that help with sorries
- `non_existent_apis`: Patterns that don't exist

## Next Steps

After setup:
1. Test the auto-solver on remaining sorries
2. Use MCP tools through Claude Code
3. Monitor `KNOWN_ISSUES.md` for areas needing improvement
4. Contribute improvements back to the project