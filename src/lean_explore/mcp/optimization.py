"""MCP output optimization for potion_problem efficiency."""

from typing import Optional, Dict, Any
from lean_explore.shared.models.api import APISearchResultItem


class PotionOptimizedResult:
    """Lightweight result format for potion_problem."""
    def __init__(self, item: APISearchResultItem):
        self.id = item.id
        self.name = self._extract_name(item)
        self.sig = self._extract_signature(item.statement_text)
        self.hint = self._get_shortest_description(item)
        self.score = self._calculate_relevance(item)
    
    def _extract_name(self, item: APISearchResultItem) -> str:
        """Extract Lean name from item."""
        if item.primary_declaration:
            return item.primary_declaration.lean_name
        return "Unknown"
    
    def _extract_signature(self, statement_text: Optional[str]) -> str:
        """Extract only the type signature (max 200 chars)."""
        if not statement_text:
            return ""
        
        # Get first line
        first_line = statement_text.split('\n')[0]
        
        # Remove @[...] annotations
        if first_line.strip().startswith('@['):
            parts = first_line.split(']', 1)
            if len(parts) > 1:
                first_line = parts[1].strip()
        
        # Start from def/theorem/lemma/class/structure keyword
        for keyword in ['def ', 'theorem ', 'lemma ', 'class ', 'structure ']:
            if keyword in first_line:
                idx = first_line.find(keyword)
                first_line = first_line[idx:]
                break
        
        return first_line[:200]
    
    def _get_shortest_description(self, item: APISearchResultItem) -> Optional[str]:
        """Get shortest description (max 100 chars)."""
        descriptions = [
            item.informal_description,
            item.docstring
        ]
        valid_descs = [d for d in descriptions if d]
        
        if not valid_descs:
            return None
        
        # Choose shortest
        shortest = min(valid_descs, key=len)
        
        # Truncate to 100 chars
        if len(shortest) > 100:
            return shortest[:97] + "..."
        return shortest
    
    def _calculate_relevance(self, item: APISearchResultItem) -> float:
        """Calculate relevance to potion_problem (0-1)."""
        # Keywords relevant to potion_problem
        potion_keywords = {
            "sum", "summable", "hassum", "tsum", "series", 
            "convergence", "limit", "factorial", "expectation", 
            "pmf", "probability", "continuous", "piecewise",
            "forward", "difference", "telescope", "finite"
        }
        
        # Keywords to exclude (advanced math topics)
        exclude_keywords = {
            "quantum", "physics", "geometry", "galois", 
            "category", "topology", "algebraic", "scheme"
        }
        
        # Combine text fields
        text = f"{item.primary_declaration.lean_name if item.primary_declaration else ''} {item.docstring or ''} {item.informal_description or ''}".lower()
        
        # Check exclusions
        for exclude in exclude_keywords:
            if exclude in text:
                return 0.0
        
        # Count keyword matches
        matches = sum(1 for kw in potion_keywords if kw in text)
        
        # Normalize to 0-1 (3+ matches = max score)
        return min(matches / 3.0, 1.0)


    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "sig": self.sig,
            "hint": self.hint,
            "score": round(self.score, 2)
        }