# trapple/skills

Personal collection of [Claude Code](https://github.com/anthropics/claude-code) skills, distributed as [APM (Agent Package Manager)](https://github.com/microsoft/apm) **subdirectory packages** — each top-level directory in this repo is an independently installable skill.

## Install

Install an individual skill (machine-wide / user-global, exposed to every Claude Code session):

```bash
apm install -g trapple/skills/<skill-name>
```

Project-local (writes to `./.claude/skills/` or `./.agents/skills/` in the current repo):

```bash
apm install trapple/skills/<skill-name>
```

Pin to a specific version:

```bash
apm install -g trapple/skills/<skill-name>#v0.1.0
```

Or add to a project's `apm.yml`:

```yaml
dependencies:
  apm:
    - trapple/skills/commit
    - trapple/skills/sync-skill
```

## Included skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| `commit` | `commit`, `コミット`, `コミットして` | Analyze conversation history to extract the **Why** behind the change, split into multiple commits when there are multiple Whys, and write a Conventional Commits style message. |
| `init-rules` | `init-rules`, `ルール導入`, `ルールテンプレート` | Copy bundled rule templates (Fail-Fast error handling, docs frontmatter policy, plan-mode output location, …) into the current project's `.claude/rules/`. Templates ship with the skill under `rules-templates/`. **Claude Code only** — relies on the `.claude/rules/` path-glob mechanism, which Codex / other agents (AGENTS.md-based) do not implement. |
| `codex` | `codex`, `Codex`, `Codexに聞いて`, `Codexで` | Thin wrapper that forwards the user's prompt to the OpenAI Codex CLI via `codex exec "$PROMPT" < /dev/null` (stdin must be closed or it hangs waiting for additional input). Requires the `codex` CLI on PATH. |
| `create-skill` | `スキル作って`, `Skill作って`, `create skill` | Meta-skill that scaffolds a new Claude Code skill at `~/.claude/skills/<name>/SKILL.md` (or `.claude/skills/<name>/SKILL.md` for project scope) with correct frontmatter. Explicitly distinguishes skills from legacy single-file commands. |
| `pbcopy` | `copy`, `コピー`, `コピーして` | Copy file contents or arbitrary text to the macOS clipboard via `pbcopy`, using heredocs to handle special characters safely. **macOS only** — `pbcopy` is not available on Linux/Windows. |
| `sync-skill` | `sync-skill`, `スキル同期`, `スキルインポート`, `スキル取り込み` | Import or update a skill from another project (`.claude/skills/`, `.apm/skills/`, or a sibling subdirectory package) into this repository's root, with automatic README table updates. Intended to be run from the `trapple/skills` repo root. |
| `cmux-read-screen` | proactive (dev logs / build output / errors) | Read the visible screen of an adjacent cmux pane via `cmux read-screen`. Useful for tailing dev server logs, build output, or terminal output in other panes without leaving the current Claude Code session. **Requires the cmux terminal multiplexer.** |
| `session-log` | `session log`, `セッションログ`, `生ログ見せて`, `経緯見せて` | Pretty-prints the raw JSONL session log at `~/.claude/projects/<proj>/<uuid>.jsonl` into a human-readable transcript (user / assistant / tool_use / tool_result). Supports `--session`, `--list`, `--full`, `--tools-only`, `--max-chars`. **Requires `jq`.** |
| `x-search` | `x_search`, `x-search`, `xサーチ`, `Xで検索`, `Xで調べて`, `X検索`, `ツイッターで調べて`, `Twitterで調べて`, `Grok で X を検索` | Search X (Twitter) via Grok using Hermes Agent's `tools.x_search_tool`, called directly from the locally-pinned `hermes-agent` venv (installed once with `uv tool install`, no repeated git fetches). Returns Markdown with footnote-style URL citations. **Requires `uv`, xAI OAuth (`hermes auth add xai-oauth`), and an X Premium subscription.** |
| `llm-wiki` | `LLM Wiki`, `Karpathy wiki`, `Vault に wiki`, `ingest`, `query`, `lint`, `Clippings を整理` | Implements Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern (LLM-maintained, persistent, append-only markdown wiki as a personal knowledge base) on top of an Obsidian vault. Covers three operations — **Ingest** (read raw sources into `pages/<genre>/sources/` and update related entity/concept pages via `[[wikilinks]]`), **Query** (manifest-based routing per query type: fact / lookup / compare / synthesis / source), and **Lint** (orphans / stale / missing / drift / frontmatter health) — plus an `.inetloc` shim for clickable Obsidian links in chat. **Requires an Obsidian vault at a fixed path (default `~/ObsidianVault/`); `.inetloc` link generation is macOS-only.** |

## Why use APM for skills?

APM provides supply-chain hygiene that the bare `.claude/skills/` directory does not:

- **Lockfile (`apm.lock.yaml`)** pins resolved versions with integrity hashes.
- **Unicode scanning** at install time detects hidden prompt-injection characters.
- **`apm audit`** rebuilds the agent context from scratch and diffs it against your working tree to surface drift.
- **`apm-policy.yml`** lets an org restrict which sources/scopes/primitives are allowed.

See [microsoft/apm](https://github.com/microsoft/apm) for details.

## License

[MIT](LICENSE)

---

## 日本語

Claude Code 向けに個人で作成したスキル集を、Microsoft の [APM (Agent Package Manager)](https://github.com/microsoft/apm) の **subdirectory package** パターンで配布するリポジトリです。各トップレベルディレクトリが独立したスキルパッケージとしてインストール可能です。

### インストール

個別スキルのインストール（マシン全体 / グローバル）:

```bash
apm install -g trapple/skills/<skill-name>
```

プロジェクトローカル（`./.claude/skills/` などに展開）:

```bash
apm install trapple/skills/<skill-name>
```

バージョン固定:

```bash
apm install -g trapple/skills/<skill-name>#v0.1.0
```

`apm.yml` に依存として追加:

```yaml
dependencies:
  apm:
    - trapple/skills/commit
    - trapple/skills/sync-skill
```

### 収録スキル

| スキル | トリガー | 概要 |
|-------|---------|------|
| `commit` | `commit` / `コミット` / `コミットして` | 会話履歴を遡って変更の **Why** を抽出し、Why が複数あればコミットを分割、Conventional Commits 形式のメッセージで自動コミットする。 |
| `init-rules` | `init-rules` / `ルール導入` / `ルールテンプレート` | スキルに同梱されたルールテンプレート（Fail-Fast エラーハンドリング、docs frontmatter 運用、plan モード出力先 など）をプロジェクトの `.claude/rules/` にコピーする。テンプレートは `rules-templates/` として skill ディレクトリに同梱。**Claude Code 専用** — `.claude/rules/` の path-glob 自動適用機構に依存しており、AGENTS.md ベースの Codex などでは効きません。 |
| `codex` | `codex` / `Codex` / `Codexに聞いて` / `Codexで` | ユーザーのプロンプトを OpenAI Codex CLI に転送する薄いラッパー。`codex exec "$PROMPT" < /dev/null` で stdin を閉じて呼ぶ（閉じないとハングする）。`codex` コマンドが PATH に必要。 |
| `create-skill` | `スキル作って` / `Skill作って` / `create skill` | 新しい Claude Code skill を `~/.claude/skills/<name>/SKILL.md`（またはプロジェクト側 `.claude/skills/<name>/SKILL.md`）に正しい frontmatter 付きで生成する meta skill。旧形式の単一ファイル command との混同を明示的に防ぐ。 |
| `pbcopy` | `copy` / `コピー` / `コピーして` | ファイル内容や任意のテキストを macOS の `pbcopy` でクリップボードにコピーする。特殊文字はヒアドキュメントで安全に扱う。**macOS 専用** — Linux/Windows では `pbcopy` が無い。 |
| `sync-skill` | `sync-skill` / `スキル同期` / `スキルインポート` / `スキル取り込み` | 別 PJ の `.claude/skills/` / `.apm/skills/` / リポジトリ直下のサブディレクトリパッケージにあるスキルを、本リポジトリのルート直下に取り込む / 更新する。同名スキルがあれば差分を提示して update、無ければ import。README の英語表・日本語表も自動で追記/更新する。**`trapple/skills` リポジトリのルートで実行する前提**。 |
| `cmux-read-screen` | 文脈トリガー（dev ログ / ビルド出力 / エラー調査） | cmux の隣ペインの画面内容を `cmux read-screen` で読み取る。タブ名指定 or 同一ワークスペース内から自動選択。dev サーバーのログ・ビルド出力・エラー調査に使う。**cmux ターミナルマルチプレクサが必要**。 |
| `session-log` | `session log` / `セッションログ` / `生ログ見せて` / `経緯見せて` | `~/.claude/projects/<proj>/<uuid>.jsonl` に保存された Claude Code の生セッションログを user / assistant / tool_use / tool_result に整形して人間が読める形で出力する。`--session` / `--list` / `--full` / `--tools-only` / `--max-chars` をサポート。**`jq` 必須**。 |
| `x-search` | `x_search` / `x-search` / `xサーチ` / `Xで検索` / `Xで調べて` / `X検索` / `ツイッターで調べて` / `Twitterで調べて` / `Grok で X を検索` | Hermes Agent の `tools.x_search_tool` を `uv tool install` でローカル固定した venv の Python から直接呼び出して X (Twitter) を Grok 検索する。脚注付き URL 引用入りの Markdown が返る (毎回 git fetch しない / ネットアクセスは初回インストール時のみ)。**`uv` / xAI OAuth (`hermes auth add xai-oauth`) / X Premium サブスクが必要**。 |
| `llm-wiki` | `LLM Wiki` / `Karpathy wiki` / `Vault に wiki` / `ingest` / `query` / `lint` / `Clippings を整理` | Karpathy の [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) パターン（LLM が維持する永続・追記型 markdown wiki を個人ナレッジベースにする手法）を Obsidian Vault 上で実装するスキル。**Ingest**（raw ソースを `pages/<genre>/sources/` に取り込み、関連 entity/concept ページを `[[wikilinks]]` で相互更新）/ **Query**（クエリ種別 fact / lookup / compare / synthesis / source ごとに経路分岐、manifest grep ベース）/ **Lint**（orphan / stale / missing / drift / frontmatter 健全性チェック）の 3 操作と、初期セットアップ・schema テンプレ・モデル切替/subagent パターンをカバー。チャット出力での `.inetloc` リンク変換も含む。**Obsidian Vault を固定パス（既定 `~/ObsidianVault/`）で運用する前提。`.inetloc` 生成は macOS 専用**。 |

### なぜ APM 経由なのか

`.claude/skills/` に直接ファイルを置くと、バージョン管理も改ざん検知もありません。APM は次を提供します。

- `apm.lock.yaml` による **integrity hash でのバージョン固定**
- インストール時の **隠し Unicode（プロンプトインジェクション）スキャン**
- `apm audit` による **配布元との差分検出**（ドリフト検出）
- `apm-policy.yml` で組織レベルの **許可ソース/スコープ/プリミティブの制御**

サプライチェーン攻撃が現実的なリスクになった今、`git clone` や手作業コピーよりも安全な配布チャネルです。

### ライセンス

[MIT](LICENSE)
