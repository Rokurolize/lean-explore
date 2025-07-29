# LeanExplore-PotionAssist 開発者ガイド

## プロジェクト概要

このプロジェクトは、**LeanExplore**の特別版フォークで、**媚薬問題（Potion Problem）の形式証明**を支援するために特化してカスタマイズされています。

### 🎯 ミッション

1. **ハルシネーション防止**: 実在しないMathlib APIの使用を防ぐ
2. **効率的なAPI検索**: Sorry箇所に最適なAPIを迅速に発見
3. **リアルタイム支援**: MCP経由でpotion_problem側のClaude Codeを支援

### 📍 重要な理解

- **このディレクトリ**: `C:\Users\id374\mcp-tools\lean-explore-potionassist` (私の作業場所)
- **支援対象**: `C:\Users\id374\workspace\potion_problem` (別のClaude Codeが作業)
- **役割**: potion_problemの形式証明を支援する特殊ツールの開発・保守

## アーキテクチャ

### 🏗️ 特殊機能実装済み

```
src/lean_explore/potion_problem/
├── backend.py           # API DBとの統合バックエンド
├── enhanced_service.py  # ハイブリッド検索サービス
├── auto_solver.py      # 自動Sorry解決システム
├── service.py          # カスタムサービス
└── tools.py            # MCP追加ツール
```

### 🔧 主要コンポーネント

1. **PotionProblemBackend**
   - potion_problemのAPI DBと直接連携
   - 実在/非実在APIの判別機能
   - Sorry貢献度によるランキング

2. **EnhancedHybridService**
   - LeanExplore本体（60万件）+ potion_problem DBの並列検索
   - 真のAPI発見能力
   - エラーパターン学習機能

3. **SorryAutoSolver**
   - Sorry箇所の自動分析
   - 文脈ベースのAPI推薦
   - パターンマッチングによる候補絞り込み

## 開発ワークフロー

### 📋 日常タスク

1. **新機能追加時**:
   ```python
   # src/lean_explore/potion_problem/tools.py に追加
   @mcp_app.tool()
   async def check_api_exists(api_name: str, ctx: Context) -> bool:
       """APIの実在性を即座に確認"""
       # 実装
   ```

2. **エラーパターン登録**:
   ```python
   # enhanced_service.py のパターンDBに追加
   ERROR_PATTERNS = {
       "unknown identifier": ["API名のタイポ", "importが不足"],
       # 新パターン追加
   }
   ```

3. **Sorry解決支援強化**:
   ```python
   # auto_solver.py の探索アルゴリズム改良
   def enhanced_search(self, context):
       # より賢い探索ロジック
   ```

### 🎨 設計原則

1. **正確性優先**: ハルシネーションゼロを目指す
2. **高速応答**: MCPツールは100ms以内に応答
3. **文脈理解**: Sorry周辺のコード文脈を深く分析
4. **継続的学習**: 成功/失敗パターンをDBに蓄積

## ドメイン知識

### 🧮 媚薬問題（Potion Problem）について

- **目標**: E[τ] = e（オイラー数）の形式証明
- **手法**: Irwin-Hall分布、テレスコーピング級数
- **難関**: 高度な数学的証明をLean 4で完全形式化

### 📚 主要証明モジュール

```
PotionProblem/
├── Basic.lean                   # 基本定義
├── IrwinHallTheory.lean        # Irwin-Hall分布（主戦場）
├── ProbabilityFoundations.lean # 確率論基盤
├── SeriesAnalysis.lean         # 級数解析
└── FactorialSeries.lean        # 階乗級数
```

### 🎯 典型的なSorryパターン

1. **収束性証明**: `summable_*`, `hasSum_*`
2. **等式証明**: `tsum_eq_*`, `sum_eq_*`
3. **不等式証明**: `le_of_*`, `lt_of_*`
4. **極限証明**: `tendsto_*`, `lim_*`

## 技術スタック

- **Lean 4**: v4.21.0
- **Mathlib**: 最新版
- **Python**: 3.12+
- **MCP**: Model Context Protocol
- **データベース**: SQLite (API DB)
- **ベクトル検索**: FAISS

## よく使うコマンド

```bash
# MCP サーバー起動（ローカルモード）
uv run python -m lean_explore.mcp.server --backend local

# 自動ソルバー実行
uv run python run_auto_solver.py

# API DB更新
cd ../workspace/potion_problem/api_database
python migrate_apis.py

# テスト実行
uv run pytest tests/lean_explore/potion_problem/
```

## トラブルシューティング

### 🐛 よくある問題

1. **「API not found」エラー**
   - API DBが最新か確認
   - importパスが正しいか確認
   - 名前空間の違い（例: `Nat.` vs `ℕ.`）

2. **MCP接続エラー**
   - .mcp.jsonのパスが正しいか
   - sentence-transformersがインストールされているか

3. **Sorry解決の提案が的外れ**
   - コンテキスト窓を広げる
   - 関連定理の依存関係を確認

## 改善アイデア

### 🚀 今後の拡張案

1. **プロアクティブ支援**
   - Sorryを書いた瞬間に候補を表示
   - 証明の次ステップを予測

2. **学習機能強化**
   - 成功した証明パターンを自動学習
   - ユーザーの証明スタイルに適応

3. **可視化ツール**
   - 証明の依存関係グラフ
   - API使用頻度ヒートマップ

4. **バッチ処理**
   - 複数Sorryの一括解決
   - 証明の自動リファクタリング

## リソース

- [Mathlib Docs](https://leanprover-community.github.io/mathlib4_docs/)
- [Lean 4 Manual](https://leanprover.github.io/lean4/doc/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [媚薬問題の数学的背景](https://x.com/suamax_scp/status/1942902598203322849)

---

**Remember**: 私たちの目標は、potion_problem側のClaude Codeが**迷わず、間違えず、効率的に**形式証明を完成できるよう支援することです。

> 「正しいAPIを、正しいタイミングで、正しい使い方と共に提供する」

それが、LeanExplore-PotionAssistの使命です。