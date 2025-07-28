"""MCP tools specific to Potion Problem integration.

These tools provide additional functionality beyond standard Lean-Explore search,
leveraging the curated API database from the potion_problem project.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from mcp.server.fastmcp import Context as MCPContext

from lean_explore.mcp.app import mcp_app
from lean_explore.potion_problem.service import HybridService

logger = logging.getLogger(__name__)


# Store the hybrid service instance
_hybrid_service: Optional[HybridService] = None


def get_hybrid_service() -> HybridService:
    """Get or create the hybrid service instance."""
    global _hybrid_service
    if _hybrid_service is None:
        _hybrid_service = HybridService()
    return _hybrid_service


@mcp_app.tool()
async def check_api_exists(
    ctx: MCPContext,
    api_name: str
) -> Dict[str, Any]:
    """Quick check if a specific API exists in Mathlib.
    
    This tool provides a fast way to verify API existence without full search.
    
    Args:
        ctx: The MCP context
        api_name: Exact API name to check (e.g., "Summable.tsum_add")
        
    Returns:
        Dictionary with existence status and basic info if found
    """
    service = get_hybrid_service()
    exists = service.check_api_exists(api_name)
    
    result = {
        "api_name": api_name,
        "exists": exists
    }
    
    if exists:
        # Get more details about the API
        results = service.potion_backend.search_apis(api_name, limit=1)
        if results:
            api_info = results[0]
            result.update({
                "signature": api_info.get("signature"),
                "import_path": api_info.get("import_path"),
                "deprecated": api_info.get("deprecated", False),
                "replacement_api": api_info.get("replacement_api"),
                "mathematical_significance": api_info.get("mathematical_significance")
            })
    
    return result


@mcp_app.tool()
async def get_api_usage(
    ctx: MCPContext,
    api_name: str
) -> Dict[str, Any]:
    """Get usage patterns and common errors for a specific API.
    
    This tool helps understand how to correctly use an API and avoid common mistakes.
    
    Args:
        ctx: The MCP context
        api_name: API name to get usage information for
        
    Returns:
        Dictionary containing usage patterns and error patterns
    """
    service = get_hybrid_service()
    return service.get_api_usage(api_name)


@mcp_app.tool()
async def search_by_sorry(
    ctx: MCPContext,
    module: str,
    sorry_line: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Search for APIs that help solve specific sorries in the potion_problem.
    
    This tool finds APIs that have been identified as useful for eliminating
    particular sorry statements.
    
    Args:
        ctx: The MCP context
        module: Module name (e.g., "IrwinHallTheory", "ProbabilityFoundations")
        sorry_line: Optional specific line number of the sorry
        
    Returns:
        List of APIs with their contribution levels and notes
    """
    service = get_hybrid_service()
    results = service.search_by_sorry(module, sorry_line)
    
    # Format results for better readability
    formatted_results = []
    for api in results:
        formatted_results.append({
            "api_name": api["api_name"],
            "signature": api["signature"],
            "import_path": api["import_path"],
            "contribution_level": api["contribution_level"],
            "notes": api.get("notes", ""),
            "sorry_line": api.get("sorry_line"),
            "mathematical_significance": api.get("mathematical_significance")
        })
    
    return formatted_results


@mcp_app.tool()
async def list_non_existent(
    ctx: MCPContext,
    search_context: Optional[str] = None
) -> List[Dict[str, Any]]:
    """List API patterns that have been confirmed not to exist in Mathlib.
    
    This tool helps avoid searching for APIs that are known not to exist,
    saving time and suggesting alternatives.
    
    Args:
        ctx: The MCP context
        search_context: Optional filter by search context (e.g., "conditional sum")
        
    Returns:
        List of non-existent API patterns with alternative approaches
    """
    service = get_hybrid_service()
    results = service.list_non_existent(search_context)
    
    # Format for clarity
    formatted_results = []
    for pattern in results:
        formatted_results.append({
            "pattern": pattern["pattern"],
            "description": pattern["description"],
            "search_context": pattern["search_context"],
            "alternative_approach": pattern["alternative_approach"]
        })
    
    return formatted_results


@mcp_app.tool()
async def get_error_patterns(
    ctx: MCPContext,
    api_name: str
) -> List[Dict[str, Any]]:
    """Get common error patterns and their corrections for a specific API.
    
    This tool helps identify and fix common mistakes when using Mathlib APIs.
    
    Args:
        ctx: The MCP context
        api_name: API name to get error patterns for
        
    Returns:
        List of error patterns with corrections and explanations
    """
    service = get_hybrid_service()
    patterns = service.potion_backend.get_error_patterns(api_name)
    
    # Format for clarity
    formatted_patterns = []
    for pattern in patterns:
        formatted_patterns.append({
            "wrong_way": pattern["error_pattern"],
            "correct_way": pattern["correct_pattern"],
            "error_message": pattern.get("error_message", ""),
            "explanation": pattern.get("explanation", "")
        })
    
    return formatted_patterns


@mcp_app.tool()
async def api_database_stats(
    ctx: MCPContext
) -> Dict[str, Any]:
    """Get statistics about the Potion Problem API database.
    
    This tool provides an overview of the curated API knowledge base.
    
    Args:
        ctx: The MCP context
        
    Returns:
        Dictionary with database statistics
    """
    service = get_hybrid_service()
    cursor = service.potion_backend.conn.cursor()
    
    # Get various statistics
    stats = {}
    
    # Total APIs
    cursor.execute("SELECT COUNT(*) FROM apis WHERE exists_in_mathlib = 1")
    stats["total_verified_apis"] = cursor.fetchone()[0]
    
    # Deprecated APIs
    cursor.execute("SELECT COUNT(*) FROM apis WHERE deprecated = 1")
    stats["deprecated_apis"] = cursor.fetchone()[0]
    
    # APIs with usage patterns
    cursor.execute("SELECT COUNT(DISTINCT api_name) FROM usage_patterns")
    stats["apis_with_usage_patterns"] = cursor.fetchone()[0]
    
    # APIs with error patterns
    cursor.execute("SELECT COUNT(DISTINCT api_name) FROM api_errors")
    stats["apis_with_error_patterns"] = cursor.fetchone()[0]
    
    # Sorry contributions
    cursor.execute("SELECT COUNT(DISTINCT api_name) FROM sorry_contributions")
    stats["apis_helping_sorries"] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT module || ':' || sorry_line) FROM sorry_contributions")
    stats["total_sorries_tracked"] = cursor.fetchone()[0]
    
    # Non-existent patterns
    cursor.execute("SELECT COUNT(*) FROM non_existent_apis")
    stats["non_existent_patterns"] = cursor.fetchone()[0]
    
    # Categories
    cursor.execute("SELECT COUNT(*) FROM categories")
    stats["total_categories"] = cursor.fetchone()[0]
    
    return stats