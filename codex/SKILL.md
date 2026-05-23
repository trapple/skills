---
name: codex
description: OpenAI Codexにプロンプトを投げて結果を返す。Use when user says "codex", "Codex", "Codexに聞いて", or "Codexで"
---

# codex - OpenAI Codex実行

ユーザーのプロンプトをOpenAI Codex CLIに投げて結果を返す。

## 前提

- ローカルに OpenAI Codex CLI (`codex` コマンド) がインストール済みであること

## 手順

1. ユーザーの入力（argsまたは会話の文脈）からプロンプトを取得する
2. 以下のコマンドを実行する:

```bash
codex exec "$PROMPT" < /dev/null
```

**重要**: 必ず `< /dev/null` で stdin を閉じること。
`codex exec` は stdin がパイプ接続状態だと「追加入力を待つ」モードに入り、
`Reading additional input from stdin...` で永久にハングする。
Claude Code の Bash ツール環境では stdin がパイプ扱いになるため、
明示的に閉じないと必ずスタックする。

3. 実行結果をそのままユーザーに返す
