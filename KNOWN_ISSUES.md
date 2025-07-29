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
  - `test_config.py`: Configuration management

## Non-Critical Issues

### 1. Performance Optimization
- Hybrid search could be parallelized better
- FAISS index loading happens on every request
- Consider caching frequently used API search results

### 2. Error Handling
- Some database errors are caught but not properly logged
- MCP tool errors need better user-facing messages
- Add retry logic for transient database connection issues

### 3. Documentation Gaps
- No API documentation for new modules
- Missing examples for custom MCP tools usage
- Need docstrings for all public methods

## Future Enhancements

### 1. Algorithm Improvements for Sorry Resolution
- **Pattern Learning**: Analyze successful sorry resolutions to improve pattern matching
- **Context-Aware Scoring**: Weight APIs based on surrounding proof context
- **Dependency Analysis**: Consider API dependencies when suggesting candidates
- **Multi-Step Resolution**: Support suggesting sequences of APIs for complex sorries

### 2. Enhanced API Discovery
- **Semantic Search**: Improve query understanding beyond keyword matching
- **API Relationship Mapping**: Build graph of related APIs for better suggestions
- **Usage Pattern Mining**: Extract common API usage patterns from Mathlib

### 3. User Experience
- **Interactive Mode**: Allow users to provide feedback on suggestions
- **Explanation Generation**: Explain why specific APIs were suggested
- **Progress Tracking**: Show which sorries have been attempted/resolved

### 4. Integration Features
- **VS Code Extension**: Real-time sorry resolution suggestions in editor
- **CI/CD Integration**: Automated sorry tracking in pull requests
- **Metrics Dashboard**: Track sorry resolution success rates

## Maintenance Notes

- Keep synced with upstream LeanExplore for core functionality updates
- API database needs regular updates as Mathlib evolves
- Test against new Lean 4 versions for compatibility
- Monitor PyTorch deprecation warnings (BertSdpaSelfAttention)