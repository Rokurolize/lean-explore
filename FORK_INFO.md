# Fork Information

## About This Fork

This is a specialized fork of [LeanExplore](https://github.com/justincasher/lean-explore) created specifically to support the **Potion Problem (媚薬問題)** formal verification project.

### Fork Details

- **Original Project**: LeanExplore v0.3.0 by Justin Asher
- **Fork Date**: July 29, 2025
- **Fork Purpose**: Prevent hallucination of non-existent Mathlib APIs in Lean 4 formal proofs
- **Target Project**: [Potion Problem](C:\Users\id374\workspace\potion_problem)

### Key Modifications

1. **Added `src/lean_explore/potion_problem/` module**:
   - `backend.py`: Integration with potion_problem's API database
   - `enhanced_service.py`: Hybrid search service
   - `auto_solver.py`: Automatic sorry resolution
   - `tools.py`: Custom MCP tools
   - `service.py`: Service orchestration

2. **Configuration Files**:
   - `potion_problem_config.yml`: Custom configuration for potion_problem integration
   - `CLAUDE.md`: Developer guide for this fork
   - `POTION_PROBLEM_SETUP.md`: Setup instructions

3. **Scripts**:
   - `run_auto_solver.py`: Automated sorry solver runner

### Relationship with Upstream

This fork maintains compatibility with the original LeanExplore while adding specialized features for formal verification support. The core LeanExplore functionality remains intact, allowing for:

- Full access to 600k+ Lean 4 declarations
- Original MCP server functionality
- All original CLI commands
- Vector search capabilities

### Future Rename

This repository will be renamed from `lean-explore` to `lean-explore-potionassist` to:
- Avoid confusion with the original project
- Clearly indicate its specialized purpose
- Maintain proper attribution to the original work

### Maintenance

This fork will:
- Track important updates from upstream LeanExplore
- Maintain compatibility where possible
- Focus development on formal verification support features
- Share improvements that benefit the broader community back to upstream

### Credits

- **Original Author**: Justin Asher (LeanExplore)
- **Fork Maintainers**: Potion Problem Contributors
- **License**: Apache 2.0 (same as original)