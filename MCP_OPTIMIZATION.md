# MCP Server 最適化ガイド

## 問題の分析

初期の接続時間: **10-11秒**

### ボトルネックの内訳

1. **uv起動オーバーヘッド** (~1-2秒)
   - `uv run` コマンドによるPython環境のセットアップ

2. **重い初期化処理** (~8-9秒)
   - SentenceTransformerモデルのロード (~3-4秒)
   - FAISSインデックスのロード (~2-3秒)
   - SQLiteデータベース接続 (~0.5秒)
   - その他の初期化 (~2秒)

## 実装した最適化

### 1. 遅延読み込み (Lazy Loading)

`fast_server.py`で実装した`LazyLocalService`により、MCPサーバーは即座に起動し、実際にツールが使用されるまで重い初期化を遅延させます。

**メリット:**
- MCP接続は即座に完了 (<1秒)
- 初回のツール使用時に初期化（バックグラウンド）

### 2. キャッシュローダー

`cached_loader.py`でシングルトンパターンを使用し、モデルとインデックスを一度だけロードします。

### 3. プリロードオプション

`--pre-warm`フラグで、サーバー起動後にバックグラウンドで初期化を実行できます。

## 使用方法

### 方法1: 高速起動サーバーを使用

```bash
# .mcp-fast.jsonを使用
claude --mcp-config .mcp-fast.json
```

### 方法2: 手動でプリロード

```bash
# 事前にアセットをロード
uv run python scripts/preload_mcp.py

# その後通常通り起動
claude
```

### 方法3: 既存の設定を更新

`.mcp.json`を編集して高速サーバーを使用:

```json
{
  "mcpServers": {
    "lean-explore": {
      "command": "C:\\\\users\\\\id374\\\\.local\\\\bin\\\\uv.EXE",
      "args": [
        "run",
        "--project",
        "C:\\\\Users\\\\id374\\\\workspace\\\\lean-explore-potionassist",
        "python",
        "-m",
        "lean_explore.mcp.fast_server",
        "--backend",
        "lazy-local"
      ],
      "env": {}
    }
  }
}
```

## パフォーマンス改善

- **初期接続時間**: 10-11秒 → **<1秒**
- **初回ツール使用**: 通常通り（初期化が発生）
- **2回目以降**: 高速（既に初期化済み）

## さらなる最適化案

1. **永続的なサーバープロセス**
   - MCPサーバーをシステムサービスとして常駐させる
   - systemdやWindows Serviceとして実装

2. **モデルの軽量化**
   - より小さいembeddingモデルの使用
   - 量子化やディスティレーション

3. **インデックスの最適化**
   - FAISSインデックスの圧縮
   - 部分的なインデックスロード

4. **並列初期化**
   - 各コンポーネントを並列で初期化
   - asyncioを活用した非同期初期化