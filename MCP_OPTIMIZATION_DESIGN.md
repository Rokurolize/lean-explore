# MCP Output Optimization Design Document

## 概要

lean-explore MCPサーバーの出力を最適化し、トークン使用量を82%削減する実装設計書。
現状: 10項目で約4,500トークン → 目標: 約800トークン

## 問題点

1. **重複情報**: `docstring`と`informal_description`が同じ内容（200-500トークン/項目）
2. **過剰な詳細**: 完全なLeanコード、アノテーション、改行を含む（100-300トークン/項目）
3. **無関係な結果**: quantum、telescope等のキーワードでpotion_problemに無関係な結果

## 実装設計

### 1. 環境変数の実装

#### 1.1 `LEAN_EXPLORE_OPTIMIZE` (bool)
**目的**: 最適化モードの有効/無効を制御

**実装箇所**: `src/lean_explore/mcp/tools.py`
```python
import os

# グローバル設定として読み込み
OPTIMIZE_MODE = os.environ.get('LEAN_EXPLORE_OPTIMIZE', 'false').lower() == 'true'
```

**影響箇所**:
- `_prepare_mcp_result_item()`関数で条件分岐
- 最適化時は`PotionOptimizedResult`を使用

#### 1.2 `LEAN_EXPLORE_DEFAULT_LIMIT` (int)
**目的**: デフォルトの検索結果数を制御

**実装箇所**: `src/lean_explore/mcp/tools.py`の`search()`関数
```python
@mcp_app.tool()
async def search(
    ctx: MCPContext,
    query: Union[str, List[str]],
    package_filters: Optional[List[str]] = None,
    limit: Optional[int] = None,  # Noneに変更
) -> List[Dict[str, Any]]:
    # 環境変数からデフォルト値を取得
    if limit is None:
        try:
            limit = int(os.environ.get('LEAN_EXPLORE_DEFAULT_LIMIT', '10'))
        except ValueError:
            limit = 10
    limit = max(1, min(limit, 100))  # 1-100の範囲に制限
```

#### 1.3 `LEAN_EXPLORE_EXCLUDE_KEYWORDS` (string)
**目的**: 検索結果から除外するキーワードを指定（カンマ区切り）

**実装箇所**: 新規関数を`tools.py`に追加
```python
def _get_exclude_keywords() -> List[str]:
    """環境変数から除外キーワードリストを取得"""
    keywords_str = os.environ.get('LEAN_EXPLORE_EXCLUDE_KEYWORDS', '')
    return [k.strip().lower() for k in keywords_str.split(',') if k.strip()]

def _should_exclude_result(item: APISearchResultItem, exclude_keywords: List[str]) -> bool:
    """結果を除外すべきか判定"""
    if not exclude_keywords:
        return False
    
    # チェック対象のテキストを結合
    text_to_check = ' '.join(filter(None, [
        item.primary_declaration.lean_name if item.primary_declaration else '',
        item.statement_text or '',
        item.docstring or '',
        item.informal_description or '',
        item.source_file or ''
    ])).lower()
    
    # いずれかのキーワードが含まれていれば除外
    return any(keyword in text_to_check for keyword in exclude_keywords)
```

### 2. 最適化実装

#### 2.1 `PotionOptimizedResult`クラスの完成

**ファイル**: `src/lean_explore/mcp/optimization.py`（既存を拡張）
```python
"""MCP output optimization for potion_problem efficiency."""

from typing import Optional, Dict, Any
from lean_explore.shared.models.api import APISearchResultItem

class PotionOptimizedResult:
    """Lightweight result format optimized for token efficiency."""
    
    def __init__(self, item: APISearchResultItem):
        self.id = item.id
        self.name = self._extract_name(item)
        self.sig = self._extract_signature(item.statement_text)
        self.hint = self._get_shortest_description(item)
        self.score = self._calculate_relevance(item)
    
    def _extract_name(self, item: APISearchResultItem) -> str:
        """Leanの名前を抽出"""
        if item.primary_declaration:
            return item.primary_declaration.lean_name
        return "Unknown"
    
    def _extract_signature(self, statement_text: Optional[str]) -> str:
        """型シグネチャのみを抽出（最大200文字）"""
        if not statement_text:
            return ""
        
        # 最初の行を取得
        first_line = statement_text.split('\n')[0]
        
        # @[...]アノテーションを除去
        if first_line.strip().startswith('@['):
            # アノテーション終了後の部分を取得
            parts = first_line.split(']', 1)
            if len(parts) > 1:
                first_line = parts[1].strip()
        
        # defやtheoremキーワードから開始
        for keyword in ['def ', 'theorem ', 'lemma ', 'class ', 'structure ']:
            if keyword in first_line:
                idx = first_line.find(keyword)
                first_line = first_line[idx:]
                break
        
        return first_line[:200]
    
    def _get_shortest_description(self, item: APISearchResultItem) -> Optional[str]:
        """最短の説明を取得（最大100文字）"""
        descriptions = [
            item.informal_description,
            item.docstring
        ]
        valid_descs = [d for d in descriptions if d]
        
        if not valid_descs:
            return None
        
        # 最短のものを選択
        shortest = min(valid_descs, key=len)
        
        # 100文字で切り詰め
        if len(shortest) > 100:
            return shortest[:97] + "..."
        return shortest
    
    def _calculate_relevance(self, item: APISearchResultItem) -> float:
        """potion_problemへの関連度を計算（0-1）"""
        # potion_problem関連キーワード
        potion_keywords = {
            "sum", "summable", "hassum", "tsum", "series", 
            "convergence", "limit", "factorial", "expectation", 
            "pmf", "probability", "continuous", "piecewise",
            "forward", "difference", "telescope", "finite"
        }
        
        # 除外すべきキーワード（高度な数学分野）
        exclude_keywords = {
            "quantum", "physics", "geometry", "galois", 
            "category", "topology", "algebraic", "scheme"
        }
        
        # テキストを結合して小文字化
        text = f"{item.primary_declaration.lean_name if item.primary_declaration else ''} {item.docstring or ''} {item.informal_description or ''}".lower()
        
        # 除外キーワードチェック
        for exclude in exclude_keywords:
            if exclude in text:
                return 0.0
        
        # 関連キーワードのマッチ数をカウント
        matches = sum(1 for kw in potion_keywords if kw in text)
        
        # 0-1の範囲に正規化（3つ以上マッチで最大値）
        return min(matches / 3.0, 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "id": self.id,
            "name": self.name,
            "sig": self.sig,
            "hint": self.hint,
            "score": round(self.score, 2)
        }
```

#### 2.2 tools.pyの修正

**修正箇所**: `_prepare_mcp_result_item()`関数
```python
def _prepare_mcp_result_item(
    backend_item: APISearchResultItem,
) -> Union[APISearchResultItem, Dict[str, Any]]:
    """バックエンドの結果をMCP用に準備"""
    
    # 最適化モードチェック
    if OPTIMIZE_MODE:
        # 最適化されたフォーマットを使用
        from lean_explore.mcp.optimization import PotionOptimizedResult
        optimized = PotionOptimizedResult(backend_item)
        
        # 関連度が低い場合はNoneを返す（フィルタリング）
        if optimized.score < 0.1:
            return None
            
        return optimized.to_dict()
    
    # 通常モード（既存の処理）
    # display_statement_textを除外
    backend_item_dict = backend_item.model_dump(
        exclude={"display_statement_text"}
    )
    return APISearchResultItem(**backend_item_dict)
```

**修正箇所**: `search()`関数
```python
@mcp_app.tool()
async def search(
    ctx: MCPContext,
    query: Union[str, List[str]],
    package_filters: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """検索ツール（最適化対応版）"""
    # デフォルトlimitの処理（上記参照）
    if limit is None:
        try:
            limit = int(os.environ.get('LEAN_EXPLORE_DEFAULT_LIMIT', '10'))
        except ValueError:
            limit = 10
    limit = max(1, min(limit, 100))
    
    # 除外キーワードの取得
    exclude_keywords = _get_exclude_keywords()
    
    # 既存の検索処理
    backend_service_instance = _get_backend_service(ctx)
    
    # ... (既存の検索ロジック)
    
    # 結果の準備
    mcp_results_list = []
    for backend_item in backend_results.results:
        # 除外キーワードチェック
        if _should_exclude_result(backend_item, exclude_keywords):
            continue
            
        # 最適化処理
        prepared_item = _prepare_mcp_result_item(backend_item)
        if prepared_item is not None:  # Noneは除外対象
            mcp_results_list.append(prepared_item)
    
    # limitを適用（除外後）
    mcp_results_list = mcp_results_list[:limit]
    
    return mcp_results_list
```

### 3. テスト計画

#### 3.1 環境変数のテスト
```bash
# テスト1: 最適化モード
export LEAN_EXPLORE_OPTIMIZE=true
export LEAN_EXPLORE_DEFAULT_LIMIT=5
export LEAN_EXPLORE_EXCLUDE_KEYWORDS="quantum,physics,telescope"

# MCPサーバー起動してsearchツールをテスト
```

#### 3.2 トークン削減の検証
```python
# テストスクリプト
def test_token_reduction():
    # 通常モードで検索
    normal_results = search("summable", limit=10)
    normal_tokens = count_tokens(normal_results)
    
    # 最適化モードで検索
    os.environ['LEAN_EXPLORE_OPTIMIZE'] = 'true'
    optimized_results = search("summable", limit=10)
    optimized_tokens = count_tokens(optimized_results)
    
    reduction = (normal_tokens - optimized_tokens) / normal_tokens * 100
    print(f"Token reduction: {reduction:.1f}%")
    assert reduction > 75  # 75%以上の削減を期待
```

### 4. 実装手順

1. **Phase 1**: 環境変数の読み込み実装
   - `LEAN_EXPLORE_DEFAULT_LIMIT`の実装（最も簡単）
   - テストで動作確認

2. **Phase 2**: 除外キーワード機能
   - `LEAN_EXPLORE_EXCLUDE_KEYWORDS`の実装
   - フィルタリング関数の追加
   - テストで動作確認

3. **Phase 3**: 最適化モード
   - `optimization.py`の完成
   - `LEAN_EXPLORE_OPTIMIZE`の実装
   - 統合テスト

### 5. 期待される効果

- **トークン削減**: 4,500 → 800トークン（82%削減）
- **関連性向上**: potion_problem無関係な結果を除外
- **柔軟性**: 環境変数で動的に制御可能

### 6. 後方互換性

- 環境変数が設定されていない場合は既存の動作を維持
- 最適化モードはオプトイン（明示的な有効化が必要）
- 既存のAPIインターフェースは変更なし

## 実装チェックリスト

- [ ] `tools.py`に環境変数読み込み追加
- [ ] `optimization.py`の完成
- [ ] 除外キーワードフィルタリング実装
- [ ] デフォルトlimit処理の実装
- [ ] 単体テストの作成
- [ ] 統合テストの実施
- [ ] ドキュメントの更新

この設計書に従って実装すれば、MCPサーバーの出力を大幅に最適化できます。