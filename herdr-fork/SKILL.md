---
name: herdr-fork
description: Fork the current Claude Code session into a new Herdr pane via `claude --fork-session` (runs bundled herdr-fork.sh). The fork inherits the full conversation history under a new session ID; the original session is untouched. Only works inside Herdr (HERDR_ENV=1). Use when user says "herdr-fork", "セッションフォーク", "セッションをフォークして", "このセッションを分岐", "別ペインでフォーク", or wants to branch the current Claude Code session into a parallel Herdr pane.
---

# herdr-fork

現在の Claude Code セッションを、herdr の新しいペインにフォークする。フォーク先は会話履歴を全部引き継いだ**新しいセッションID**で起動し (`claude --resume <sid> --fork-session`)、元のセッションは変更されない。

出典: https://gist.github.com/miyagawa/cb1a9f6c8695d1219efba0c66d5f78f7 (miyagawa氏の herdr-fork.sh を同梱)

## 実行方法

```
bash ~/.claude/skills/herdr-fork/herdr-fork.sh [direction]
```

- `direction`: `right` (デフォルト) / `down` / `tab`。右に分割・下に分割・新しいタブで開く (`tab` は gist からの独自拡張)
- 成功すると `forked session <sid> -> pane <pane_id>` が出力される

## 前提

- **herdr 管理下のペインで動いていること** (`HERDR_ENV=1`)。それ以外では即エラー終了する
- `python3` が必要 (JSON 解析に使用)
- フォーク対象のセッションIDは `CLAUDE_CODE_SESSION_ID` から取る。未設定の場合は、現在フォーカスされている herdr の Claude エージェントのセッションIDにフォールバックする

## 使いどころ

- 今の会話の文脈を保ったまま、別の作業 (別案の検討・危険な実験・並行調査) を隣のペインで進めたいとき
- フォーク先で何をしても元セッションには影響しない

## エラー対処

- **`no reachable Herdr server`**: herdr サーバーに接続できない (herdr 外での実行等)。ガードは `HERDR_ENV` ではなくサーバー到達性で判定する (herdr キーバインドの shell には `HERDR_ENV` が渡らないため gist から変更)
- **`could not resolve the focused Claude session`**: `CLAUDE_CODE_SESSION_ID` が無く、フォーカス中の herdr エージェントも Claude ではない。フォークしたい Claude ペインにフォーカスして実行するか、環境変数を設定する
- **`direction must be 'right', 'down' or 'tab'`**: 引数の指定ミス
