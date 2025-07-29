#!/usr/bin/env python3
"""
Run the automated sorry solver on Potion Problem
================================================

Simple command-line interface for the auto solver.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from lean_explore.potion_problem.auto_solver import SorryAutoSolver
from lean_explore.potion_problem.config import get_potion_config


def main():
    """Run auto solver with simple output."""
    print("🤖 Potion Problem 自動Sorry解決システム")
    print("=" * 50)
    print("単純な探索アルゴリズムでAPIを自動探索します")
    print("機械学習は使用せず、パターンマッチングと枝刈りのみ")
    print("=" * 50)
    
    # Initialize solver using config
    solver = SorryAutoSolver()
    potion_path = solver.potion_path
    
    if not potion_path.exists():
        print(f"❌ エラー: {potion_path} が見つかりません")
        print(f"💡 ヒント: 環境変数 POTION_PROBLEM_PATH を設定するか、.env ファイルを作成してください")
        return
    
    # Get remaining sorries
    remaining_sorries = [
        (potion_path / "PotionProblem" / "IrwinHallTheory.lean", 174),
        (potion_path / "PotionProblem" / "IrwinHallTheory.lean", 204),
        (potion_path / "PotionProblem" / "IrwinHallTheory.lean", 229),
        (potion_path / "PotionProblem" / "IrwinHallTheory.lean", 273)
    ]
    
    print(f"\n🎯 {len(remaining_sorries)}個のsorryを解析します\n")
    
    # Process each sorry
    for i, (file_path, line_num) in enumerate(remaining_sorries):
        print(f"\n{'='*60}")
        print(f"Sorry {i+1}/{len(remaining_sorries)}: {file_path.name}:{line_num}")
        print('='*60)
        
        try:
            solution = solver.solve_sorry(file_path, line_num)
            
            # Show top 3 recommendations
            print("\n📋 推奨API (上位3個):")
            for j, candidate in enumerate(solution['top_candidates'][:3]):
                print(f"\n  {j+1}. {candidate['api']}")
                print(f"     スコア: {'★' * int(candidate['score'] * 5)}")
                print(f"     Import: {candidate['import']}")
                if candidate['usage']:
                    print(f"     使用例:")
                    print(f"       {candidate['usage'][:150]}...")
        
        except Exception as e:
            print(f"❌ エラー: {e}")
    
    print("\n\n✅ 自動探索完了!")
    print("\n💡 ヒント:")
    print("  - スコアが高いAPIから順に試してください")
    print("  - 使用例を参考に実装してください") 
    print("  - 必要に応じて関連APIも探索してください")


if __name__ == "__main__":
    main()