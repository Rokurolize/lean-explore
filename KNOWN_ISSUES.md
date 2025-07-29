# Known Issues and TODOs

## Critical TODOs

### 1. Missing Tests for Potion Problem Integration
- **Issue**: No tests exist for `src/lean_explore/potion_problem/` modules
- **Impact**: Code reliability cannot be guaranteed
- **Required Tests**:
  - `test_backend.py`: API database connection and queries
  - `test_enhanced_service.py`: Hybrid search functionality
  - `test_auto_solver.py`: Sorry resolution algorithms
  - `test_tools.py`: MCP tool implementations

### 2. Hardcoded Paths
- **Issue**: Paths are hardcoded to `C:/Users/id374/workspace/potion_problem`
- **Fix Needed**: Make paths configurable via environment variables or config file
- **Files Affected**:
  - `src/lean_explore/potion_problem/enhanced_service.py` (line 30-31)
  - `run_auto_solver.py` (line 27)

### 3. Missing Backend Modules
- **Issue**: Not all backend modules are committed to git
- **Missing Files**:
  - `src/lean_explore/potion_problem/backend.py`
  - `src/lean_explore/potion_problem/service.py`
  - `src/lean_explore/potion_problem/tools.py`
  - `src/lean_explore/potion_problem/__init__.py`

### 4. Environment Setup Documentation
- **Issue**: No clear documentation on required environment variables
- **Needed**:
  - Document `PYTHONPATH` requirements
  - Document API key management (if using API backend)
  - Document data directory setup

## Non-Critical Issues

### 1. Performance Optimization
- Hybrid search could be parallelized better
- FAISS index loading happens on every request

### 2. Error Handling
- Some database errors are caught but not properly logged
- MCP tool errors need better user-facing messages

### 3. Documentation Gaps
- No API documentation for new modules
- Missing examples for custom MCP tools usage

## Future Enhancements

1. **Automated API Discovery**
   - Monitor build errors to discover new APIs
   - Auto-update API database from CI/CD

2. **Machine Learning Integration**
   - Learn from successful sorry resolutions
   - Predict API usage patterns

3. **IDE Integration**
   - VS Code extension for real-time API validation
   - Inline sorry resolution suggestions

4. **Monitoring and Analytics**
   - Track which APIs are most helpful
   - Monitor hallucination prevention effectiveness

## Maintenance Notes

- Keep synced with upstream LeanExplore for core functionality updates
- API database needs regular updates as Mathlib evolves
- Test against new Lean 4 versions for compatibility