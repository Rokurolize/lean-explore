"""Enhanced MCP tools with sorry analysis integration."""

from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import Context as MCPContext
from lean_explore.mcp.app import mcp_app
from lean_explore.mcp.tools import search
from lean_explore.mcp.sorry_analyzer import SorryContextAnalyzer
from lean_explore.mcp.smart_filter import SmartExcludeFilter
from lean_explore.mcp.api_recommender import APIRecommendationEngine


@mcp_app.tool()
async def search_with_context(
    ctx: MCPContext,
    query: str,
    context: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Search with mathematical context awareness.
    
    Args:
        ctx: MCP context
        query: Search query
        context: Mathematical context (e.g., 'measure_theory', 'series_analysis')
        limit: Maximum results
        
    Returns:
        Search results with context-aware filtering
    """
    # Use smart filter if context is provided
    if context:
        from lean_explore.mcp.tools import _get_exclude_keywords
        exclude_keywords = _get_exclude_keywords()
        smart_filter = SmartExcludeFilter(exclude_keywords)
        
        # Check if query should be excluded based on context
        if not smart_filter.should_exclude(query, context=context):
            return await search(ctx, query, limit=limit)
    
    return await search(ctx, query, limit=limit)


@mcp_app.tool()
async def analyze_sorry(
    ctx: MCPContext,
    sorry_context: str,
) -> Dict[str, Any]:
    """Analyze a sorry context to extract useful information.
    
    Args:
        ctx: MCP context
        sorry_context: The Lean 4 code containing sorry
        
    Returns:
        Analysis results including keywords, recommendations, and context
    """
    analyzer = SorryContextAnalyzer()
    result = analyzer.analyze(sorry_context)
    
    # Get API recommendations
    recommender = APIRecommendationEngine()
    recommendations = recommender.recommend(result.keywords)
    
    return {
        'keywords': result.keywords,
        'recommended_searches': [
            s.query if hasattr(s, 'query') else str(s) 
            for s in result.suggested_searches
        ],
        'mathematical_context': result.mathematical_context,
        'mentioned_apis': result.mentioned_apis,
        'api_recommendations': [
            {
                'api_name': r.api_name,
                'relevance_score': r.relevance_score,
                'confidence': r.confidence,
                'reason': r.reason
            }
            for r in recommendations
        ]
    }


@mcp_app.tool()
async def search_enhanced(
    ctx: MCPContext,
    query: str,
    use_recommendations: bool = False,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Enhanced search with API recommendations.
    
    Args:
        ctx: MCP context
        query: Search query
        use_recommendations: Whether to include API recommendations
        limit: Maximum results
        
    Returns:
        Search results with optional recommendations
    """
    # Regular search
    search_results = await search(ctx, query, limit=limit)
    
    result = {
        'results': search_results,
        'query': query
    }
    
    if use_recommendations:
        # Extract keywords from query
        keywords = query.lower().split()
        
        # Get recommendations
        recommender = APIRecommendationEngine()
        recommendations = recommender.recommend(keywords)
        
        result['recommendations'] = [
            {
                'api_name': r.api_name,
                'relevance_score': r.relevance_score,
                'confidence': r.confidence,
                'reason': r.reason
            }
            for r in recommendations
        ]
    
    return result