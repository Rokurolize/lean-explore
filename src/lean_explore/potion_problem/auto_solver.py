#!/usr/bin/env python3
"""
Automated Sorry Elimination Solver for Potion Problem
=====================================================

A simple, deterministic approach to automatically explore APIs for sorry elimination.
No machine learning - just systematic search with pruning based on:
1. Curated API knowledge from potion_problem database
2. Pattern matching from successful eliminations
3. Simple heuristics for branch pruning
"""

import re
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

from lean_explore.potion_problem.backend import PotionProblemBackend
from lean_explore.potion_problem.service import HybridService
from lean_explore.potion_problem.config import get_potion_config


@dataclass
class Sorry:
    """Represents a sorry in the codebase."""
    module: str
    line: int
    context: str
    surrounding_code: List[str]
    mentioned_apis: List[str]
    mathematical_concepts: List[str]


@dataclass
class SearchPath:
    """Represents a search path for API exploration."""
    sorry: Sorry
    tried_apis: Set[str]
    successful_patterns: List[str]
    current_score: float
    depth: int


class SorryAutoSolver:
    """Automated sorry elimination through systematic API exploration."""
    
    def __init__(self, potion_problem_path: Optional[str] = None):
        # Use config manager if no path provided
        if potion_problem_path is None:
            config = get_potion_config()
            self.potion_path = config.workspace_path
            self.backend = PotionProblemBackend(config)
        else:
            self.potion_path = Path(potion_problem_path)
            # Create custom config for provided path
            from lean_explore.potion_problem.backend import PotionProblemConfig
            config = PotionProblemConfig(
                api_database_path=self.potion_path / 'api_database' / 'mathlib_apis.db',
                workspace_path=self.potion_path
            )
            self.backend = PotionProblemBackend(config)
        
        self.service = HybridService()
        
        # Pattern knowledge base
        self.successful_patterns = self._load_successful_patterns()
        
        # Search limits
        self.max_depth = 5
        self.max_apis_per_sorry = 50
        self.min_score_threshold = 0.1
    
    def _load_successful_patterns(self) -> Dict[str, List[str]]:
        """Load patterns from successful sorry eliminations."""
        patterns = defaultdict(list)
        
        # Extract from verified-apis.md
        verified_path = self.potion_path / 'docs' / 'api-reference' / 'verified-apis.md'
        if verified_path.exists():
            content = verified_path.read_text()
            # Simple pattern extraction
            for match in re.finditer(r'### For `(\w+)`.*?```lean\n(.*?)```', content, re.DOTALL):
                sorry_type = match.group(1)
                code_pattern = match.group(2)
                patterns[sorry_type].append(code_pattern)
        
        # Common successful patterns from experience
        patterns['telescoping'].extend([
            'Finset.sum_congr rfl',
            'Finset.sum_sub_distrib',
            'pmf_telescoping'
        ])
        
        patterns['tail_probability'].extend([
            'Summable.sum_add_tsum_nat_add',
            'tsum_subtype_add_tsum_subtype_compl',
            'Set.indicator'
        ])
        
        patterns['convergence'].extend([
            'FloorSemiring.tendsto_pow_div_factorial_atTop',
            'hasSum_iff_tendsto_nat_of_nonneg',
            'Tendsto.comp'
        ])
        
        return dict(patterns)
    
    def extract_sorry_info(self, file_path: Path, line_num: int) -> Sorry:
        """Extract detailed information about a sorry."""
        lines = file_path.read_text().splitlines()
        
        # Convert to 0-based index
        line_idx = line_num - 1
        
        # Get surrounding context (20 lines before and after for better analysis)
        start = max(0, line_idx - 20)
        end = min(len(lines), line_idx + 20)
        surrounding = lines[start:end]
        
        # Extract mentioned APIs from comments
        mentioned_apis = []
        for i in range(max(0, line_idx - 15), min(len(lines), line_idx + 5)):
            if i < len(lines) and '--' in lines[i]:
                comment = lines[i].split('--', 1)[1]
                # Look for API-like patterns
                apis = re.findall(r'[A-Z]\w*(?:\.\w+)+', comment)
                mentioned_apis.extend(apis)
        
        # Extract mathematical concepts
        concepts = self._extract_concepts(surrounding)
        
        return Sorry(
            module=file_path.stem,
            line=line_num,
            context=lines[line_idx] if 0 <= line_idx < len(lines) else "",
            surrounding_code=surrounding,
            mentioned_apis=list(set(mentioned_apis)),
            mathematical_concepts=concepts
        )
    
    def _extract_concepts(self, code_lines: List[str]) -> List[str]:
        """Extract mathematical concepts from code."""
        concepts = []
        
        concept_patterns = {
            'summability': r'[Ss]ummable',
            'convergence': r'[Tt]endsto|[Cc]onverg',
            'factorial': r'factorial',
            'telescoping': r'telescop',
            'probability': r'pmf|PMF|probability',
            'continuous': r'[Cc]ontinuous',
            'derivative': r'derivative|deriv',
            'finite_difference': r'fwdDiff|forward.*diff|finite.*diff',
            'alternating': r'alternating',
            'binomial': r'binomial|choose',
            'spline': r'spline|B-spline',
            'positivity': r'positiv',
            'sum': r'\bsum\b',
            'frontier': r'frontier',
            'indicator': r'indicator'
        }
        
        code_text = '\n'.join(code_lines)
        for concept, pattern in concept_patterns.items():
            if re.search(pattern, code_text):
                concepts.append(concept)
        
        return concepts
    
    def generate_search_queries(self, sorry: Sorry) -> List[Tuple[str, float]]:
        """Generate prioritized search queries for a sorry."""
        queries = []
        
        # High priority: Mentioned APIs
        for api in sorry.mentioned_apis:
            queries.append((api, 1.0))
        
        # Medium priority: Mathematical concepts
        for concept in sorry.mathematical_concepts:
            queries.append((concept, 0.7))
        
        # Pattern-based queries
        for concept in sorry.mathematical_concepts:
            if concept in self.successful_patterns:
                for pattern in self.successful_patterns[concept][:3]:
                    queries.append((pattern, 0.8))
        
        # Context-based queries
        if 'tail' in sorry.context.lower():
            queries.extend([
                ('tail probability', 0.6),
                ('complement sum', 0.6),
                ('tsum_subtype', 0.5)
            ])
        
        if 'continuous' in sorry.context.lower():
            queries.extend([
                ('piecewise continuous', 0.6),
                ('frontier agreement', 0.5),
                ('continuousOn', 0.5)
            ])
        
        # Sort by priority
        queries.sort(key=lambda x: x[1], reverse=True)
        return queries
    
    def score_api(self, api_name: str, sorry: Sorry) -> float:
        """Score an API's relevance to a sorry."""
        score = 0.0
        
        # Check contribution level from database
        try:
            conn = sqlite3.connect(str(self.backend.config.api_database_path))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT contribution_level 
                FROM sorry_contributions 
                WHERE api_name = ? AND module = ?
            """, (api_name, sorry.module))
            result = cursor.fetchone()
            if result:
                score += result[0] / 10.0  # Normalize to 0-1
            conn.close()
        except:
            pass
        
        # Pattern matching score
        api_lower = api_name.lower()
        for concept in sorry.mathematical_concepts:
            if concept.lower() in api_lower:
                score += 0.3
        
        # Direct mention bonus
        if api_name in sorry.mentioned_apis:
            score += 0.5
        
        return min(score, 1.0)
    
    def explore_api_tree(self, sorry: Sorry, max_results: int = 10) -> List[Dict]:
        """Explore API tree for a sorry using depth-first search with pruning."""
        results = []
        visited = set()
        
        # Initialize search paths
        initial_queries = self.generate_search_queries(sorry)
        search_queue = []
        
        for query, priority in initial_queries[:5]:  # Start with top 5
            path = SearchPath(
                sorry=sorry,
                tried_apis=set(),
                successful_patterns=[],
                current_score=priority,
                depth=0
            )
            search_queue.append((priority, query, path))
        
        while search_queue and len(results) < max_results:
            # Get highest priority search
            search_queue.sort(key=lambda x: x[0], reverse=True)
            priority, query, path = search_queue.pop(0)
            
            # Skip if score too low
            if priority < self.min_score_threshold:
                continue
            
            # Skip if too deep
            if path.depth > self.max_depth:
                continue
            
            # Search for APIs
            response = self.service.search(query, limit=10)
            
            for result in response.results:
                if not result.primary_declaration:
                    continue
                
                api_name = result.primary_declaration.lean_name
                
                # Skip if already tried
                if api_name in visited or api_name in path.tried_apis:
                    continue
                
                visited.add(api_name)
                
                # Score the API
                api_score = self.score_api(api_name, sorry)
                
                # Get usage info
                usage = self.service.get_api_usage(api_name)
                
                # Add to results if promising
                if api_score > 0.3:
                    results.append({
                        'api_name': api_name,
                        'score': api_score,
                        'search_path': [query],
                        'usage': usage,
                        'import': getattr(result.primary_declaration, 'filepath', '') or result.source_file or ''
                    })
                
                # Generate follow-up searches for promising APIs
                if api_score > 0.5 and path.depth < self.max_depth - 1:
                    # Look for related APIs
                    related_queries = self._generate_related_queries(api_name, sorry)
                    for rel_query, rel_priority in related_queries[:3]:
                        new_path = SearchPath(
                            sorry=sorry,
                            tried_apis=path.tried_apis | {api_name},
                            successful_patterns=path.successful_patterns + [api_name],
                            current_score=api_score * rel_priority,
                            depth=path.depth + 1
                        )
                        search_queue.append((api_score * rel_priority, rel_query, new_path))
        
        # Sort results by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def _generate_related_queries(self, api_name: str, sorry: Sorry) -> List[Tuple[str, float]]:
        """Generate queries for APIs related to a successful one."""
        queries = []
        
        # Extract module and base name
        parts = api_name.split('.')
        if len(parts) > 1:
            module = parts[0]
            base = parts[-1]
            
            # Look for variants
            queries.append((f"{module}.{base}", 0.8))
            queries.append((f"{module}", 0.6))
            
            # Common suffixes/prefixes
            for suffix in ['_eq', '_iff', '_of', '_at']:
                queries.append((f"{base}{suffix}", 0.5))
            
            for prefix in ['summable_', 'continuous_', 'tendsto_']:
                if base.lower().startswith(prefix[:-1]):
                    queries.append((f"{prefix}", 0.5))
        
        return queries
    
    def solve_sorry(self, file_path: Path, line_num: int) -> Dict:
        """Attempt to automatically solve a sorry."""
        print(f"\n🔍 Analyzing sorry at {file_path.name}:{line_num}")
        
        # Extract sorry information
        sorry = self.extract_sorry_info(file_path, line_num)
        print(f"  Module: {sorry.module}")
        print(f"  Concepts: {', '.join(sorry.mathematical_concepts)}")
        if sorry.mentioned_apis:
            print(f"  Mentioned APIs: {', '.join(sorry.mentioned_apis[:3])}")
        
        # Explore API tree
        print("\n🌳 Exploring API tree...")
        results = self.explore_api_tree(sorry, max_results=15)
        
        # Format results
        solution = {
            'sorry_location': f"{file_path.name}:{line_num}",
            'mathematical_concepts': sorry.mathematical_concepts,
            'top_candidates': []
        }
        
        print(f"\n✨ Found {len(results)} candidate APIs:")
        for i, result in enumerate(results[:10]):
            print(f"\n  {i+1}. {result['api_name']} (score: {result['score']:.2f})")
            print(f"     Import: {result['import']}")
            if result['usage'].get('usage_example'):
                print(f"     Example: {result['usage']['usage_example'][:100]}...")
            
            solution['top_candidates'].append({
                'api': result['api_name'],
                'score': result['score'],
                'import': result['import'],
                'usage': result['usage'].get('usage_example', '')
            })
        
        return solution
    
    def batch_solve(self, sorries: List[Tuple[Path, int]]) -> List[Dict]:
        """Solve multiple sorries in batch."""
        solutions = []
        
        print(f"🚀 Starting batch solution for {len(sorries)} sorries\n")
        
        for file_path, line_num in sorries:
            solution = self.solve_sorry(file_path, line_num)
            solutions.append(solution)
            print("\n" + "="*60 + "\n")
        
        return solutions


def demo():
    """Demo the auto solver on remaining sorries."""
    # Use config-based path
    solver = SorryAutoSolver()
    potion_path = solver.potion_path
    
    # Remaining sorries from IrwinHallTheory.lean
    remaining_sorries = [
        (potion_path / "PotionProblem" / "IrwinHallTheory.lean", 174),
        (potion_path / "PotionProblem" / "IrwinHallTheory.lean", 204),
        (potion_path / "PotionProblem" / "IrwinHallTheory.lean", 229),
        (potion_path / "PotionProblem" / "IrwinHallTheory.lean", 273)
    ]
    
    # Solve them
    solutions = solver.batch_solve(remaining_sorries[:2])  # Start with first 2
    
    # Save results
    import json
    output_path = Path("sorry_solutions.json")
    with open(output_path, 'w') as f:
        json.dump(solutions, f, indent=2)
    
    print(f"\n💾 Solutions saved to {output_path}")
    print("\n📊 Summary:")
    for solution in solutions:
        print(f"\n  {solution['sorry_location']}:")
        if solution['top_candidates']:
            top = solution['top_candidates'][0]
            print(f"    Best candidate: {top['api']} (score: {top['score']:.2f})")


if __name__ == "__main__":
    demo()