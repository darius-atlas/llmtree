# LLM Tree

**ドキュメント:** [🇺🇸 English](../README.md) | [🇷🇺 Русский](RU.md) | [🇩🇪 Deutsch](DE.md) | [🇯🇵 日本語](JA.md) | [🇨🇳 中文](CH.md)

LLM（大規模言語モデル）向けにプロジェクトデータを準備するためのCLIツールです。プロジェクトの構造とソースコードの内容を含むMarkdownファイルを生成します。

## インストール

```bash
pip install -e .
```

またはグローバルインストール：

```bash
pip install llmtree
```

## クイックスタート

```bash
# 現在のディレクトリを処理
llmtree .

# 特定のフォルダを処理
llmtree /path/to/project

# 特定のプロファイルを使用
llmtree . -p python

# プロファイルを設定
llmtree --config
```

## 主な機能

### プロファイル

* **default** – ほとんどのプロジェクトに対応する汎用プロファイル
* **python** – Pythonプロジェクト向けに最適化されたプロファイル
* 対話型メニューを通じてカスタムプロファイルの作成が可能

### 対話型操作

`llmtree .` を実行すると：

* **Enter**キー：`4llm.md` ファイルを生成
* \*\*Space（スペース）\*\*キー：設定メニューを開く

### プロファイル設定

* 含めるファイルのパターン
* 除外するファイルのパターン
* ディレクトリツリー構造の有無
* 最大ファイルサイズ
* 行番号の付加
* カスタムヘッダーとフッターの設定

## 設定構成

設定は `~/.llmtree/config.json` に保存されます：

```json
{
  "default": {
    "name": "default",
    "include_patterns": ["*.py", "*.js", "*.md"],
    "exclude_patterns": ["node_modules/*", ".git/*"],
    "include_tree": true,
    "max_file_size": 100000,
    "encoding": "utf-8",
    "add_line_numbers": false,
    "include_hidden": false,
    "tree_depth": 3,
    "custom_header": "",
    "custom_footer": ""
  }
}
```

## 使用例

### フロントエンド用プロファイルの作成

```bash
llmtree --config
# 「Create new profile」を選択
# 名前：frontend
# 含めるパターン：*.js,*.jsx,*.ts,*.tsx,*.vue,*.css,*.scss,package.json
# 除外パターン：node_modules/*,dist/*,build/*
```

### ドキュメント用プロファイル

```bash
llmtree --config
# "docs"という名前のプロファイルを作成
# 含めるパターン：*.md,*.rst,*.txt
# ツリー：あり
# 行番号：なし
```

## コマンドライン

```
usage: llmtree [-h] [-p PROFILE] [-o OUTPUT] [--config] [path]

位置引数:
  path                  対象ディレクトリパス（デフォルト：カレントディレクトリ）

オプション引数:
  -h, --help            ヘルプメッセージを表示して終了
  -p, --profile PROFILE 使用するプロファイル（デフォルト：default）
  -o, --output OUTPUT   出力ファイル名（デフォルト：4llm.md）
  --config              対話型設定を起動
```

## 出力形式

生成される `4llm.md` には以下が含まれます：

1. カスタムヘッダー（指定されていれば）
2. プロジェクト構造（tree形式）
3. ソースファイルの内容（構文ハイライト付き）
4. カスタムフッター（指定されていれば）

出力例：

```markdown
## プロジェクト構造

```

.
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test\_main.py
└── README.md

````

## ソースファイル

### src/main.py
```python
def main():
    print("Hello, World!")
````

### README.md

```markdown
# 私のプロジェクト
```

## ライセンス

MITライセンス
