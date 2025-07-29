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

### 2. ~~Hardcoded Paths~~ [RESOLVED]
- **Issue**: ~~Paths are hardcoded to `C:/Users/id374/workspace/potion_problem`~~
- **Status**: Resolved - Now uses environment variables and config management
- **Resolution**: 
  - Created `config.py` module for centralized configuration
  - Added `.env` file support with python-dotenv
  - All modules now use configurable paths
  - Created `.env.example` for easy setup

### 3. ~~Missing Backend Modules~~ [RESOLVED]
- **Issue**: ~~Not all backend modules are committed to git~~
- **Status**: All modules have been committed as of commit 891a628
- **Resolution Date**: Previously resolved

### 4. ~~Environment Setup Documentation~~ [RESOLVED]
- **Issue**: ~~No clear documentation on required environment variables~~
- **Status**: Resolved - Updated SETUP_REQUIREMENTS.md with comprehensive documentation
- **Resolution**:
  - Added environment variable documentation in SETUP_REQUIREMENTS.md
  - Created `.env.example` file with all configurable options
  - Documented configuration precedence and usage

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