# 初期セットアップ + テンプレート

新規 wiki 立ち上げ時に使う。既存 wiki の運用には不要なので、SKILL.md 本体から分離 (v0.20)。

## 初期セットアップ（wiki がまだ無いとき）

ユーザーが「wiki を作って」と言ってきたら：

1. **wiki の用途・スコープを確認**: 「Clippings の整理」「論文サーベイ」「読書 companion」など。1〜2 行で固める。これが schema の中身を決める。
2. **既存ディレクトリを点検**: `~/ObsidianVault/llm-wiki/` が無いことを確認（あれば既存利用）。`~/ObsidianVault/raw/Clippings/` が既存ソースとして存在するか確認（なければ Web Clipper 保存先設定変更を案内）。
3. **ディレクトリ作成**:
   ```bash
   mkdir -p ~/ObsidianVault/{raw/Clippings,llm-wiki/pages/{entities,concepts,sources,syntheses}}
   ```
   （カテゴリフォルダ `raw/AI/`, `raw/Tech/` 等は ingest 時に必要になったら作成）
4. **Schema (`llm-wiki/CLAUDE.md`) を生成**: `references/schema-template.md` をベースに、用途・**ソース場所一覧**・ページ命名規則・追加 frontmatter フィールド・ingest/query/lint 各ワークフローをユーザーと話しながら埋める。テンプレ丸コピで終わらせない。
5. **`index.md` と `log.md` を空のスケルトンで作成**: 下記テンプレに従う。
6. **動作確認**: 1 つだけサンプルソースを ingest してみて、流れが回ることを確認（ユーザー希望時）。

セットアップは「テンプレ展開」ではなく「ユーザーとの対話で schema を共設計する」工程。ここで手を抜くと wiki が腐る。

## index.md の規約

content-oriented なカタログ。LLM は query 時にまずここを読んで関連ページを絞り込む。

```markdown
---
tags: [index]
updated: YYYY-MM-DD
---

# Index

> この wiki の全ページカタログ。各ページの役割を 1 行で。

## Entities
- [[Alice]] — プロジェクト X のリード
- [[Acme Corp]] — 競合 SaaS

## Concepts
- [[Retrieval Augmentation|RAG]] — 概要と派生
- [[LLM Wiki Pattern]] — Karpathy のパターン

## Sources
- [[2026-04-12 Karpathy LLM Wiki]] — 元アイデアの gist 要約
- [[2026-05-07 Claude Code TradingView MCP]] — 技術記事
（※ Sources 節は wiki 内の要約ページ一覧。生ソース本体は `~/ObsidianVault/raw/<Category>/`（未整理は `raw/Clippings/`）配下にある）

## Syntheses
- [[RAG vs Wiki tradeoff]] — query から派生した分析
```

Ingest のたびに該当セクションへ 1 行追記する。`updated` を更新。

**規模が大きくなったら 2 層化**: ページ数が 100+ になったら `pages/<genre>/index.md` 構造（schema v0.8 で導入）に移行。トップ `index.md` はジャンル一覧のみ、各ジャンル詳細はジャンル index.md。

## log.md の規約

時系列・append-only。**必ず一定の prefix で始める**ので、`grep "^## \[" log.md | tail -10` で履歴を追える：

```markdown
---
tags: [log]
---

# Log

## [2026-05-07] ingest | Karpathy LLM Wiki gist
- Source: [[llm-wiki]]
- New pages: [[LLM Wiki Pattern]], [[Memex]]
- Updated: [[Retrieval Augmentation|RAG]]（対比節を追加）, [[Index]]

## [2026-05-07] query | wiki と RAG の違いを 1 段落で
- Used: [[LLM Wiki Pattern]], [[Retrieval Augmentation|RAG]]
- Filed answer to: [[RAG vs Wiki one-pager]]

## [2026-05-08] lint
- Orphans: [[Bob]]（誰からもリンクされていない）
- Stale: [[X]] — 新ソースで主張が変わった
- TODO: [[Y]] のページを新設
```

2 層化後はジャンル log (`pages/<genre>/log.md`) と meta log (`pages/meta/log.md`) に振り分け。

## Obsidian 統合のヒント

- **graph view** で全体形状を見て orphan/hub を把握する。Lint の最初のチェックに使う
- **Web Clipper** の出力先は `~/ObsidianVault/raw/Clippings/` に設定（Obsidian Settings → Web Clipper → 保存場所）
- **画像のローカル保存**: Settings → Files and links → Attachment folder path を `raw/assets/` 等に。LLM が画像を直接参照できる
- **`raw/Clippings/` から `raw/<Category>/` への整理**: ingest 時に LLM がカテゴリ判断して移動提案 → 承認後 mv
- **Dataview プラグイン**: frontmatter（tags, sources, created）から動的テーブルを生成可能。Lint や index の補助に使える
- **Marp プラグイン**: wiki ページからスライド生成。Query の出力形式の選択肢に
- Vault 全体を **git 管理** すれば履歴・分岐・共有が無料で手に入る
