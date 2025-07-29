"""Hybrid service that combines Potion Problem's API database with Lean-Explore's capabilities.

This service provides a unified interface that leverages both the curated API knowledge
from potion_problem and the comprehensive search capabilities of Lean-Explore.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from lean_explore.local.service import Service as LocalService
from lean_explore.shared.models.api import (
    APICitationsResponse,
    APISearchResponse,
    APISearchResultItem,
)
from lean_explore.potion_problem.backend import PotionProblemBackend
from lean_explore.potion_problem.config import get_potion_config, ConfigManager

logger = logging.getLogger(__name__)


class HybridService:
    """Service that combines PotionProblem backend with Lean-Explore local service."""
    
    def __init__(self, potion_config_path: Optional[Path] = None):
        """Initialize the hybrid service.
        
        Args:
            potion_config_path: Path to potion_problem configuration file
        """
        # Initialize Potion Problem backend using config manager
        if potion_config_path is None:
            # Use default config manager
            self.potion_config = get_potion_config()
        else:
            # Load from specific config file
            config_manager = ConfigManager(potion_config_path)
            self.potion_config = config_manager.get_potion_problem_config()
        
        self.potion_backend = PotionProblemBackend(self.potion_config)
        
        # Initialize Lean-Explore local service if data is available
        try:
            self.lean_service = LocalService()
            self.has_lean_service = True
            logger.info("Lean-Explore local service initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize Lean-Explore local service: {e}")
            logger.info("Will use Potion Problem database only")
            self.lean_service = None
            self.has_lean_service = False
    
    
    def search(
        self,
        queries: Union[str, List[str]],
        package_filters: Optional[List[str]] = None,
        limit: int = 30,
    ) -> APISearchResponse:
        """Search for Lean declarations using both backends.
        
        This method first searches the Potion Problem database for curated results,
        then optionally extends the search using Lean-Explore's comprehensive index.
        
        Args:
            queries: Search query or list of queries
            package_filters: Optional package filters
            limit: Maximum results per query
            
        Returns:
            Combined search results from both backends
        """
        # Normalize queries to list
        if isinstance(queries, str):
            queries = [queries]
        
        all_results = []
        seen_apis = set()  # Track seen APIs to avoid duplicates
        
        # First, search Potion Problem database
        logger.info(f"Searching Potion Problem database for: {queries}")
        for query in queries:
            potion_results = self.potion_backend.search_apis(query, limit=limit)
            
            # Convert and add results
            for result in potion_results:
                api_name = result['api_name']
                if api_name not in seen_apis:
                    seen_apis.add(api_name)
                    all_results.append(result)
        
        # If we have Lean-Explore service and need more results
        if self.has_lean_service and len(all_results) < limit:
            remaining_limit = limit - len(all_results)
            logger.info(f"Extending search with Lean-Explore (limit: {remaining_limit})")
            
            try:
                lean_response = self.lean_service.search(
                    query=' '.join(queries),  # Join queries into single string
                    package_filters=package_filters,
                    limit=remaining_limit * 2  # Get more to filter duplicates
                )
                
                # Add Lean-Explore results that aren't duplicates
                for item in lean_response.results:
                    if item.primary_declaration and item.primary_declaration.lean_name:
                        api_name = item.primary_declaration.lean_name
                        if api_name not in seen_apis and len(all_results) < limit:
                            seen_apis.add(api_name)
                            # Convert to dict format for consistency
                            all_results.append({
                                'api_name': api_name,
                                'signature': item.statement_text or '',
                                'mathematical_significance': item.docstring or item.informal_description or '',
                                'source_file': item.source_file,
                                'line_number': item.range_start_line,
                                'lean_explore_id': item.id,
                                'import_path': '',  # Not available from APIPrimaryDeclarationInfo
                                'exists_in_mathlib': True,
                                'deprecated': False,
                            })
            except Exception as e:
                logger.error(f"Error searching with Lean-Explore: {e}")
        
        # Convert combined results to APISearchResponse
        return self.potion_backend.convert_to_api_search_response(all_results[:limit])
    
    def get_group_by_id(self, group_id: int) -> APISearchResultItem:
        """Get a specific group by ID.
        
        First checks if it's a Potion Problem ID, then falls back to Lean-Explore.
        """
        # Check if it's in Potion Problem database
        cursor = self.potion_backend.conn.cursor()
        cursor.execute(
            "SELECT * FROM apis WHERE lean_explore_id = ?",
            (group_id,)
        )
        result = cursor.fetchone()
        
        if result:
            # Convert to APISearchResultItem
            db_results = [dict(result)]
            response = self.potion_backend.convert_to_api_search_response(db_results)
            if response.results:
                return response.results[0]
        
        # Fall back to Lean-Explore if available
        if self.has_lean_service:
            return self.lean_service.get_group_by_id(group_id)
        
        raise ValueError(f"Group ID {group_id} not found")
    
    def get_dependencies(self, group_id: int) -> APICitationsResponse:
        """Get dependencies for a group.
        
        This primarily uses Lean-Explore's dependency tracking.
        """
        if self.has_lean_service:
            return self.lean_service.get_dependencies(group_id)
        
        # Minimal implementation for Potion Problem only
        return APICitationsResponse(
            group_id=group_id,
            direct_prereqs=[],
            all_prereqs=[]
        )
    
    # Additional Potion Problem specific methods
    
    def check_api_exists(self, api_name: str) -> bool:
        """Quick check if an API exists."""
        return self.potion_backend.check_api_exists(api_name)
    
    def get_api_usage(self, api_name: str) -> Dict[str, Any]:
        """Get usage patterns and error patterns for an API."""
        return {
            'usage_patterns': self.potion_backend.get_api_usage_patterns(api_name),
            'error_patterns': self.potion_backend.get_error_patterns(api_name),
        }
    
    def search_by_sorry(self, module: str, sorry_line: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for APIs that help with specific sorries."""
        return self.potion_backend.search_by_sorry(module, sorry_line)
    
    def list_non_existent(self, search_context: Optional[str] = None) -> List[Dict[str, Any]]:
        """List APIs that are known not to exist."""
        return self.potion_backend.list_non_existent_patterns(search_context)