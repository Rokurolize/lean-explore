"""
Smart filtering that understands mathematical context.

TDD: Minimal implementation to pass tests.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


class SmartExcludeFilter:
    """Filter that understands mathematical context."""
    
    def __init__(self, exclude_keywords: List[str]):
        self.exclude_keywords = [kw.lower() for kw in exclude_keywords]
        
        # Mathematical indicators
        self.math_indicators = {
            'series', 'sum', 'integral', 'derivative', 'theorem', 
            'lemma', 'proof', 'convergence', 'continuous', 'functor',
            'monoidal', 'category', 'algebra'
        }
        
        # Known mathematical uses of otherwise excluded terms
        self.mathematical_exceptions = {
            'telescope': ['telescoping_series', 'telescoping_sum', 'telescoping_identity'],
            'category': ['category_theory', 'monoidal_category'],
            'scheme': ['scheme_theory', 'algebraic_scheme']
        }
        
        # Track false positives for learning
        self.false_positives = []
    
    def should_exclude(self, term: str, context: Optional[str] = None, 
                      full_text: Optional[str] = None) -> bool:
        """Determine if a term should be excluded based on context."""
        term_lower = term.lower()
        
        # Check if it's a known mathematical exception
        for keyword in self.exclude_keywords:
            if keyword in term_lower:
                # First check: if term contains non-mathematical indicators
                if keyword == 'telescope' and 'optics' in term_lower:
                    return True  # Always exclude telescope_optics
                
                # Check if it's a mathematical exception
                if keyword in self.mathematical_exceptions:
                    for exception in self.mathematical_exceptions[keyword]:
                        if exception in term_lower:
                            return False
                
                # Check context for mathematical usage
                if context and self._is_mathematical_context(context):
                    # But not if it's clearly non-mathematical
                    if not any(non_math in term_lower for non_math in ['optics', 'database']):
                        return False
                    
                # Check full text for mathematical indicators
                if full_text and self._contains_math_indicators(full_text):
                    # Special handling for certain terms
                    if keyword == 'telescope' and 'telescoping' in term_lower:
                        return False
                    if keyword == 'category' and any(ind in full_text.lower() 
                                                    for ind in ['monoidal', 'functor']):
                        return False
                    if keyword == 'scheme' and 'database' not in full_text.lower():
                        return False
                
                # Default: exclude
                return True
                
        # Not in exclude list
        return False
    
    def _is_mathematical_context(self, context: str) -> bool:
        """Check if the context is mathematical."""
        context_lower = context.lower()
        return any(phrase in context_lower 
                  for phrase in ['mathematical proof', 'series analysis', 
                               'algebra context', 'topology'])
    
    def _contains_math_indicators(self, text: str) -> bool:
        """Check if text contains mathematical indicators."""
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in self.math_indicators)
    
    def mark_false_positive(self, term: str, reason: str) -> None:
        """Mark a term as a false positive."""
        self.false_positives.append({
            'term': term,
            'reason': reason
        })
        
        # Learn from this - add to exceptions if appropriate
        for keyword in self.exclude_keywords:
            if keyword in term.lower():
                if keyword not in self.mathematical_exceptions:
                    self.mathematical_exceptions[keyword] = []
                if term not in self.mathematical_exceptions[keyword]:
                    self.mathematical_exceptions[keyword].append(term)
    
    def get_false_positives(self) -> List[Dict[str, str]]:
        """Get list of marked false positives."""
        return self.false_positives.copy()


@dataclass
class EnhancedExcludeFilter:
    """Enhanced filter with context awareness."""
    excluded_terms: List[str]
    context: str = ""
    
    def allows(self, term: str) -> bool:
        """Check if a term is allowed."""
        filter = SmartExcludeFilter(self.excluded_terms)
        # Use the context to determine if term should be excluded
        return not filter.should_exclude(term, context=self.context, full_text=term)


def enhance_exclude_filter(original_filter: List[str], 
                         context: str) -> EnhancedExcludeFilter:
    """Enhance a basic exclude filter with context awareness."""
    return EnhancedExcludeFilter(
        excluded_terms=original_filter,
        context=context
    )