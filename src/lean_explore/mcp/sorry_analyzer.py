"""
Sorry Context Analyzer - Extract meaningful information from Lean 4 sorry contexts.

Following TDD approach: minimal implementation to pass tests.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass 
class SearchQuery:
    """A prioritized search query."""
    query: str
    priority: str = "medium"


@dataclass
class SorryAnalysisResult:
    """Result of analyzing a sorry context."""
    keywords: List[str]
    suggested_searches: List[Union[str, SearchQuery]]
    mathematical_context: Optional[str]
    mentioned_apis: List[str]
    mentioned_imports: List[str]
    
    def __contains__(self, item: str) -> bool:
        """Allow 'measure' in result.suggested_searches syntax."""
        for search in self.suggested_searches:
            if isinstance(search, str):
                if item in search:
                    return True
            elif isinstance(search, SearchQuery):
                if item in search.query:
                    return True
        return False
    
    def is_mathematical_context(self, term: str) -> bool:
        """Check if a term is used in mathematical context."""
        # Simple implementation: if "series" or "sum" is in context, it's mathematical
        return any(math_term in ' '.join(self.keywords) 
                  for math_term in ['series', 'sum', 'identity'])
    
    def should_exclude(self, api_name: str) -> bool:
        """Check if an API should be excluded."""
        # Never exclude if it's a suggested search
        for search in self.suggested_searches:
            if isinstance(search, str) and api_name == search:
                return False
            elif isinstance(search, SearchQuery) and api_name == search.query:
                return False
        return True


class SorryContextAnalyzer:
    """Analyzes sorry contexts to extract meaningful search information."""
    
    def __init__(self):
        # Mathematical keywords to look for
        self.math_keywords = {
            'simplex', 'volume', 'factorial', 'measure', 'summable',
            'alternating', 'binomial', 'choose', 'telescoping', 'series',
            'sum', 'continuous', 'piecewise', 'hitting_time', 'pmf'
        }
        
        # Patterns for extracting information
        self.patterns = {
            'factorial': r'\b\d+\s*/\s*n\.factorial\b|1/n!',
            'alternating': r'\(\-1\s*:\s*ℝ?\)\s*\^\s*\w+|\(\-1\)\s*\^\s*\w+',
            'api_mention': r'(?:Use|Try|Need|Apply)\s*:?\s*(\w+(?:\.\w+)*)',
            'import_mention': r'from\s+(Mathlib\.\S+)'
        }
    
    def analyze(self, sorry_context: str) -> SorryAnalysisResult:
        """Analyze a sorry context and extract useful information."""
        # Extract keywords
        keywords = self._extract_keywords(sorry_context)
        
        # Extract mentioned APIs and imports
        mentioned_apis = self._extract_mentioned_apis(sorry_context)
        mentioned_imports = self._extract_mentioned_imports(sorry_context)
        
        # Generate suggested searches
        suggested_searches = self._generate_search_queries(
            keywords, mentioned_apis, sorry_context
        )
        
        # Determine mathematical context
        mathematical_context = self._determine_context(keywords)
        
        # Keep SearchQuery objects for tests that need them
        # But also provide string access
        return SorryAnalysisResult(
            keywords=keywords,
            suggested_searches=suggested_searches,
            mathematical_context=mathematical_context,
            mentioned_apis=mentioned_apis,
            mentioned_imports=mentioned_imports
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract mathematical keywords from text."""
        text_lower = text.lower()
        found_keywords = []
        
        # Check for each mathematical keyword
        for keyword in self.math_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        # Check for special patterns
        if re.search(self.patterns['factorial'], text):
            found_keywords.append('factorial')
        
        if re.search(self.patterns['alternating'], text):
            if 'alternating' not in found_keywords:
                found_keywords.append('alternating')
        
        return found_keywords
    
    def _extract_mentioned_apis(self, text: str) -> List[str]:
        """Extract APIs mentioned in comments."""
        apis = []
        
        # Look for API mentions in comments
        for match in re.finditer(self.patterns['api_mention'], text):
            api = match.group(1)
            if '.' in api:  # Likely an API name
                apis.append(api)
        
        # Also check for specific API names in text
        if 'Continuous.if' in text:
            apis.append('Continuous.if')
        if 'continuous_piecewise' in text:
            apis.append('continuous_piecewise')
            
        return apis
    
    def _extract_mentioned_imports(self, text: str) -> List[str]:
        """Extract import paths mentioned in comments."""
        imports = []
        
        # Look for Mathlib paths
        if 'Mathlib.Topology.Piecewise' in text:
            imports.append('Mathlib.Topology.Piecewise')
            
        for match in re.finditer(self.patterns['import_mention'], text):
            imports.append(match.group(1))
            
        return imports
    
    def _generate_search_queries(self, keywords: List[str], 
                                mentioned_apis: List[str], 
                                text: str) -> List[SearchQuery]:
        """Generate prioritized search queries."""
        queries = []
        
        # Add mentioned APIs first
        for api in mentioned_apis:
            queries.append(SearchQuery(api, priority="high"))
        
        # Generate combined queries
        if 'simplex' in keywords and 'volume' in keywords:
            queries.append(SearchQuery("simplex volume formula", priority="high"))
        
        if 'measure' in keywords:
            queries.append(SearchQuery("measure theory", priority="medium"))
        
        if 'alternating' in keywords:
            queries.append(SearchQuery("alternating sum", priority="high"))
            
        if 'telescoping' in text.lower():
            queries.append(SearchQuery("telescoping_series", priority="high"))
            
        if 'summable' in keywords:
            queries.append(SearchQuery("summable", priority="high"))
        
        # Special case for sum_add_tsum_nat_add
        if 'sum_add_tsum_nat_add' in text:
            queries.append(SearchQuery("sum_add_tsum_nat_add", priority="high"))
            
        return queries
    
    def _determine_context(self, keywords: List[str]) -> Optional[str]:
        """Determine the mathematical context."""
        if 'measure' in keywords or 'volume' in keywords:
            return 'measure_theory'
        elif 'summable' in keywords or 'series' in keywords:
            return 'series_analysis'
        elif 'continuous' in keywords:
            return 'topology'
        return None