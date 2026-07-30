---
name: herdr-fork-popup
description: Fork the current Claude Code session into a Herdr session-modal popup terminal (80% x 80%) via `claude --fork-session`. Like herdr-fork but opens a floating popup instead of splitting the tiled layout. Only works inside Herdr (HERDR_ENV=1) with the bundled plugin linked. Use when user says "herdr-fork-popup", "popupでフォーク", "ポップアップでフォーク", "フォークをポップアップで", or wants to branch the current Claude session into a floating Herdr popup.
---

# herdr-fork-popup

現在の Claude Code セッションを、herdr の**セッションモーダルなポップアップ** (80%×80%) にフォークする。herdr-fork のポップアップ版で、タイルレイアウトを一切変更しない。フォーク先は履歴を全部引き継いだ新しいセッションIDで起動し、元セッションは変更されない。

セッションID解決ロジックは [miyagawa 氏の herdr-fork.sh](https://gist.github.com/miyagawa/cb1a9f6c8695d1219efba0c66d5f78f7) 由来。

## 実行方法

```
bash ~/.claude/skills/herdr-fork-popup/herdr-fork-popup.sh
```

- 成功すると `forked session <sid> -> popup (80% x 80%)` が出力され、画面中央にポップアップで claude が起動する
- サイズは同梱プラグインのマニフェスト (`plugin/herdr-plugin.toml`) の `width`/`height` で変更できる

## 仕組み

herdr の popup は CLI から直接開けず**プラグインペインとしてのみ**開けるため、`[[panes]]` で `placement = "popup"` を宣言した最小プラグイン (`trapple.herdr-fork-popup`) を同梱している。ラッパースクリプトがセッションIDを解決し、`herdr plugin pane open --plugin trapple.herdr-fork-popup --entrypoint fork --env CLAUDE_FORK_SID=... --env CLAUDE_FORK_CWD=...` で popup を開く。popup 内では `fork-popup.sh` が cwd を移して `claude --resume <sid> --fork-session` を exec する。

## 前提 (初回のみ)

同梱プラグインのリンクが必要:

```
herdr plugin link ~/.claude/skills/herdr-fork-popup/plugin
```

- herdr 管理下 (`HERDR_ENV=1`) で実行すること
- `python3` が必要 (セッションID解決の JSON 解析)

## popup の性質 (注意)

- **セッションモーダル**: 開いている間は Escape を含む全ターミナル入力を popup が受け取る。閉じるには popup 内の claude を終了する (`/exit` 等)
- **セッションに1つだけ**: すでに popup が開いていると開けない
- Settings・コピーモード・他のモーダルが開いていると `ui_busy` エラーになる
- popup は herdr ペインではない (pane id を持たず、レイアウト・永続化・エージェント API に参加しない)。長く並行作業したい場合はペイン分割版の herdr-fork を使う

## エラー対処

- **`no reachable Herdr server`**: herdr サーバーに接続できない (herdr 外での実行等)。ガードは `HERDR_ENV` ではなくサーバー到達性で判定する (herdr キーバインドの shell には `HERDR_ENV` が渡らないため)
- **`could not resolve the focused Claude session`**: `CLAUDE_CODE_SESSION_ID` が無く、フォーカス中のエージェントも Claude ではない
- **`plugin not found` 系**: 前提のプラグインリンク未実行。上記 `herdr plugin link` を案内
- **`ui_busy`**: 別のモーダル (Settings / コピーモード / 既存 popup) が開いている。閉じてから再実行
- **popup 内に「claude exited with status N」**: フォーク起動自体の失敗。表示されたエラーを確認し Enter で閉じる
