<h1 align="center">
  LeanExplore-PotionAssist
</h1>

<h3 align="center">
  A specialized fork of LeanExplore for Potion Problem formal verification support
</h3>

<p align="center">
  <a href="https://github.com/justincasher/lean-explore">
    <img src="https://img.shields.io/badge/Fork%20of-LeanExplore-blue.svg" alt="Fork of LeanExplore" />
  </a>
  <a href="https://github.com/justincasher/lean-explore/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/justincasher/lean-explore.svg" alt="license" />
  </a>
</p>

## 🎯 About This Fork

This is a **specialized fork** of [LeanExplore](https://github.com/justincasher/lean-explore) that has been customized to support the **Potion Problem (媚薬問題)** formal verification project. The primary goal is to prevent hallucination of non-existent Mathlib APIs and provide accurate, real-time assistance for formal proof development in Lean 4.

### Key Enhancements

- 🛡️ **Hallucination Prevention**: Integrated API existence verification against curated database
- 🔍 **Sorry-Focused Search**: Find APIs specifically helpful for eliminating sorry placeholders
- 📊 **Hybrid Search**: Combines 600k+ declarations from LeanExplore with curated Potion Problem API database
- 🤖 **Enhanced MCP Tools**: Custom tools for API verification, usage patterns, and error analysis
- 🚀 **Auto-Solver**: Automated sorry resolution suggestions with context-aware ranking

## 🏗️ Architecture

```
lean-explore-potionassist/
├── src/lean_explore/
│   ├── potion_problem/      # Potion Problem specific modules
│   │   ├── backend.py       # API database integration
│   │   ├── enhanced_service.py  # Hybrid search service
│   │   ├── auto_solver.py   # Automatic sorry solver
│   │   └── tools.py         # Custom MCP tools
│   └── ...                  # Original LeanExplore modules
├── potion_problem_config.yml # Custom configuration
├── CLAUDE.md               # Developer guide
└── POTION_PROBLEM_SETUP.md # Setup instructions
```

## 🚀 Quick Start

### Prerequisites

1. Python 3.12+
2. [Potion Problem repository](https://github.com/yourusername/potion_problem) at `C:\Users\id374\workspace\potion_problem`
3. Initialized API database at `potion_problem/api_database/mathlib_apis.db`

### Installation

```bash
# Clone this repository
git clone <this-repo-url> lean-explore-potionassist
cd lean-explore-potionassist

# Install with uv
uv sync

# Optional: Fetch LeanExplore data for comprehensive search
uv run leanexplore data fetch
```

### MCP Server Setup

#### For Claude Code

Create `.mcp.json` in your project:

```json
{
  "mcpServers": {
    "lean-explore-potion": {
      "command": "C:\\\\users\\\\id374\\\\.local\\\\bin\\\\uv.EXE",
      "args": [
        "run",
        "--project",
        "C:\\\\path\\\\to\\\\lean-explore-potionassist",
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

## 📋 Features

### Custom MCP Tools

- **`check_api_exists`**: Instantly verify if an API exists in Mathlib
- **`search_by_sorry`**: Find APIs for specific sorry locations
- **`get_api_usage`**: Retrieve usage patterns and examples
- **`list_non_existent`**: Check commonly mistaken API patterns
- **`get_error_patterns`**: Learn from common API usage errors
- **`api_database_stats`**: View API database statistics

### Auto-Solver

```bash
# Run automatic sorry solver
uv run python run_auto_solver.py
```

Analyzes sorry contexts and suggests relevant APIs with confidence scores.

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)**: Developer guide and architecture details
- **[POTION_PROBLEM_SETUP.md](POTION_PROBLEM_SETUP.md)**: Detailed setup instructions
- **[docs/MCP_INTEGRATION_GUIDE.md](docs/MCP_INTEGRATION_GUIDE.md)**: MCP integration reference

## 🤝 Contributing

This fork maintains compatibility with upstream LeanExplore while adding Potion Problem specific features. Contributions should:

1. Maintain backward compatibility with original LeanExplore
2. Focus on improving formal verification workflows
3. Include tests for new features
4. Update relevant documentation

## 📖 Original LeanExplore

This project is based on [LeanExplore](https://github.com/justincasher/lean-explore) by Justin Asher.

**Original features preserved:**
- 🔍 Semantic search for Lean 4 declarations
- 🤖 Model Context Protocol (MCP) server
- 🌐 Web API and CLI interface
- 📊 Local and remote backend support
- 🗄️ Vector database with FAISS indexing

**Original Citation:**

```bibtex
@software{Asher_LeanExplore_2025,
  author = {Asher, Justin},
  title = {{LeanExplore: A search engine for Lean 4 declarations}},
  year = {2025},
  url = {https://arxiv.org/abs/2506.11085}
}
```

## 📄 License

This fork maintains the same Apache License as the original LeanExplore project. See [LICENSE](LICENSE) for details.

---

**Note**: This repository will be renamed to `lean-explore-potionassist` after session completion to avoid confusion with the original LeanExplore project.