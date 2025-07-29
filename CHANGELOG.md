# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

N/A

## [0.3.0-potion] - 2025-07-29

### Added
- **Potion Problem Integration**: Complete integration with potion_problem's API database for hallucination prevention
- **Enhanced Hybrid Service**: Parallel search combining 600k+ LeanExplore declarations with curated API database
- **Custom MCP Tools**: New tools for API verification, usage patterns, and sorry-specific search
  - `check_api_exists`: Instant API existence verification
  - `search_by_sorry`: Find APIs for specific sorry locations
  - `get_api_usage`: Retrieve usage patterns and examples
  - `list_non_existent`: Check commonly mistaken API patterns
  - `get_error_patterns`: Learn from common API usage errors
  - `api_database_stats`: View API database statistics
- **Auto-Solver System**: Automated sorry resolution with context-aware API suggestions
- **Custom Configuration**: `potion_problem_config.yml` for project-specific settings
- **Developer Documentation**: `CLAUDE.md` and enhanced setup guides

### Changed
- Modified backend architecture to support dual database operation
- Enhanced search algorithms to prioritize APIs that help with sorry elimination
- Updated MCP server to include potion_problem specific functionality
- Improved error handling to catch and learn from API usage mistakes

### Fork Information
- This version represents a specialized fork of LeanExplore v0.3.0
- Forked specifically to support the Potion Problem (媚薬問題) formal verification project
- Maintains compatibility with original LeanExplore while adding hallucination prevention features

## [0.3.0] - 2025-06-09

### Added
- Implemented batch processing for `search`, `get_by_id`, and `get_dependencies` methods across the stack, allowing them to accept lists of requests for greater efficiency.
- The **API Client** (`lean_explore.api.client`) now sends batch requests concurrently using `asyncio.gather` to reduce network latency.
- The **Local Service** (`lean_explore.local.service`) was updated to process lists of requests serially against the local database and FAISS index.
- The **MCP Tools** (`lean_explore.mcp.tools`) now expose this batch functionality and provide list-based responses.
- The **AI Agent** instructions (`lean_explore.cli.agent`) were updated to explicitly guide the model to use batch calls for more efficient tool use.

## [0.2.2] - 2025-06-06

### Changed
- Updated minimum Python requirement to `>=3.10`.