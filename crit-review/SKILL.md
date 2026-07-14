---
name: crit-review
description: Have an LLM reviewer (user-selected model) review files and publish findings as crit inline comments, then open the crit UI. Use when user says "○○をレビューして", "AIレビュー", "LLMレビュー", "crit-review", or asks for an LLM review of specific files.
argument-hint: "[@file | file ...]"
---

# crit-review - LLM レビューを crit コメントとして出力

選択したモデル（LLM）にファイルをレビューさせ、その指摘を crit のインラインコメントとして投稿し、crit UI でユーザーが閲覧・返信できるようにする。

## 既存 crit スキルとの役割分担

- `/crit`（公式スキル）: **人間**がレビュアー。エージェントの成果物に人間がコメントする
- このスキル: **LLM がレビュアー**（逆方向）。LLM のレビュー結果を crit コメントとして人間に見せる

## 前提

- `crit` CLI がインストール済みであること（`brew install crit`）
- Codex を選択する場合は `codex` CLI も必要

## Step 1: 対象ファイルの特定

1. `$ARGUMENTS` からファイルパスを取得する。`@` プレフィックス付き（例: `/crit-review @src/foo.ts`）は `@` を除去してパスとして解釈する。複数指定可
2. 引数が空なら会話文脈からレビュー対象を特定する
3. 対象ファイルの存在を確認する。特定できなければユーザーに聞く

## Step 2: レビュー方法の確認（AskUserQuestion 1回の呼び出しで2問）

- Q1「どのモデルにレビューさせますか？」
  - Fable 5 (Recommended) → subagent `model: fable`
  - Opus 4.8 → subagent `model: opus`
  - Sonnet 5 → subagent `model: sonnet`
  - Codex → subagent を使わず `codex exec` を直接実行
- Q2「レビュー結果を crit で表示しますか？」
  - crit を使う (Recommended) → コメント投稿 + UI 起動（Step 4a）
  - チャットに出力 → crit を使わない（Step 4b）

## Step 3: レビュー実行

レビュアーには次の出力形式を指示する（crit の bulk JSON スキーマ準拠）:

```json
[
  {"body": "<レビュー全体のサマリ>", "scope": "review"},
  {"file": "<path>", "line": 42, "body": "<指摘>"},
  {"file": "<path>", "line": "45-47", "body": "<指摘>"}
]
```

- 行番号は**ディスク上のファイルの 1-indexed 行番号**（diff の行番号ではない）
- `file` は**リポジトリルートからの相対パス**（絶対パスは `crit comment` が `path must be relative and within the repository` で拒否する。実測確認済み）
- `body` は日本語で、指摘の理由と修正案を含める

レビュアー（subagent / codex）には絶対パスを Read させてよいが、JSON の `file` は相対パスで返させるか、投稿前に自分で相対パスへ変換する。

### Claude 系モデルの場合

Agent tool で fresh subagent を起動する:

- `subagent_type: general-purpose`、`model` は選択値（`fable` / `opus` / `sonnet`）
- プロンプトに含める内容:
  - 対象ファイルの**絶対パス**（subagent に Read させる。ファイル内容は貼らない）
  - レビュー観点: 正しさ / 明瞭さ / 設計 / セキュリティ / パフォーマンス（ユーザーが観点を指定していればそれを優先）
  - 最終出力は上記 JSON 配列**のみ**を返すこと（前置き・コードフェンス外の説明は不要）

### Codex の場合

```bash
codex exec "$PROMPT" < /dev/null
```

**必ず `< /dev/null` で stdin を閉じること**（閉じないと追加入力待ちで永久にハングする）。プロンプトには対象ファイルの絶対パスと上記 JSON 形式の指示を含め、出力から JSON 部分をパースする。

## Step 4a: crit を使う場合

**必ず「UI 起動 → コメント投稿」の順で行うこと。** file モードの `crit <file>` は git ブランチレビューとは**別の専用セッション**（独自の review file）を作るため、先に headless で投稿したコメントは UI に表示されない。daemon 稼働中の `crit comment` は実行中セッションに自動接続され、UI に live reload で反映される（実測確認済み）。

1. crit UI を起動する。`run_in_background: true` で:

```bash
crit <file...>
```

起動直後に出力される URL をそのままユーザーに提示する:

> 「Crit を http://localhost:\<port\> で開きました。\<モデル名\> のレビューコメントを確認し、返信を残して Finish Review を押してください」

2. レビュー結果 JSON を scratchpad の一時ファイルに Write する（複数行 body が JSON 内にあるため、stdin パイプは使わず必ず `--file` で渡す）
3. 一括投稿する。`--author` には**レビュアーのモデル名**を渡す（例: 'Fable 5' / 'Opus 4.8' / 'Sonnet 5' / 'Codex'）:

```bash
crit comment --json --file <tmpfile> --author '<モデル名>'
```

4. **Finish Review まで待機する**。バックグラウンドタスクの完了通知が来たら stdout の未解決コメント・返信を読み取り:
   - ユーザーが同意・依頼した指摘は対象ファイルを Edit で修正する
   - 対応内容を返信する: `crit comment --reply-to <id> --author 'Claude Code' '<対応内容>'`
   - **`--resolve` は付けない**（解決判断はユーザーのもの。明示的に頼まれた場合のみ）

## Step 4b: crit を使わない場合

レビュー結果を `file:line` 参照つきでチャットに整形して出力する（サマリ → 指摘一覧の順）。

## 注意（footgun）

- **`crit <file>` に `--no-open` を付けない**: crit 0.17.1 では `--no-open` 付きだと daemon が起動直後にクラッシュする（`could not reach daemon: connection reset by peer`、実測確認済み）。ブラウザは自動で開かせる
- **`crit comment --help` を実行しない**: ヘルプ表示ではなく body="--help" のレビューコメント投稿として解釈される（実測確認済み）。ヘルプは `crit --help` で見る
- コメント body をシェル引数で直接渡すときは single-quote を使う（backtick やシェルメタ文字対策）。複数エントリは必ず `--json --file`
