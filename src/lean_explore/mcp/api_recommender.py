"""
API Recommendation Engine based on patterns and learning.

TDD: Minimal implementation to pass tests.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class APIRecommendation:
    """A recommended API with relevance score."""
    api_name: str
    relevance_score: float
    confidence: float = 0.5
    reason: Optional[str] = None


class APIRecommendationEngine:
    """Recommends APIs based on patterns and learned resolutions."""
    
    def __init__(self):
        # Known patterns for API recommendations
        self.patterns = {
            'factorial_reciprocal': {
                'keywords': ['factorial', 'reciprocal', 'sum'],
                'apis': [
                    ('Complex.sum_div_factorial_le', 0.9),
                    ('NormedSpace.expSeries_div_hasSum_exp', 0.85)
                ]
            },
            'summable_reindex': {
                'keywords': ['summable', 'reindex', 'shift', 'index'],
                'apis': [
                    ('Summable.sum_add_tsum_nat_add', 0.95)
                ]
            }
        }
        
        # Learned patterns from successful resolutions
        self.learned_patterns = []
    
    def recommend(self, keywords: List[str], pattern: Optional[str] = None) -> List[APIRecommendation]:
        """Recommend APIs based on keywords and patterns."""
        recommendations = []
        
        # Check learned patterns first
        for learned in self.learned_patterns:
            if self._matches_pattern(keywords, learned['keywords']):
                recommendations.append(
                    APIRecommendation(
                        api_name=learned['successful_api'],
                        relevance_score=0.95,
                        confidence=0.95,
                        reason="Learned from successful resolution"
                    )
                )
        
        # Check known patterns
        if pattern and '1 / n.factorial' in pattern:
            # Factorial pattern detected
            for api, score in self.patterns['factorial_reciprocal']['apis']:
                recommendations.append(
                    APIRecommendation(
                        api_name=api,
                        relevance_score=score,
                        confidence=0.8,
                        reason="Factorial reciprocal pattern"
                    )
                )
        
        # Check for summable patterns
        if any(kw in keywords for kw in ['summable', 'reindex', 'shift']):
            for api, score in self.patterns['summable_reindex']['apis']:
                recommendations.append(
                    APIRecommendation(
                        api_name=api,
                        relevance_score=score,
                        confidence=0.85,
                        reason="Summable reindexing pattern"
                    )
                )
        
        # Check for series convergence patterns
        if any(kw in keywords for kw in ['series', 'convergence']):
            recommendations.append(
                APIRecommendation(
                    api_name="HasSum.tsum_eq",
                    relevance_score=0.7,
                    confidence=0.7,
                    reason="Series convergence pattern"
                )
            )
        
        # Sort by relevance score
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # If no recommendations yet, return a default
        if not recommendations and keywords:
            recommendations.append(
                APIRecommendation(
                    api_name="search_required",
                    relevance_score=0.1,
                    confidence=0.1,
                    reason="No pattern match found"
                )
            )
        
        return recommendations
    
    def learn_pattern(self, resolution: Dict[str, Any]) -> None:
        """Learn from a successful sorry resolution."""
        # Extract pattern information
        pattern = {
            'keywords': resolution.get('keywords', []),
            'successful_api': resolution.get('successful_api'),
            'context': resolution.get('sorry_context', '')
        }
        
        # Add to learned patterns
        self.learned_patterns.append(pattern)
        
        # Update confidence for future recommendations
        # In a real implementation, this would be more sophisticated
        
    def _matches_pattern(self, keywords: List[str], pattern_keywords: List[str]) -> bool:
        """Check if keywords match a pattern."""
        # Simple implementation: at least 2 keywords match
        matches = sum(1 for kw in keywords if kw in pattern_keywords)
        return matches >= 2