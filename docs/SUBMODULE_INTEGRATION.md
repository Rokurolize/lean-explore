# Potion Problem Submodule Integration Guide

This guide explains how to integrate potion_problem as a git submodule for better code reference and analysis.

## Benefits of Submodule Integration

1. **Direct Code Access**: Sub-agents can analyze actual Lean 4 code and proof structures
2. **Version Synchronization**: Keep potion_problem code in sync with upstream
3. **Improved Analysis**: 
   - Analyze sorry patterns in context
   - Extract real usage examples
   - Validate API existence against actual code
4. **Development Efficiency**: No need to maintain separate workspace paths

## Setup Instructions

### 1. Add Submodule

```bash
# Option A: Use the provided script
bash scripts/add_submodule.sh

# Option B: Manual addition (replace with actual Git URL)
git submodule add https://github.com/[username]/potion_problem.git external/potion_problem
git submodule update --init --recursive
```

### 2. Update Configuration

Edit your `.env` file:
```bash
# Old path
POTION_PROBLEM_PATH=C:/Users/id374/workspace/potion_problem

# New path (relative to project root)
POTION_PROBLEM_PATH=./external/potion_problem
```

### 3. Verify Integration

```bash
# Check submodule status
git submodule status

# Test configuration
uv run python -c "from lean_explore.potion_problem.config import get_potion_config; print(get_potion_config())"
```

## Usage Examples

### For Sub-agents

Sub-agents can now directly analyze potion_problem code:

```python
# Example: Analyze sorry patterns in IrwinHallTheory.lean
from pathlib import Path

lean_file = Path("external/potion_problem/IrwinHallTheory.lean")
with open(lean_file, 'r', encoding='utf-8') as f:
    content = f.read()
    # Analyze sorry locations, contexts, etc.
```

### For MCP Tools

The MCP tools automatically use the submodule path:

```python
# The configuration will resolve to:
# workspace_path = Path("./external/potion_problem").resolve()
```

## Working with Submodules

### Update to Latest

```bash
cd external/potion_problem
git pull origin main
cd ../..
git add external/potion_problem
git commit -m "Update potion_problem submodule"
```

### Clone with Submodules

When cloning this repository:
```bash
git clone --recursive [this-repo-url]
# Or if already cloned:
git submodule update --init --recursive
```

## Troubleshooting

1. **Submodule not found**: Ensure you've run `git submodule update --init`
2. **Permission issues**: Check that the Git URL is accessible
3. **Path resolution**: Use absolute paths in .env if relative paths fail

## Advanced: Analyzing Code Patterns

With the submodule integrated, you can run advanced analysis:

```bash
# Find all sorry locations
uv run python scripts/analyze_sorries.py --source external/potion_problem

# Extract API usage patterns
uv run python scripts/extract_patterns.py --lean-file external/potion_problem/IrwinHallTheory.lean
```

This integration enables powerful code analysis capabilities while maintaining clean separation between the projects.