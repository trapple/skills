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

## Included skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| `commit` | `commit`, `コミット`, `コミットして` | Analyze conversation history to extract the **Why** behind the change, split into multiple commits when there are multiple Whys, and write a Conventional Commits style message. |

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
```

### 収録スキル

| スキル | トリガー | 概要 |
|-------|---------|------|
| `commit` | `commit` / `コミット` / `コミットして` | 会話履歴を遡って変更の **Why** を抽出し、Why が複数あればコミットを分割、Conventional Commits 形式のメッセージで自動コミットする。 |

### なぜ APM 経由なのか

`.claude/skills/` に直接ファイルを置くと、バージョン管理も改ざん検知もありません。APM は次を提供します。

- `apm.lock.yaml` による **integrity hash でのバージョン固定**
- インストール時の **隠し Unicode（プロンプトインジェクション）スキャン**
- `apm audit` による **配布元との差分検出**（ドリフト検出）
- `apm-policy.yml` で組織レベルの **許可ソース/スコープ/プリミティブの制御**

サプライチェーン攻撃が現実的なリスクになった今、`git clone` や手作業コピーよりも安全な配布チャネルです。

### ライセンス

[MIT](LICENSE)
