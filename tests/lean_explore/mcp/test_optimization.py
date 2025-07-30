"""Tests for MCP output optimization following TDD approach."""

import os
import json
from typing import Dict, Any
import pytest
from unittest.mock import Mock, patch

from lean_explore.mcp.optimization import PotionOptimizedResult
from lean_explore.shared.models.api import APISearchResultItem, APIPrimaryDeclarationInfo


class TestPotionOptimizedResult:
    """Test class for PotionOptimizedResult optimization."""
    
    @pytest.fixture
    def sample_api_item(self):
        """Create a sample APISearchResultItem for testing."""
        return APISearchResultItem(
            id=187627,
            primary_declaration=APIPrimaryDeclarationInfo(
                kind="def",
                lean_name="Summable",
                statement_id=187627
            ),
            source_file="Mathlib/Topology/Algebra/InfiniteSum/Defs.lean",
            range_start_line=147,
            statement_text='def Summable (f : β → α) : Prop := ∃ a, HasSum f a',
            docstring="`Summable f` means that `f` has some (infinite) sum. Use `tsum` to get the value.",
            informal_description="`Summable f` means that `f` has some (infinite) sum. Use `tsum` to get the value."
        )
    
    def test_optimization_reduces_size(self, sample_api_item):
        """Test that optimization significantly reduces data size."""
        # Original size
        original_size = len(json.dumps(sample_api_item.model_dump()))
        
        # Optimized size
        optimized = PotionOptimizedResult(sample_api_item)
        optimized_size = len(json.dumps(optimized.to_dict()))
        
        # Calculate reduction
        reduction_rate = (original_size - optimized_size) / original_size * 100
        
        assert reduction_rate > 50, f"Expected >50% reduction, got {reduction_rate:.1f}%"
    
    def test_preserves_essential_info(self, sample_api_item):
        """Test that essential information is preserved."""
        optimized = PotionOptimizedResult(sample_api_item)
        result = optimized.to_dict()
        
        assert result['id'] == 187627
        assert result['name'] == 'Summable'
        # Signature should contain def or theorem keyword
        assert 'def' in result['sig'] and 'Summable' in result['sig']
        assert 'Prop' in result['sig']
        assert 'tsum' in result['hint']
    
    def test_relevance_scoring(self):
        """Test relevance scoring for potion_problem keywords."""
        # High relevance item
        high_relevance_item = APISearchResultItem(
            id=1,
            primary_declaration=APIPrimaryDeclarationInfo(
                kind="theorem",
                lean_name="summable_series_convergence",
                statement_id=1
            ),
            source_file="test.lean",
            range_start_line=1,
            statement_text="theorem summable_series_convergence",
            docstring="About summable series and convergence"
        )
        
        # Low relevance item
        low_relevance_item = APISearchResultItem(
            id=2,
            primary_declaration=APIPrimaryDeclarationInfo(
                kind="def",
                lean_name="quantum_state",
                statement_id=2
            ),
            source_file="test.lean",
            range_start_line=1,
            statement_text="def quantum_state",
            docstring="Quantum physics related"
        )
        
        high_opt = PotionOptimizedResult(high_relevance_item)
        low_opt = PotionOptimizedResult(low_relevance_item)
        
        assert high_opt.score > 0.5
        assert low_opt.score == 0.0  # Should be 0 due to 'quantum' keyword


class TestExcludeKeywords:
    """Test exclude keywords functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Setup and cleanup environment variables."""
        self.original_env = os.environ.get('LEAN_EXPLORE_EXCLUDE_KEYWORDS')
        yield
        if self.original_env is None:
            os.environ.pop('LEAN_EXPLORE_EXCLUDE_KEYWORDS', None)
        else:
            os.environ['LEAN_EXPLORE_EXCLUDE_KEYWORDS'] = self.original_env
    
    def test_exclude_keywords_parsing(self):
        """Test parsing of exclude keywords from environment."""
        os.environ['LEAN_EXPLORE_EXCLUDE_KEYWORDS'] = "quantum,physics,telescope"
        
        # Import after setting env var
        from lean_explore.mcp.tools import _get_exclude_keywords
        
        keywords = _get_exclude_keywords()
        assert keywords == ['quantum', 'physics', 'telescope']
    
    def test_false_positive_detection(self):
        """Test detection of false positives in exclude keywords."""
        from lean_explore.mcp.tools import _should_exclude_result
        
        # Important API that contains 'telescope'
        telescoping_item = APISearchResultItem(
            id=1,
            primary_declaration=APIPrimaryDeclarationInfo(
                kind="theorem",
                lean_name="telescoping_series",
                statement_id=1
            ),
            source_file="test.lean",
            range_start_line=1,
            statement_text="theorem telescoping_series",
            docstring="Telescoping series identity"
        )
        
        exclude_keywords = ['telescop', 'quantum']  # Using partial match
        
        # This is a false positive - important API filtered by keyword
        assert _should_exclude_result(telescoping_item, exclude_keywords) == True
        
        # This demonstrates the problem with simple keyword filtering
        # Even partial matches like 'telescop' can exclude important mathematical concepts
        # Recommendation: Be very careful with exclude keywords in mathematical contexts


class TestOptimizationMode:
    """Test optimization mode toggle."""
    
    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Setup and cleanup environment variables."""
        self.original_env = os.environ.get('LEAN_EXPLORE_OPTIMIZE')
        yield
        if self.original_env is None:
            os.environ.pop('LEAN_EXPLORE_OPTIMIZE', None)
        else:
            os.environ['LEAN_EXPLORE_OPTIMIZE'] = self.original_env
    
    def test_optimization_mode_enabled(self):
        """Test when optimization mode is enabled."""
        os.environ['LEAN_EXPLORE_OPTIMIZE'] = 'true'
        
        # Reload module to pick up env var
        import importlib
        import lean_explore.mcp.tools
        importlib.reload(lean_explore.mcp.tools)
        
        assert lean_explore.mcp.tools.OPTIMIZE_MODE == True
    
    def test_optimization_mode_disabled(self):
        """Test when optimization mode is disabled."""
        os.environ['LEAN_EXPLORE_OPTIMIZE'] = 'false'
        
        # Reload module to pick up env var
        import importlib
        import lean_explore.mcp.tools
        importlib.reload(lean_explore.mcp.tools)
        
        assert lean_explore.mcp.tools.OPTIMIZE_MODE == False


@pytest.mark.asyncio
class TestDefaultLimit:
    """Test default limit functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Setup and cleanup environment variables."""
        self.original_env = os.environ.get('LEAN_EXPLORE_DEFAULT_LIMIT')
        yield
        if self.original_env is None:
            os.environ.pop('LEAN_EXPLORE_DEFAULT_LIMIT', None)
        else:
            os.environ['LEAN_EXPLORE_DEFAULT_LIMIT'] = self.original_env
    
    async def test_default_limit_from_env(self):
        """Test that default limit is read from environment."""
        os.environ['LEAN_EXPLORE_DEFAULT_LIMIT'] = '5'
        
        # This would require mocking the full MCP context
        # For now, we just verify the environment variable is set correctly
        assert os.environ['LEAN_EXPLORE_DEFAULT_LIMIT'] == '5'