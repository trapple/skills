---
name: x-search
description: xAI 公式 CLI「Grok Build」(`grok` コマンド) のサーバーサイド x_search ツールをヘッドレスモードで呼び出して X (Twitter) を Grok で検索する。Grok による検索結果分析が Markdown (脚注付き URL 引用) で返る。Use when user says "x_search", "x-search", "xサーチ", "Xで検索", "Xで調べて", "X検索", "ツイッターで調べて", "Twitterで調べて", "Grok で X を検索", or asks to look up trending posts / sentiment / discussions on X.
---

# x-search

X (Twitter) を Grok 経由で検索するスキル。xAI 公式 CLI「Grok Build」(`grok`) をヘッドレスモード (`-p`) で起動し、サーバーサイドの `x_search` hosted tool に検索させる。以前の hermes-agent 版を置き換えたもの (Python venv 不要、認証も `grok login` 1回のみ)。

## 前提 (ユーザー側で1度だけ手動実行が必要)

以下が未実行の場合、まずユーザーに案内すること。スキル内では自動化しない (ブラウザ操作・グローバル副作用を伴うため)。

1. **grok CLI のインストール**:
   ```
   curl -fsSL https://x.ai/cli/install.sh | bash
   ```
   更新は `grok update`。
2. **ログイン (xAI サブスクリプションの OAuth)**:
   ```
   grok login               # ブラウザが開く
   grok login --device-code # リモート (SSH) / ブラウザレス環境
   ```
   認証情報は `~/.grok/` にグローバル保存され、全プロジェクト共通 (hermes 時代の HERMES_HOME ごとの分裂は無い)。

## 実行方法

Bash で以下を実行する。クエリは自然文 (日本語/英語どちらでも可)。

```
grok -p "<クエリ>。組み込みの X 検索 (x_search) を直接使って X (Twitter) を検索し、代表的なポストの URL 引用を含む Markdown で回答して。前置きは不要" \
  --tools "" --always-approve --max-turns 8
```

- 既定 (`--output-format plain`) では応答 Markdown がそのまま stdout に出る
- 生 JSON (usage / sessionId / stopReason 等) が欲しい場合は `--output-format json` を付ける。応答本文は `.text`

### フラグの意味 (省略禁止)

- `--tools ""`: ローカルツール (シェル実行・ファイル編集等) を全封鎖する。**grok は `~/.claude/` の CLAUDE.md やスキルを読み込むため、これが無いと `--always-approve` 下で他スキルのコマンドを勝手にシェル実行しうる** (実際に発生を確認済み)。`x_search` はサーバーサイド実行なので封鎖の影響を受けない
- `--always-approve`: ツール実行の自動承認。無いとヘッドレスでは承認が取れず `stopReason: "Cancelled"` で検索前に終了する
- `--max-turns 8`: 暴走防止の上限

## Bash 実行時の注意

- **タイムアウト**: 1〜2 分かかる。Bash 呼び出し時の `timeout` は **300000 (5分)** 程度を指定すること
- **クエリのクオート**: シェルに渡すクエリは必ず `"..."` でクオートする (空白・記号・日本語のため)

## 出力の扱い方

- 返ってくる Markdown には `[[N]](https://x.com/...)` 形式の脚注付き URL 引用が含まれる。**そのままユーザーへの回答に含めて構わない** (参照性が高い)
- ユーザーが「生データが欲しい」と言った場合は `--output-format json` で JSON を取得して整形する
- ユーザーが「元ポストの実テキストが欲しい」と言った場合はクエリ自体に「該当ポストの本文も引用して返答してください」等を含める

## エラー対処

- **`Not signed in`**: `grok login` の実行を案内 (ブラウザ認証)。リモートなら `grok login --device-code`
- **`grok: command not found`**: 前提セットアップ未完了。インストールコマンドを案内
- **`stopReason: "Cancelled"` / 検索せず終了**: `--always-approve` の付け忘れ
- **応答が「Hermes / スキルで検索します」等と回り道する**: `--tools ""` が付いていれば実害は無い (最終的に内蔵 x_search で検索される)。プロンプト内の「組み込みの X 検索 (x_search) を直接使って」の指示を削らないこと

## 制約

- これは Grok による検索結果の**分析**であって、X の検索 API そのものではない。生ツイートの完全な一覧は得られない
- Grok の知識カットオフ・解釈バイアスが乗る
- grok CLI は更新が速く、フラグの挙動がバージョンで変わりうる (検証済みバージョン: 0.2.102)
