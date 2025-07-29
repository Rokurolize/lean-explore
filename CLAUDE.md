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

**PotionProblemBackend** (`backend.py`)
- Integrates with potion_problem's API database
- Validates API existence and tracks usage patterns
- Ranks APIs by sorry contribution scores

**EnhancedHybridService** (`enhanced_service.py`)
- Parallel search across 600k+ LeanExplore declarations and curated Potion DB
- True API discovery with confidence scoring
- Error pattern learning capabilities

**SorryAutoSolver** (`auto_solver.py`)
- Automated sorry analysis with context extraction
- Pattern matching from successful eliminations
- Depth-first search with pruning heuristics

**Configuration Management** (`config.py`)
- Environment variable support via `.env` file
- Flexible path configuration
- Precedence: env vars → .env → potion_problem_config.yml → defaults

## Common Commands

```bash
# Setup environment
cp .env.example .env
# Edit .env to set POTION_PROBLEM_PATH

# Install dependencies
uv sync

# Run auto-solver
uv run python run_auto_solver.py

# Start MCP server (for Claude Code integration)
uv run python -m lean_explore.mcp.server --backend local

# Run specific tests (when implemented)
uv run pytest tests/lean_explore/potion_problem/test_backend.py -v

# Check configuration
uv run python -c "from lean_explore.potion_problem.config import get_potion_config; print(get_potion_config())"

# Test API search
uv run python -c "from lean_explore.potion_problem.backend import PotionProblemBackend; from lean_explore.potion_problem.config import get_potion_config; backend = PotionProblemBackend(get_potion_config()); print(backend.search_apis('continuous', limit=3))"
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

### API Database Updates
The API database (`mathlib_apis.db`) contains:
- `apis`: Core API information with existence flags
- `usage_patterns`: Code examples for each API
- `sorry_contributions`: APIs that help resolve specific sorries
- `api_errors`: Common mistakes and their fixes
- `non_existent_apis`: Patterns that don't exist (hallucination prevention)

## Domain Knowledge

### Potion Problem Context
- **Goal**: Prove E[τ] = e (Euler's number) formally
- **Method**: Irwin-Hall distribution, telescoping series
- **Challenge**: Complex mathematical proofs requiring precise API usage

### Typical Sorry Patterns
1. **Convergence**: `summable_*`, `hasSum_*`
2. **Equality**: `tsum_eq_*`, `sum_eq_*`
3. **Inequality**: `le_of_*`, `lt_of_*`
4. **Limits**: `tendsto_*`, `lim_*`

### Key Lean 4 Modules
```
PotionProblem/
├── IrwinHallTheory.lean     # Main battlefield - contains most sorries
├── ProbabilityFoundations.lean
├── SeriesAnalysis.lean
└── FactorialSeries.lean
```

## Technical Requirements

- **Python**: 3.12+ (uses modern type hints)
- **LeanExplore Data**: Optional but recommended (~3.6GB database)
- **Dependencies**: Managed by `uv` (see pyproject.toml)
- **API Database**: Required SQLite database from potion_problem

## Troubleshooting

### Configuration Issues
- Ensure `.env` file exists with correct paths
- Check `POTION_PROBLEM_PATH` environment variable
- Verify database exists at configured location

### Search Performance
- First search may be slow (loading FAISS index)
- Consider implementing index caching
- Monitor PyTorch deprecation warnings

### API Not Found
- Check if API exists in different namespace (e.g., `Nat.` vs `ℕ.`)
- Verify import statements in target Lean file
- Update API database if Mathlib has changed

## Important Design Decisions

1. **Hybrid Search Strategy**: Combines curated knowledge (high precision) with comprehensive search (high recall)
2. **Context-Aware Scoring**: APIs are scored based on sorry context, not just keyword matching
3. **Configurable Paths**: All paths use configuration management for portability
4. **Stateless Auto-Solver**: Each sorry is analyzed independently for simplicity

Remember: The goal is to help potion_problem developers complete formal proofs **accurately, efficiently, and without hallucination**.