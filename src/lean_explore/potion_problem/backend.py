"""Custom backend service for Potion Problem integration with Lean-Explore.

This module provides a custom backend that integrates with the potion_problem's
API database, allowing searches to leverage both the existing API knowledge base
and Lean-Explore's comprehensive search capabilities.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging
from dataclasses import dataclass

from lean_explore.shared.models.api import (
    APIPrimaryDeclarationInfo,
    APISearchResponse,
    APISearchResultItem,
)

logger = logging.getLogger(__name__)


@dataclass
class PotionProblemConfig:
    """Configuration for Potion Problem integration."""
    api_database_path: Path
    workspace_path: Path
    prioritize_sorry_contributions: bool = True
    include_error_patterns: bool = True
    sorry_contribution_weight: float = 2.0


class PotionProblemBackend:
    """Custom backend service that integrates with potion_problem's API database."""
    
    def __init__(self, config: PotionProblemConfig):
        self.config = config
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Establish connection to the API database."""
        try:
            self.conn = sqlite3.connect(self.config.api_database_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to API database: {self.config.api_database_path}")
        except Exception as e:
            logger.error(f"Failed to connect to API database: {e}")
            raise
    
    def _close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def search_apis(
        self, 
        query: str, 
        limit: int = 30,
        include_deprecated: bool = False
    ) -> List[Dict[str, Any]]:
        """Search for APIs in the potion_problem database.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            include_deprecated: Whether to include deprecated APIs
            
        Returns:
            List of API records matching the query
        """
        cursor = self.conn.cursor()
        
        # Build the WHERE clause
        where_conditions = ["api_name LIKE ? OR signature LIKE ? OR mathematical_significance LIKE ?"]
        params = [f"%{query}%", f"%{query}%", f"%{query}%"]
        
        if not include_deprecated:
            where_conditions.append("deprecated = 0")
        
        # If prioritizing sorry contributions, join with that table
        if self.config.prioritize_sorry_contributions:
            sql = f"""
            SELECT DISTINCT a.*, 
                   COALESCE(MAX(sc.contribution_level), 0) as max_contribution
            FROM apis a
            LEFT JOIN sorry_contributions sc ON a.api_name = sc.api_name
            WHERE (a.api_name LIKE ? OR a.signature LIKE ? OR a.mathematical_significance LIKE ?)
            {'AND a.deprecated = 0' if not include_deprecated else ''}
            GROUP BY a.api_name
            ORDER BY max_contribution DESC, a.api_name
            LIMIT ?
            """
        else:
            sql = f"""
            SELECT * FROM apis
            WHERE (api_name LIKE ? OR signature LIKE ? OR mathematical_significance LIKE ?)
            {'AND deprecated = 0' if not include_deprecated else ''}
            ORDER BY api_name
            LIMIT ?
            """
        
        params.append(limit)
        
        cursor.execute(sql, params)
        results = []
        for row in cursor.fetchall():
            # Convert row to dict and ensure required fields have defaults
            result = dict(row)
            # Ensure fields that might be NULL have default values
            result['source_file'] = result.get('source_file') or ''
            result['line_number'] = result.get('line_number') or 0
            results.append(result)
        
        return results
    
    def check_api_exists(self, api_name: str) -> bool:
        """Quick check if an API exists in the database.
        
        Args:
            api_name: Exact API name to check
            
        Returns:
            True if API exists and is not deprecated
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT exists_in_mathlib FROM apis WHERE api_name = ? AND deprecated = 0",
            (api_name,)
        )
        result = cursor.fetchone()
        return bool(result and result[0])
    
    def get_api_usage_patterns(self, api_name: str) -> List[Dict[str, Any]]:
        """Get usage patterns for a specific API.
        
        Args:
            api_name: API name to get patterns for
            
        Returns:
            List of usage pattern records
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT pattern_code, description 
            FROM usage_patterns 
            WHERE api_name = ?
            """,
            (api_name,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_error_patterns(self, api_name: str) -> List[Dict[str, Any]]:
        """Get common error patterns for a specific API.
        
        Args:
            api_name: API name to get error patterns for
            
        Returns:
            List of error pattern records
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT error_pattern, correct_pattern, error_message, explanation
            FROM api_errors
            WHERE api_name = ?
            """,
            (api_name,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def search_by_sorry(self, module: str, sorry_line: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for APIs that contribute to solving specific sorries.
        
        Args:
            module: Module name (e.g., "IrwinHallTheory")
            sorry_line: Optional specific line number
            
        Returns:
            List of APIs that help with the specified sorry
        """
        cursor = self.conn.cursor()
        
        if sorry_line:
            sql = """
            SELECT a.*, sc.contribution_level, sc.notes
            FROM apis a
            JOIN sorry_contributions sc ON a.api_name = sc.api_name
            WHERE sc.module = ? AND sc.sorry_line = ?
            ORDER BY sc.contribution_level DESC
            """
            params = (module, sorry_line)
        else:
            sql = """
            SELECT a.*, sc.contribution_level, sc.notes, sc.sorry_line
            FROM apis a
            JOIN sorry_contributions sc ON a.api_name = sc.api_name
            WHERE sc.module = ?
            ORDER BY sc.contribution_level DESC, sc.sorry_line
            """
            params = (module,)
        
        cursor.execute(sql, params)
        results = []
        for row in cursor.fetchall():
            result = dict(row)
            # Ensure fields that might be NULL have default values
            result['source_file'] = result.get('source_file') or ''
            result['line_number'] = result.get('line_number') or 0
            results.append(result)
        return results
    
    def list_non_existent_patterns(self, search_context: Optional[str] = None) -> List[Dict[str, Any]]:
        """List patterns that have been confirmed as non-existent.
        
        Args:
            search_context: Optional filter by search context
            
        Returns:
            List of non-existent API patterns
        """
        cursor = self.conn.cursor()
        
        if search_context:
            sql = """
            SELECT pattern, description, search_context, alternative_approach
            FROM non_existent_apis
            WHERE search_context LIKE ?
            """
            params = (f"%{search_context}%",)
        else:
            sql = """
            SELECT pattern, description, search_context, alternative_approach
            FROM non_existent_apis
            ORDER BY pattern
            """
            params = ()
        
        cursor.execute(sql, params)
        results = []
        for row in cursor.fetchall():
            result = dict(row)
            # Ensure fields that might be NULL have default values
            result['source_file'] = result.get('source_file') or ''
            result['line_number'] = result.get('line_number') or 0
            results.append(result)
        return results
    
    def convert_to_api_search_response(self, db_results: List[Dict[str, Any]]) -> APISearchResponse:
        """Convert database results to APISearchResponse format.
        
        Args:
            db_results: Results from database query
            
        Returns:
            APISearchResponse compatible with Lean-Explore
        """
        items = []
        for result in db_results:
            # Create APIPrimaryDeclarationInfo if we have the information
            declaration = None
            if result.get('api_name'):
                declaration = APIPrimaryDeclarationInfo(
                    lean_name=result['api_name']
                )
            
            # Create APISearchResultItem
            # Ensure we have a valid ID - use lean_explore_id if available, otherwise hash of api_name
            item_id = result.get('lean_explore_id')
            if item_id is None:
                # Create a stable ID from the API name
                item_id = abs(hash(result['api_name'])) % (10**9)  # Keep it in reasonable range
            
            item = APISearchResultItem(
                id=item_id,
                primary_declaration=declaration,
                source_file=result.get('source_file', ''),  # Provide empty string if None
                range_start_line=result.get('line_number', 0),  # Provide 0 if None
                statement_text=f"{result['api_name']} : {result['signature']}",
                docstring=result.get('mathematical_significance'),
                informal_description=None,  # Could be enhanced
                display_statement_text=None,
            )
            items.append(item)
        
        # Note: APISearchResponse requires these fields
        return APISearchResponse(
            query="",  # We don't track the original query in this method
            packages_applied=None,
            results=items,
            count=len(items),
            total_candidates_considered=len(items),  # Same as count for now
            processing_time_ms=0  # We don't track timing
        )
    
    def __del__(self):
        """Cleanup database connection."""
        self._close()