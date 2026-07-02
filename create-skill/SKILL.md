---
name: create-skill
description: Create a new Claude Code skill. Use when user says "スキル作って", "Skill作って", or "create skill"
argument-hint: "[skill-name]"
---

# スキル作成

ユーザーの要望に応じて新しいSkillを作成する。

## 重要: SkillとCommandは別物

- **Skill**: `~/.claude/skills/<name>/SKILL.md`（ディレクトリ構造）
- **Command**: `~/.claude/commands/<name>.md`（単一ファイル、旧形式）
- **絶対にCommandと間違えないこと**

## よくあるミス（厳禁）

- `.claude/skills/<name>.md` のように単一ファイルで作るのはNG → 必ず `<name>/SKILL.md` のディレクトリ構造にする
- ファイル名は `SKILL.md`（大文字）。`skill.md` は不可

## 配置場所

| スコープ | パス |
|---------|------|
| グローバル（個人用） | `~/.claude/skills/<name>/SKILL.md` |
| プロジェクト | `.claude/skills/<name>/SKILL.md` |

ユーザーが「グローバル」と言ったら `~/.claude/skills/` に、そうでなければプロジェクトの `.claude/skills/` に作成する。

## 手順

0. `$ARGUMENTS` が空の場合（文脈トリガー）は、会話の文脈からスキル名・内容を判断する。不足情報があればユーザーに聞く
1. `mkdir -p <配置パス>/<skill-name>`
2. `SKILL.md` を以下のフォーマットで作成:

```yaml
---
name: <skill-name>
description: <英語で書く。"Use when user says ..." 形式のトリガー文を含める。日本語トリガー語を混ぜてもOK>
---

# 本文（日本語でOK）

スキルの指示内容をここに書く
```

description の例:
- 発話トリガー: `Create a new Claude Code skill. Use when user says "スキル作って", "Skill作って", or "create skill"`
- 文脈トリガー（発話に頼らず文脈から自動起動させたい場合）: `Review a GitHub pull request. Use proactively when the user references a PR number, or triggered when the conversation context indicates a PR needs review.`
- 手動限定（`disable-model-invocation: true`）の場合: トリガー文は不要。用途を簡潔に英語で書くだけで良い（例: `Quickly grep files using Read and Grep. Manual invocation only.`）

skill 名はビルトイン（init, review, security-review 等）や既存 skill と被らないようにする。衝突しそうなら用途を絞った 2 語にする（例: `review` → `code-review`, `review-pr`）。

## Frontmatter オプション（すべて任意）

- `name`: スキル名（デフォルト: ディレクトリ名）
- `description`: 英語で記述。Claude自動実行の判断基準
- `disable-model-invocation: true`: ユーザー手動実行のみ（/name で呼ぶ）
- `user-invocable: false`: Claudeのみ自動実行（ユーザーは /name で呼べない）
- 使い分け: 手動限定→`disable-model-invocation: true` / Claude自動のみ→`user-invocable: false` / 両方許可（デフォルト）→どちらも付けない。両者は排他的で同時指定しない
- `allowed-tools`: 使用ツール制限。カンマ区切り文字列で書く（例: `"Read, Grep, Glob"`）
- `context: fork`: Subagentとして独立実行
- `agent`: context: fork時のAgent型（Explore, Plan, general-purpose）
- `argument-hint`: オートコンプリートで表示するヒント

## 引数

- `$ARGUMENTS`: 全引数
- `$0`, `$1`, `$2`...: 個別引数

## 動的コンテキスト

`` ！`コマンド` `` （`！`は全角表記。実際に使う際は半角 `!` に置き換える）でシェルコマンドの実行結果を注入可能。

**注意**: SKILL.md本文中でこの構文を説明目的で書く場合、半角 `!` を直接バッククォートの前に置くと、Claude Code側がコードスパンを無視してリテラルに動的コマンド実行として解釈し、`Shell command permission check failed` エラーを引き起こすことがある（Claude Code既知の挙動）。ドキュメント内で例示する際は必ず全角 `！` などでエスケープすること。
