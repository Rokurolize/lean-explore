# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a specialized fork of LeanExplore customized for the **Potion Problem (媚薬問題)** formal verification project. The primary mission is to prevent hallucination of non-existent Mathlib APIs while providing accurate, real-time assistance for formal proof development in Lean 4.

### Key Goals
1. **Hallucination Prevention**: Verify API existence against curated database
2. **Efficient API Search**: Find optimal APIs for sorry elimination  
3. **Real-time MCP Support**: Assist potion_problem development via Model Context Protocol

## Architecture

### Core Components

**PotionProblemBackend** (`src/lean_explore/potion_problem/backend.py`)
- Integrates with potion_problem's API database (`external/potion_problem/api_database/mathlib_apis.db`)
- Validates API existence and tracks usage patterns
- Ranks APIs by sorry contribution scores

**EnhancedHybridService** (`src/lean_explore/potion_problem/enhanced_service.py`)
- Parallel search across 600k+ LeanExplore declarations and curated Potion DB
- True API discovery with confidence scoring
- Error pattern learning capabilities

**SorryAutoSolver** (`src/lean_explore/potion_problem/auto_solver.py`)
- Automated sorry analysis with context extraction
- Pattern matching from successful eliminations
- Depth-first search with pruning heuristics

**MCP Optimization** (`src/lean_explore/mcp/optimization.py`)
- Token-efficient output format (70% reduction)
- Relevance scoring for potion_problem
- Configurable via environment variables

**Configuration Management** (`src/lean_explore/potion_problem/config.py`)
- Environment variable support via `.env` file
- Flexible path configuration
- Precedence: env vars → .env → potion_problem_config.yml → defaults

## Common Commands

```bash
# Setup environment
cp .env.example .env
# Edit .env to set POTION_PROBLEM_PATH (relative path: ./external/potion_problem)

# Install dependencies (including dev dependencies)
uv sync --extra dev

# Run tests
uv run pytest tests/ -v
uv run pytest tests/lean_explore/mcp/test_optimization.py -v  # Single test file

# Start MCP server (for Claude Code integration)
uv run python -m lean_explore.mcp.server --backend local

# Run auto-solver
uv run python run_auto_solver.py

# Check configuration
uv run python -c "from lean_explore.potion_problem.config import get_potion_config; print(get_potion_config())"

# Test API search
uv run python -c "from lean_explore.potion_problem.backend import PotionProblemBackend; from lean_explore.potion_problem.config import get_potion_config; backend = PotionProblemBackend(get_potion_config()); print(backend.search_apis('continuous', limit=3))"
```

## MCP Server Configuration

The MCP server can be optimized via environment variables (see `.mcp.json`):

```bash
# Enable optimization mode (reduces output tokens by ~70%)
export LEAN_EXPLORE_OPTIMIZE=true

# Set default search result limit
export LEAN_EXPLORE_DEFAULT_LIMIT=5

# Exclude keywords (be careful with mathematical terms!)
export LEAN_EXPLORE_EXCLUDE_KEYWORDS="quantum,physics,geometry"
# Note: Avoid excluding "telescope" as it filters important mathematical concepts
```

## Development Workflow

### Adding New MCP Tools
```python
# In src/lean_explore/potion_problem/tools.py
@mcp_app.tool()
async def your_new_tool(param: str, ctx: Context) -> Dict:
    """Tool description for MCP"""
    # Implementation using backend/service
```

### Enhancing Sorry Resolution
1. Update concept patterns in `auto_solver._extract_concepts()`
2. Add successful patterns to `_load_successful_patterns()`
3. Improve scoring logic in `score_api()`

### Running Tests with pytest
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=lean_explore --cov-report=html

# Run specific test class
uv run pytest tests/lean_explore/mcp/test_optimization.py::TestPotionOptimizedResult -v

# Run tests matching pattern
uv run pytest -k "test_optimization" -v
```

## API Database Structure

The API database (`mathlib_apis.db`) contains:
- `apis`: Core API information with existence flags
- `usage_patterns`: Code examples for each API
- `sorry_contributions`: APIs that help resolve specific sorries
- `api_errors`: Common mistakes and their fixes
- `non_existent_apis`: Patterns that don't exist (hallucination prevention)

## Submodule Management

The `potion_problem` repository is included as a submodule:
```bash
# Initialize/update submodule
git submodule update --init --recursive

# Pull latest changes
cd external/potion_problem
git pull origin main
cd ../..
git add external/potion_problem
git commit -m "Update potion_problem submodule"
```

## Known Issues and Solutions

### Search Performance
- First search may be slow (loading FAISS index)
- Consider implementing index caching
- Monitor PyTorch deprecation warnings

### API Not Found
- Check if API exists in different namespace (e.g., `Nat.` vs `ℕ.`)
- Verify import statements in target Lean file
- Update API database if Mathlib has changed

### False Positive Filtering
- Be cautious with exclude keywords
- "telescope" filters important mathematical concepts like "telescoping_series"
- Review `test_mcp_optimization_report.md` for analysis

## Important Design Decisions

1. **Hybrid Search Strategy**: Combines curated knowledge (high precision) with comprehensive search (high recall)
2. **Context-Aware Scoring**: APIs are scored based on sorry context, not just keyword matching
3. **Configurable Paths**: All paths use configuration management for portability
4. **Stateless Auto-Solver**: Each sorry is analyzed independently for simplicity
5. **MCP Optimization**: Balances token efficiency with information completeness

Remember: The goal is to help potion_problem developers complete formal proofs **accurately, efficiently, and without hallucination**.