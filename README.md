# trapple/skills

Personal collection of [Claude Code](https://github.com/anthropics/claude-code) skills, packaged for the [Agent Package Manager (APM)](https://github.com/microsoft/apm).

## Install

Project-local (writes to `./.claude/` or `./.agents/skills/` in the current repo):

```bash
apm install trapple/skills
```

Machine-wide / user-global (writes to `~/.apm/` and is exposed to every Claude Code session):

```bash
apm install -g trapple/skills
```

Or pin to a specific version:

```bash
apm install -g trapple/skills#v0.1.0
```

Install only a specific skill (instead of the whole package):

```bash
apm install trapple/skills --skill commit
apm install -g trapple/skills --skill commit
```

## Included skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| `commit` | `commit`, `コミット`, `コミットして` | Analyze conversation history to extract the **Why** behind the change, split into multiple commits when there are multiple Whys, and write a Conventional Commits style message. |
| `init-rules` | `init-rules`, `ルール導入`, `ルールテンプレート` | Copy bundled rule templates (Fail-Fast error handling, docs frontmatter policy, plan-mode output location, …) into the current project's `.claude/rules/`. Templates ship with the skill under `rules-templates/`. **Claude Code only** — relies on the `.claude/rules/` path-glob mechanism, which Codex / other agents (AGENTS.md-based) do not implement. |
| `codex` | `codex`, `Codex`, `Codexに聞いて`, `Codexで` | Thin wrapper that forwards the user's prompt to the OpenAI Codex CLI via `codex exec "$PROMPT" < /dev/null` (stdin must be closed or it hangs waiting for additional input). Requires the `codex` CLI on PATH. |
| `create-skill` | `スキル作って`, `Skill作って`, `create skill` | Meta-skill that scaffolds a new Claude Code skill at `~/.claude/skills/<name>/SKILL.md` (or `.claude/skills/<name>/SKILL.md` for project scope) with correct frontmatter. Explicitly distinguishes skills from legacy single-file commands. |
| `pbcopy` | `copy`, `コピー`, `コピーして` | Copy file contents or arbitrary text to the macOS clipboard via `pbcopy`, using heredocs to handle special characters safely. **macOS only** — `pbcopy` is not available on Linux/Windows. |

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

Claude Code 向けに個人で作成したスキル集を、Microsoft の [APM (Agent Package Manager)](https://github.com/microsoft/apm) パッケージとして配布するリポジトリです。

### インストール

```bash
apm install trapple/skills               # プロジェクトローカル（./.claude/ など）
apm install -g trapple/skills            # マシン全体（~/.apm/ → 全 Claude Code セッションで利用可能）
apm install -g trapple/skills#v0.1.0     # バージョン固定（global）
apm install trapple/skills --skill commit       # 特定スキルのみ（パッケージ全体ではなく commit だけ）
apm install -g trapple/skills --skill commit    # 同上をグローバルに
```

### 収録スキル

| スキル | トリガー | 概要 |
|-------|---------|------|
| `commit` | `commit` / `コミット` / `コミットして` | 会話履歴を遡って変更の **Why** を抽出し、Why が複数あればコミットを分割、Conventional Commits 形式のメッセージで自動コミットする。 |
| `init-rules` | `init-rules` / `ルール導入` / `ルールテンプレート` | スキルに同梱されたルールテンプレート（Fail-Fast エラーハンドリング、docs frontmatter 運用、plan モード出力先 など）をプロジェクトの `.claude/rules/` にコピーする。テンプレートは `rules-templates/` として skill ディレクトリに同梱。**Claude Code 専用** — `.claude/rules/` の path-glob 自動適用機構に依存しており、AGENTS.md ベースの Codex などでは効きません。 |
| `codex` | `codex` / `Codex` / `Codexに聞いて` / `Codexで` | ユーザーのプロンプトを OpenAI Codex CLI に転送する薄いラッパー。`codex exec "$PROMPT" < /dev/null` で stdin を閉じて呼ぶ（閉じないとハングする）。`codex` コマンドが PATH に必要。 |
| `create-skill` | `スキル作って` / `Skill作って` / `create skill` | 新しい Claude Code skill を `~/.claude/skills/<name>/SKILL.md`（またはプロジェクト側 `.claude/skills/<name>/SKILL.md`）に正しい frontmatter 付きで生成する meta skill。旧形式の単一ファイル command との混同を明示的に防ぐ。 |
| `pbcopy` | `copy` / `コピー` / `コピーして` | ファイル内容や任意のテキストを macOS の `pbcopy` でクリップボードにコピーする。特殊文字はヒアドキュメントで安全に扱う。**macOS 専用** — Linux/Windows では `pbcopy` が無い。 |

### なぜ APM 経由なのか

`.claude/skills/` に直接ファイルを置くと、バージョン管理も改ざん検知もありません。APM は次を提供します。

- `apm.lock.yaml` による **integrity hash でのバージョン固定**
- インストール時の **隠し Unicode（プロンプトインジェクション）スキャン**
- `apm audit` による **配布元との差分検出**（ドリフト検出）
- `apm-policy.yml` で組織レベルの **許可ソース/スコープ/プリミティブの制御**

サプライチェーン攻撃が現実的なリスクになった今、`git clone` や手作業コピーよりも安全な配布チャネルです。

### ライセンス

[MIT](LICENSE)
