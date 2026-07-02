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
| `refactor-doc` | Manual only | Refactor an existing doc file against project conventions (frontmatter / prefix / placement / structure). Spawns parallel sub-agents for content review, placement, quality / frontmatter checks, and plan-vs-implementation drift detection. Preserves the original facts; trims redundancy and stale implementation details. **Project-conventions aware** — expects a `docs/` tree with `analysis_` / `plan_` / `strategy_` prefixes and YAML frontmatter (`作成日` / `最終更新` / `ステータス`). |
| `user-journey` | `要件確認`, `ジャーニー検索`, `user_journey`, `ユーザージャーニー`, `○○の要件は`, `○○の方針は`, `user-journey`; proactive (design / impl start) | A keyword-searchable knowledge base of a project's current user-journey / requirements / constraints, kept as short one-liners in a SQLite DB. Search before designing or implementing to stay consistent with what the user currently expects; write only with explicit permission. **UPDATE-by-default** (the journey row is the current state, not a history log — git history covers the audit trail), with a 4-choice flow when a new rule conflicts with an existing record. **Requires the `sqlite3` CLI; assumes a project-local `data/user_journey.db`.** |
| `cmux-update-check` | `cmux update`, `cmuxアップデート`, `cmuxの更新確認`, `cmuxを更新`, `cmuxのリリースノート` | Compares the installed cmux version against the latest GitHub release and lists the per-version changes (notes / breaking changes / new features) in between. Prefers the `gh` CLI for release data, falling back to WebFetch. **Requires the `cmux` CLI on PATH; `gh` CLI recommended to avoid GitHub rate limits.** |
| `brainstorming` | `ブレスト`, `設計したい`, `作りたい`, `brainstorm`, `設計`; proactive (start of non-trivial implementation work) | Force a requirements → design dialogue before any implementation. Fixes "what to build" and "acceptance criteria", writes a design doc, picks an implementation style (4 combinations of isolation × parallelism), then commits the spec on a fresh branch/worktree before handing off to `writing-plans`. **Never commits to main / default branch directly.** |
| `writing-plans` | `プラン書いて`, `実装計画`, `writing plans`, `plan を作って`; proactive (after `brainstorming` approves a spec) | Turn a spec / requirements into a zero-context-engineer-executable implementation plan. Decomposes work into bite-size TDD steps (write failing test → confirm fail → minimal impl → confirm pass → commit), locks the file structure decision (1 file 1 responsibility) before task decomposition, and writes Global Constraints in three required subsections (Spec-derived / PJ permanent rules / Operational premise). Saved to `.claude/plans/YYYY-MM-DD-<feature-name>.md`, then handed off to `subagent-driven-development` or serial implementation. When invoked without `brainstorming`, prompts the user for the 4-way implementation style (isolation × parallelism). |
| `subagent-driven-development` | `subagent driven`, `SDD`, `subagent 駆動`, `plan を消化`, `plan を実行` | Execute a `writing-plans` plan inside the current session by dispatching a fresh implementer subagent per task, gating each with a task reviewer (spec compliance + code quality), and running one whole-branch reviewer at the end. Each subagent receives only the context the controller selects (no session-history pollution), keeping both the implementer focused and the controller's coordination context preserved. Persists progress to `.claude/sdd/progress.md` so a compaction-killed session can resume without re-dispatching completed tasks; passes briefs / reports / diffs as files instead of pasting into prompts. Includes a pre-flight gate that batches plan ↔ review-rule conflicts and downstream-prereq misses into a single user question before Task 1 dispatch. |
| `parallel-dispatch` | `並列`, `並列で`, `parallel`, `parallel-dispatch`; proactive (multiple unrelated investigations / fixes) | Thin variant for fanning N independent problem domains out to fresh subagents by stacking multiple `Agent` tool calls in a single assistant response (1 response = parallel, 1-response-1-call = sequential), then integrating the results. Covers when to use vs avoid (independent vs related failures, shared state, agent interference), an Agent-prompt mandatory-fields checklist split by mode — (a) implementation mode (fix through green) and (b) investigation mode (root cause only, no production-code changes) — with explicit fields for touch / NG files, 1-hop read range default, expected return shape, scope-narrowed test command, and a "no-expectation-degradation" clause. For 2-stage implement + review use `subagent-driven-development` instead. |
| `using-git-worktrees` | `worktree`, `並行開発`, `並列実装`, `隔離環境`, `using-git-worktrees` | Ensure an isolated workspace exists before starting feature work. Detect-existing-isolation first → prefer the platform's native worktree tool (cmux / `EnterWorktree` / `/worktree`) → fall back to `git worktree add` under `.claude/worktrees/`, committing the `.gitignore` entry first. Then runs project setup (auto-detects pnpm / yarn / bun / npm / uv / pip / bundle / cargo / go) and a baseline test so the worktree starts in a known-clean state. |
| `test-driven-development` | `TDD`, `テスト駆動`, `test driven`, `テスト先行`; proactive (any feature / bugfix / refactor before writing implementation code) | Force the test-first cycle: failing test → observe failure → minimum implementation → observe pass → refactor. Includes a **"RED が観測できなかったときの判別フロー"** that splits immediate-pass into A-1 existing-behavior duplicate / A-2 earlier-cycle preempt (kept as regression coverage) / A-3 accidentally-passing — A-3a *negation injection* and A-3b *counterfactual injection* (temporary suppress wrapper) for forced-break observation; plus Pattern C `ERR_MODULE_NOT_FOUND` "empty stub" exception to the Iron Law and Pattern D-1 / D-2 split for runner-crash-as-valid-RED. Iron Law's delete clause is explicitly scoped to *newly added* production code (existing bug fix is failing-test → minimal patch). Empirically tuned (3-iter `empirical-prompt-tuning` loop, 3 scenarios, accuracy stabilized at 100%). Bundled `testing-anti-patterns.md` covers 5 mock anti-patterns + DI pattern with explicit gates. |
| `install-skills` | `install-skills`, `スキル導入`, `skill install`, `スキル入れて`, `apm スキル` | Interactively browse an APM skills repository (defaults to `trapple/skills`), with each skill annotated by install-status badges (`global` / `local` / `both` / `manual` / `—`) and cross-repo same-name conflicts surfaced as a separate warning block. Selection is a chat reply (`foo bar` / `all` / `cancel`); install destination (`global` / `local`) is asked once via AskUserQuestion (skippable with `--global` / `--local`); then `apm install` runs the lot. Pin-point install / version pinning / uninstall / update are out of scope (use `apm` directly). On manual selection of a `manual`-status skill (= already physically present in `~/.claude/skills/` outside APM), the install is refused and the user is told to `rm -rf` first to avoid overwrite conflicts. **Requires the `apm` CLI; `gh` CLI optional (fallback fetch when the target repo has no local clone under `~/repos`).** |
| `fable5-prompt-tuning` | `Fable5向けに最適化`, `Fable 5 prompting`, `fable5チューニング`, `このプロンプトをFable5向けに直して` | Diagnose an instruction document (system prompt / skill `SKILL.md` / `CLAUDE.md` / agent prompt) against Claude Fable 5's known behavioral differences from Opus 4.8, and propose concrete before/after edits rather than reciting the source doc. Checklist covers effort-level guidance, trimming over-enumerated steps into brief steering instructions, grounding long-run progress claims in tool evidence, explicit action boundaries, async parallel-subagent delegation, a lessons-learned memory system, avoiding early-stopping/context-anxiety failure modes, giving the *why* behind requests, keeping final summaries readable, auditing for reasoning-echo instructions that trigger `reasoning_extraction` refusals, and adding a send-to-user tool for long async runs. Bundled `patterns.md` holds the verbatim reusable instruction snippets from Anthropic's official guide. Only proposes changes that are actually relevant to the target document — short one-shot-task skills may need none. |

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
| `refactor-doc` | 手動のみ | 既存ドキュメントファイルをプロジェクト規約 (prefix / frontmatter / 配置 / 構造) に沿ってリファクタリングする。並列サブエージェントで「内容レビュー」「配置判断」「品質・frontmatter チェック」「計画と実装の整合性チェック」を分担。元の事実は保持しつつ、冗長さや陳腐化した実装詳細を整理する。`docs/` 配下に `analysis_` / `plan_` / `strategy_` 命名規約と YAML frontmatter (`作成日` / `最終更新` / `ステータス`) を前提とするため **プロジェクト固有運用に依存**。 |
| `user-journey` | `要件確認` / `ジャーニー検索` / `user_journey` / `ユーザージャーニー` / `○○の要件は` / `○○の方針は` / `user-journey` / proactive（設計・実装着手時） | プロジェクトの「現在のユーザー体験・要件・制約」を SQLite に短文で蓄積し、キーワード検索できるナレッジベース。設計・実装に着手する前に検索して現行のユーザー像と整合を取り、ルール更新は許可を得てから書き込む。**既定は UPDATE 上書き**（user_journey は現行像 1 本の表現であり履歴ログではない、履歴は git ログで追える）、既存と矛盾するときは 4 択フローで取り扱いを確認。他文書からは `user_journey id N` 表記で引用。**要 `sqlite3` CLI / プロジェクトローカルに `data/user_journey.db` を作る運用前提**。 |
| `cmux-update-check` | `cmux update` / `cmuxアップデート` / `cmuxの更新確認` / `cmuxを更新` / `cmuxのリリースノート` | cmux のインストール済みバージョンと GitHub の Latest リリースを比較し、間の各バージョンの更新点（注意点・破壊的変更・新機能）を列挙する。リリース取得は `gh` CLI を優先し、無ければ WebFetch にフォールバック。**要 `cmux` CLI / GitHub rate limit 回避のため `gh` CLI 推奨**。 |
| `brainstorming` | `ブレスト` / `設計したい` / `作りたい` / `brainstorm` / `設計`; proactive（非自明な実装着手時） | 実装着手前に「要件 → 設計」の対話を強制し、「何を作るか / 受け入れ条件」を確定。design doc 書き出し → 実装スタイル決定（隔離 × 並列の 4 択）→ branch / worktree を切ってから spec を commit → `writing-plans` に引き継ぐまでが責務。**main / 既定 branch への直 commit は禁止**。 |
| `writing-plans` | `プラン書いて` / `実装計画` / `writing plans` / `plan を作って`; proactive（`brainstorming` で spec 承認後） | spec / 要件を、ゼロ context のエンジニアでも実行可能な bite-size TDD ステップ（失敗テスト → 失敗確認 → 最小実装 → 通過確認 → commit）に分解した実装プランを書く。タスク分解の前にファイル構造（1 ファイル 1 責務）を確定し、Global Constraints は「Spec 由来」「PJ 恒久ルール」「運用前提」の 3 サブセクション必須で記述する。保存先は `.claude/plans/YYYY-MM-DD-<feature-name>.md`。書き終わったら `subagent-driven-development` または直列実装に引き継ぐ。`brainstorming` を経由せず単独起動された場合は、実装方式 4 択（隔離 × 並列）をユーザーに確認する。 |
| `subagent-driven-development` | `subagent driven` / `SDD` / `subagent 駆動` / `plan を消化` / `plan を実行` | `writing-plans` で書いた実装プランを **タスクごとに fresh implementer subagent** を派遣して同セッション内で消化する。各タスク完了後に **task reviewer**（spec 適合 + コード品質）、全タスク終了後に **whole-branch reviewer** を 1 回回す。subagent は controller が選んだ context だけを受け取り session 履歴を引き継がないため、implementer は集中して succeed し controller の context も coordination 用に温存される。完了状況は `.claude/sdd/progress.md` の ledger で永続化し、compaction で履歴が消えても完了済み task を再派遣せず resume できる。brief / report / diff は dispatch prompt に貼らず file 渡しにして context 汚染を防ぐ。Task 1 派遣前の pre-flight gate で plan ↔ review 規約の矛盾と下流前提の不在を 1 質問にまとめて adjudicate する。 |
| `parallel-dispatch` | `並列` / `並列で` / `parallel` / `parallel-dispatch`; proactive（独立した複数の調査・修正タスク） | 独立した N 個の問題ドメインを、1 つの assistant 応答内に複数の `Agent` tool call を並べることで **並列発注**し、結果を統合する薄い版（1 response 1 call は逐次になるので注意）。使うとき / 使わないとき（独立 vs 関連 fail / 共有状態 / Agent 同士の干渉）、Agent prompt 必須項目チェックリスト（モード別: **(a) 実装モード** = fix まで / **(b) 調査モード** = root cause 仮説まで・production 変更禁止）、触ってよい / NG ファイル、読み取り 1 hop default、期待する返り、自スコープに絞ったテストコマンド、「期待値退化禁止」条項、帰還後の conflict チェック + フルテスト + spot check までをカバー。実装 + レビューの 2 段サブエージェントが要るなら `subagent-driven-development` (重い版) を使う。 |
| `using-git-worktrees` | `worktree` / `並行開発` / `並列実装` / `隔離環境` / `using-git-worktrees` | feature 着手前に独立した workspace を確保するスキル。まず Step 0 で「既に linked worktree 内ではないか」を検出し、続いてネイティブ worktree ツール (cmux / `EnterWorktree` / `/worktree`) を優先、無ければ `git worktree add .claude/worktrees/<branch>` にフォールバック（`.gitignore` 追記 → commit → 作成の順序を守る）。worktree 作成後はマニフェスト検出ベースで pnpm/yarn/bun/npm/uv/pip/bundle/cargo/go の install と baseline テストを走らせ、clean state から作業を開始できるようにする。 |
| `test-driven-development` | `TDD` / `テスト駆動` / `test driven` / `テスト先行`; proactive（新機能 / bug fix / リファクタの実装着手前） | テスト → 失敗確認 → 最小実装 → 通過確認 → リファクタを強制するスキル。目玉は **「RED が観測できなかったときの判別フロー」**: 即 pass を A-1 既存重複 / A-2 別 cycle 先取り（regression coverage として残す）/ A-3 偶然成立 に分割し、A-3 には **A-3a 既存ロジックへの negation 注入** と **A-3b counterfactual injection（壊す wrapper を一時追加して RED 強制観測）** の 2 手法を明示。Pattern C には `ERR_MODULE_NOT_FOUND` 解消用の「空 stub は Iron Law の production code に該当しない」特例、Pattern D-1 / D-2 で「runner crash 自体を valid RED とみなす」分岐を備える。Iron Law の delete 規則は「この cycle で新規追加する production code」対象であり、既存コードの bug fix は failing test → minimal patch で対象外と明示。`empirical-prompt-tuning` を 3 iter 回して accuracy 100% で天井安定したことを根拠に出荷。同梱 `testing-anti-patterns.md` は mock 系 anti-pattern 5 種 + 副作用 DI パターンを gate function 付きでカバー。 |
| `install-skills` | `install-skills` / `スキル導入` / `skill install` / `スキル入れて` / `apm スキル` | APM の skills repository (既定 `trapple/skills`) を対話的にブラウズし、各 skill の install 済み状態を 5-status (`global` / `local` / `both` / `manual` / `—`) で併記、別 repo 由来の同名スキル衝突は表とは別の警告ブロックで通知する。選択はチャット返信 (`foo bar` / `all` / `cancel`)、install 先 (`global` / `local`) は AskUserQuestion で 1 回だけ確認 (`--global` / `--local` で skip 可)、その後 `apm install` を一括実行する。pin-point install / バージョン指定 / uninstall / update は責務外 (= `apm` 直叩きの方が速い)。`manual` 状態 (= apm 経由でなく `~/.claude/skills/` に物理配置済み) のスキルを明示選択した場合は、上書き衝突防止のため install を実行せず `rm -rf` 案内を出して終了する。**`apm` CLI 必須 / 対象 repo のローカルクローンが `~/repos` 配下に無い場合は `gh` CLI も必要**。 |
| `fable5-prompt-tuning` | `Fable5向けに最適化` / `Fable 5 prompting` / `fable5チューニング` / `このプロンプトをFable5向けに直して` | システムプロンプト / skill の `SKILL.md` / `CLAUDE.md` / エージェント向けプロンプトを、Claude Fable 5 の Opus 4.8 からの挙動差分に照らして診断し、ページの丸暗記ではなく Before/After の具体的な修正案を提示する。effort設定のアドバイス、過剰な手順列挙を簡潔な誘導文に圧縮、長時間実行時の進捗申告をツール結果で裏付けさせる指示、行動境界の明示、非同期な並列サブエージェント委任、教訓を記録するメモリ設計、早期停止/コンテキスト不安への対策、依頼背景(Why)の明示、最終サマリーの可読性、`reasoning_extraction` 拒否を誘発する「思考過程を書け」系指示の監査、長時間非同期タスク向け send-to-user ツールの追加、をチェックリスト化。同梱の `patterns.md` に Anthropic公式ガイドからのそのまま使える指示文言を収録。対象文書に無関係な項目は提案しない（短い一発タスクの skill なら変更不要と結論することもある）。 |

### なぜ APM 経由なのか

`.claude/skills/` に直接ファイルを置くと、バージョン管理も改ざん検知もありません。APM は次を提供します。

- `apm.lock.yaml` による **integrity hash でのバージョン固定**
- インストール時の **隠し Unicode（プロンプトインジェクション）スキャン**
- `apm audit` による **配布元との差分検出**（ドリフト検出）
- `apm-policy.yml` で組織レベルの **許可ソース/スコープ/プリミティブの制御**

サプライチェーン攻撃が現実的なリスクになった今、`git clone` や手作業コピーよりも安全な配布チャネルです。

### ライセンス

[MIT](LICENSE)
