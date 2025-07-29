"""Enhanced Hybrid Service that fully leverages both Potion Problem and Lean-Explore.

This enhanced version properly utilizes the 600k+ declarations from Lean-Explore
for true API discovery while maintaining the curated knowledge from Potion Problem.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from collections import defaultdict

from lean_explore.local.service import Service as LocalService
from lean_explore.shared.models.api import (
    APICitationsResponse,
    APISearchResponse,
    APISearchResultItem,
)
from lean_explore.potion_problem.backend import PotionProblemBackend
from lean_explore.potion_problem.config import get_potion_config

logger = logging.getLogger(__name__)


class EnhancedHybridService:
    """Enhanced service that properly leverages both backends for true API discovery."""
    
    def __init__(self, potion_config_path: Optional[Path] = None):
        """Initialize the enhanced hybrid service."""
        # Initialize Potion Problem backend using config manager
        self.potion_config = get_potion_config()
        self.potion_backend = PotionProblemBackend(self.potion_config)
        
        # Initialize Lean-Explore local service
        try:
            self.lean_service = LocalService()
            self.has_lean_service = True
            logger.info("Lean-Explore local service initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize Lean-Explore local service: {e}")
            self.lean_service = None
            self.has_lean_service = False
    
    def parallel_search(
        self,
        query: str,
        limit: int = 30,
        package_filters: Optional[List[str]] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search both backends in parallel and return categorized results.
        
        Returns:
            Dictionary with 'verified', 'new_discoveries', and 'all' results
        """
        results = {
            'verified': [],      # From Potion Problem (curated)
            'new_discoveries': [],  # From Lean-Explore (not in Potion)
            'all': []            # Combined results
        }
        
        # Search Potion Problem database
        potion_results = self.potion_backend.search_apis(query, limit=limit)
        potion_api_names = {r['api_name'] for r in potion_results}
        
        results['verified'] = potion_results
        
        # Search Lean-Explore if available
        if self.has_lean_service:
            try:
                # Search with much larger limit to find new APIs
                lean_response = self.lean_service.search(
                    query=query,  # Fixed: was queries=queries
                    package_filters=package_filters,
                    limit=limit * 5  # Get more results for discovery
                )
                
                # Categorize Lean-Explore results
                for item in lean_response.results:
                    if item.primary_declaration and item.primary_declaration.lean_name:
                        api_name = item.primary_declaration.lean_name
                        
                        # Convert to dict format
                        api_dict = {
                            'api_name': api_name,
                            'signature': item.statement_text or '',
                            'mathematical_significance': item.docstring or item.informal_description or '',
                            'source_file': item.source_file,
                            'line_number': item.range_start_line,
                            'lean_explore_id': item.id,
                            'import_path': item.source_file or '',
                            'exists_in_mathlib': True,
                            'deprecated': False,
                            'discovery_source': 'lean-explore',
                            'page_rank_score': getattr(item, 'page_rank_score', 0),
                        }
                        
                        # Check if it's a new discovery
                        if api_name not in potion_api_names:
                            results['new_discoveries'].append(api_dict)
                
            except Exception as e:
                logger.error(f"Error searching with Lean-Explore: {e}")
        
        # Combine results with scoring
        results['all'] = self._merge_and_score(
            results['verified'],
            results['new_discoveries'],
            limit
        )
        
        return results
    
    def _merge_and_score(
        self,
        verified_apis: List[Dict[str, Any]],
        new_apis: List[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Merge and score results from both sources."""
        all_results = []
        
        # Verified APIs get boost
        for api in verified_apis:
            api['final_score'] = api.get('score', 0) + 1.0  # Boost for being verified
            api['is_verified'] = True
            all_results.append(api)
        
        # New discoveries get scored based on PageRank and relevance
        for api in new_apis:
            api['final_score'] = api.get('page_rank_score', 0) * 0.5
            api['is_verified'] = False
            api['is_new_discovery'] = True
            all_results.append(api)
        
        # Sort by score and return top results
        all_results.sort(key=lambda x: x['final_score'], reverse=True)
        return all_results[:limit]
    
    def discover_new_apis(
        self,
        query: str,
        limit: int = 50,
        min_page_rank: float = 0.01
    ) -> List[Dict[str, Any]]:
        """Specifically search for APIs not in Potion Problem database.
        
        This is the key method for true API discovery.
        """
        if not self.has_lean_service:
            return []
        
        new_apis = []
        
        try:
            # Search Lean-Explore with large limit
            lean_response = self.lean_service.search(
                query=query,
                limit=limit * 3
            )
            
            # Get all known APIs from Potion Problem
            known_apis = set()
            cursor = self.potion_backend.conn.cursor()
            cursor.execute("SELECT api_name FROM apis")
            known_apis = {row[0] for row in cursor.fetchall()}
            
            # Filter for truly new APIs
            for item in lean_response.results:
                if not item.primary_declaration:
                    continue
                
                api_name = item.primary_declaration.lean_name
                
                # Skip if already known
                if api_name in known_apis:
                    continue
                
                # Calculate confidence score
                confidence = self._calculate_discovery_confidence(item, query)
                
                if confidence > 0.3:  # Threshold for relevance
                    new_apis.append({
                        'api_name': api_name,
                        'signature': item.statement_text or '',
                        'docstring': item.docstring or '',
                        'informal_description': item.informal_description or '',
                        'import_path': item.source_file or '',
                        'lean_explore_id': item.id,
                        'confidence': confidence,
                        'page_rank_score': getattr(item, 'page_rank_score', 0),
                        'source_file': item.source_file,
                        'line_number': item.range_start_line,
                    })
            
            # Sort by confidence
            new_apis.sort(key=lambda x: x['confidence'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error discovering new APIs: {e}")
        
        return new_apis[:limit]
    
    def _calculate_discovery_confidence(
        self,
        item: APISearchResultItem,
        query: str
    ) -> float:
        """Calculate confidence score for a discovered API."""
        confidence = 0.0
        
        # PageRank contribution
        if hasattr(item, 'page_rank_score'):
            confidence += item.page_rank_score * 0.3
        
        # Text relevance
        if item.primary_declaration and item.primary_declaration.lean_name:
            name = item.primary_declaration.lean_name.lower()
            query_terms = query.lower().split()
            
            # Exact match bonus
            for term in query_terms:
                if term in name:
                    confidence += 0.2
        
        # Has documentation bonus
        if item.docstring:
            confidence += 0.1
        if item.informal_description:
            confidence += 0.1
        
        # Semantic similarity (if available)
        if hasattr(item, 'similarity_score'):
            confidence += item.similarity_score * 0.3
        
        return min(confidence, 1.0)
    
    def analyze_sorry_with_discovery(
        self,
        module: str,
        sorry_line: int
    ) -> Dict[str, Any]:
        """Analyze a sorry and discover potentially useful new APIs."""
        # Get curated suggestions
        curated = self.potion_backend.search_by_sorry(module, sorry_line)
        
        # Extract keywords from sorry context
        keywords = self._extract_sorry_keywords(module, sorry_line)
        
        # Discover new APIs for each keyword
        all_discoveries = []
        for keyword in keywords:
            discoveries = self.discover_new_apis(keyword, limit=10)
            all_discoveries.extend(discoveries)
        
        # Remove duplicates and sort by confidence
        seen = set()
        unique_discoveries = []
        for api in all_discoveries:
            if api['api_name'] not in seen:
                seen.add(api['api_name'])
                unique_discoveries.append(api)
        
        unique_discoveries.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'sorry_location': f"{module}:{sorry_line}",
            'curated_suggestions': curated[:5],
            'new_discoveries': unique_discoveries[:10],
            'keywords_used': keywords
        }
    
    def _extract_sorry_keywords(self, module: str, sorry_line: int) -> List[str]:
        """Extract relevant keywords from sorry context."""
        # This would analyze the sorry's surrounding code
        # For now, return common mathematical concepts
        keywords = []
        
        # Map module/line to known concepts
        keyword_map = {
            ('IrwinHallTheory', 174): ['alternating sum', 'binomial', 'choose'],
            ('IrwinHallTheory', 204): ['forward difference', 'finite difference', 'factorial'],
            ('IrwinHallTheory', 229): ['sum', 'factorial', 'finite difference'],
            ('IrwinHallTheory', 273): ['continuous', 'piecewise', 'floor'],
        }
        
        return keyword_map.get((module, sorry_line), ['sum', 'continuous'])
    
    def sync_discovered_apis(self, threshold: float = 0.7) -> int:
        """Sync high-confidence discovered APIs back to Potion Problem database."""
        if not self.has_lean_service:
            return 0
        
        # Search for commonly needed patterns
        patterns = [
            'factorial', 'continuous', 'sum', 'derivative',
            'finite difference', 'binomial', 'choose'
        ]
        
        added_count = 0
        
        for pattern in patterns:
            discoveries = self.discover_new_apis(pattern, limit=20)
            
            for api in discoveries:
                if api['confidence'] >= threshold:
                    # Add to Potion Problem database
                    success = self.potion_backend.add_api(
                        api_name=api['api_name'],
                        signature=api['signature'],
                        import_path=api['import_path'],
                        mathematical_significance=api.get('docstring', ''),
                        lean_explore_id=api['lean_explore_id']
                    )
                    if success:
                        added_count += 1
                        logger.info(f"Added new API: {api['api_name']}")
        
        return added_count
    
    # Backward compatibility methods
    def search(self, query: str, limit: int = 30) -> APISearchResponse:
        """Backward compatible search method."""
        results = self.parallel_search(query, limit)
        combined_results = results['all']
        
        # Convert to APISearchResponse
        return self.potion_backend.convert_to_api_search_response(combined_results)
    
    def check_api_exists(self, api_name: str) -> bool:
        """Check if API exists in either backend."""
        # First check Potion Problem
        if self.potion_backend.check_api_exists(api_name):
            return True
        
        # Then check Lean-Explore
        if self.has_lean_service:
            try:
                results = self.lean_service.search(query=api_name, limit=5)
                for item in results.results:
                    if item.primary_declaration and item.primary_declaration.lean_name == api_name:
                        return True
            except:
                pass
        
        return False