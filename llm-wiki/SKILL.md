---
name: llm-wiki
description: "Karpathyの「LLM Wiki」パターン（永続的・追記型のmarkdown wikiをLLMが維持する個人ナレッジベース手法）をObsidianVault上で運用するスキル。Wiki本体は `~/ObsidianVault/llm-wiki/`、ソースは `~/ObsidianVault/raw/` 配下（`raw/Clippings/` はWeb Clipper受け皿、整理済みは `raw/<Category>/`）と外部の `~/repos/<owner>/<repo>/docs/`。3操作: Ingest / Query / Lint。ユーザーが「LLM Wiki」「Karpathy wiki」「永続的なナレッジベース」「wiki に取り込んで／ingest」「wiki から〜について調べて／query」「wiki を lint／掃除／健全性チェック」「Clippings を整理して」「memex」のような発話をしたとき、または `~/ObsidianVault/llm-wiki/`・`~/ObsidianVault/raw/`・`~/repos/<owner>/<repo>/docs/` 配下で作業しているときは、明示されていなくても必ずこのスキルを使う。"
---

# LLM Wiki

Andrej Karpathy 提唱「LLM が維持する個人ナレッジベース」を Claude Code + Obsidian で運用するスキル。RAG で都度検索するのではなく、コンパイル済みで相互リンクされた永続 wiki 層を LLM 自身が維持する。

詳細規約（schema）は `~/ObsidianVault/llm-wiki/CLAUDE.md` に集約。本 SKILL.md は **操作判定と Query 高速経路** に絞る。

## 配置概要

```
~/ObsidianVault/
├── raw/                       # 全ソースのルート（immutable、分類のための移動のみ可）
│   ├── Clippings/             # Web Clipper 受け皿（未整理）
│   └── <Category>/            # 整理済み（AI/Tech/VFX/XR/Entertainment/Personal/Twitter/...）
├── llm-wiki/                  # wiki 本体（このスキルが書き換える唯一の場所）
│   ├── CLAUDE.md              # schema（書き込みを伴う操作の前に必ず Read）
│   ├── index.md               # 全体カタログ（2 層 index の上層）
│   ├── pages/<genre>/         # 9 ジャンル × {index, log, _summary, entities, concepts, sources, syntheses}
│   └── .query/manifest.jsonl  # 検索インデックス（grep 用、直接 Read しない）
└── .obsidian-links/           # チャット出力用 .inetloc（update_indexes.py が自動生成）
```

外部ソース: `~/repos/<host>/<owner>/<repo>/docs/**/*.md` も ingest 対象（git 管理下、コピーせず参照。機密境界は CLAUDE.md「外部リポジトリ docs/ ingest 規約」）。

## Obsidian 規約（必須、要約）

- 内部リンクは `[[wikilinks]]` 形式（`[text](path.md)` は禁止 — backlink/graph が壊れる）
- 全ページに frontmatter 必須: `tags / created / updated`（種別ごとの追加フィールドは CLAUDE.md）
- 主張ごとに `（参照: [[<source-name>]]）` で出典明記、矛盾は `> [!warning] 矛盾` callout で残す

## 操作ディスパッチ（`/llm-wiki <op> [...]`）

`args` 先頭トークンで操作判定（大文字小文字無視、引用符剥がす）。空 or 非該当なら自然文から推定。

| `args` 先頭 | 操作 | 残りの引数 |
|---|---|---|
| `i` / `ingest` | Ingest | ソースパス／識別子。空なら対話で確認 |
| `q` / `query` | Query | 質問文。空なら対話で確認 |
| `l` / `lint` | Lint | チェック対象の絞り込み（例: `orphans`）。空なら全項目 |
| `h` / `help` | Help | なし。下記「Help」節のヘルプをそのまま出力して終了（wiki には触らない） |

## Help（`/llm-wiki help`）

以下をそのままチャットに出力する（ファイルは一切読まない・書かない。即答すること）:

```markdown
# /llm-wiki 使い方

| コマンド | 動作 | 例 |
|---|---|---|
| `/llm-wiki q "<質問>"` | wiki に問い合わせ | `/llm-wiki q "Karpathy って誰？"` |
| `/llm-wiki i <パス>` | ソースを wiki に取り込む | `/llm-wiki i raw/Clippings/foo.md`<br>`/llm-wiki i ~/repos/github.com/<owner>/<repo>` |
| `/llm-wiki l [項目]` | 健全性チェック（提案のみ、適用は承認後） | `/llm-wiki l` / `/llm-wiki l orphans` / `/llm-wiki l stale_external` |
| `/llm-wiki help` | このヘルプ | |

**query の種別（自動判定）**:
- **fact** —「X を始めたのいつ？」「何回した？」→ raw サマリ層を grep して即答
- **lookup** —「Y って誰／何？」→ manifest grep → 1-3 ページ Read（迷ったらこれ）
- **compare** —「A と B の違いは？」→ 比較表
- **synthesis** —「2025 年に何してた？」→ ジャンル横断統合（良い回答は保存提案 💾 が出る）
- **source** —「この記事の原文は？」→ raw を直接 Read

**補足**:
- 保存提案 💾 は保存価値があると判断したときだけ付く（不要なら「不要」と返すだけ）
- 所要時間を計測したいときは質問に「計測して」と添える
- 未整理の `raw/Clippings/` は「Clippings を整理して」で ingest + カテゴリ振り分け
- インデックス手動更新: `python3 ~/ObsidianVault/scripts/update_indexes.py`（ingest 後は自動実行される）
```

## Query（デフォルト経路 — さっと答える）

**原則: 読み取りだけの query に書き込み儀式を付けない。** fact / lookup / compare / source は「grep → 1-3 ページ Read → 回答」で完結する。CLAUDE.md・トップ index.md は読まない。

### 種別判定と経路

| 種別 | 例 | 経路 |
|------|-----|------|
| **fact** | 「X を始めたのいつ？」「何回 Z した？」 | `grep -rln "<keyword>" ~/ObsidianVault/raw/<source-dir>/*/_summary/` → 該当月 Read → 回答 |
| **lookup** | 「Karpathy って誰？」「Nano Banana って何？」 | manifest grep → 候補 1-3 件 Read → 回答（判定曖昧ならこれが default） |
| **compare** | 「A と B の違いは？」 | 各キーワードを manifest grep → 候補ページの該当節 Read → 比較表 |
| **synthesis** | 「2025 年に何してた？」「〜の履歴は？」 | `pages/<genre>/_summary.md` (~2KB) → 必要ならジャンル index → manifest grep → 個別ページ複数 Read → 必要なら raw へ。**5+ ページ Read は Sonnet subagent に委譲**（例は `references/operations.md`） |
| **source** | 「この記事の本文は？」 | `raw/<Category>/<file>.md` を直接 Read |

モデル: fact/lookup/compare/source は Sonnet で十分・高速。上位モデルで単発 lookup が続くようなら「`/model sonnet` で速くなる」と一言添える。synthesis と ingest は判断が多いので上位モデル向き。

### manifest の使い方（最重要）

`~/ObsidianVault/llm-wiki/.query/manifest.jsonl` は全ページ 1 行要約の検索インデックス。**直接 Read しない（~80K tokens）、必ず grep で絞る**:

```bash
grep -i 'karpathy' ~/ObsidianVault/llm-wiki/.query/manifest.jsonl            # キーワード横断
grep '"genre":"ai"' ~/ObsidianVault/llm-wiki/.query/manifest.jsonl           # ジャンル絞り込み
grep '"genre":"ai"' ~/ObsidianVault/llm-wiki/.query/manifest.jsonl | grep '"type":"synthesis"'   # ジャンル × type
grep '"genre":"ai"' ~/ObsidianVault/llm-wiki/.query/manifest.jsonl | grep -i 'claude'            # AND は 2 段 grep
```

絞ったエントリの `path` から、本当に必要なページだけ Read する。1 行スキーマ: `{"path","genre","type","title","aliases","summary","keywords","sources","updated","size"}`。

### Twitter 系 fact のショートカット

「いつ」「誰」「何回」型はまずここ:

```bash
cat ~/ObsidianVault/raw/Twitter/<handle>/_yearly/<YYYY>.md        # 年俯瞰
grep -rln "<keyword>" ~/ObsidianVault/raw/Twitter/*/_summary/     # 全月横断
# 詳細は raw/Twitter/<handle>/<YYYY-MM>.md を Read
```

### 儀式は条件付き（v0.23）

| 儀式 | 実行条件 |
|---|---|
| 💾 保存提案フッター | 保存推奨(✅) or グレー(⚠) と判断したときのみ付ける。保存不要(❌)なら **何も出さない** |
| ジャンル log 追記 | synthesis を **保存したときのみ**（保存判断基準は CLAUDE.md） |
| クエリ計測 (timer) | ユーザーが「計測して」「timing」「遅い」等と言ったときのみ。手順は `references/operations.md` |

## チャット出力時のリンク変換（必須）

チャット応答で wiki ページ・raw ソースに言及するときは `[[Page Name]]` ではなく `.inetloc` への `file://` リンクに変換する（ターミナルが `obsidian://` を通さないため）:

`[Page Name](file://<絶対HOME>/ObsidianVault/.obsidian-links/Page%20Name.inetloc)`

`.inetloc` は `update_indexes.py` が wiki 全ページ分を事前生成済み。無いページ（raw ソース等）のみ lazy 生成（手順は `references/operations.md`）。**wiki ファイル本体の中では `[[wikilinks]]` のまま**（変換すると graph/backlink が壊れる）。

## Ingest

2 系統: **(A) raw/ 系**（`raw/Clippings/` はカテゴリ判定 → `raw/<Category>/` へ移動提案 → ingest）、**(B) 外部 repo docs/ 系**（コピーせず frontmatter で参照、機密 repo は強制 `pages/work/` + `confidential: true`）。

手順詳細は `~/ObsidianVault/llm-wiki/CLAUDE.md`（**書き込み前に必ず Read**）と `references/operations.md`。

**どちらの場合も最後に必ず 1 コマンド**（増分更新、変更ページのみ再パースで数秒）:

```bash
python3 ~/ObsidianVault/scripts/update_indexes.py
```

これで manifest / pages.tsv / ジャンル index.md / _summary.md / .inetloc がまとめて更新される。ジャンル index.md への手動追記は不要（自動再生成）。

## Lint

orphan / stale / 矛盾 / リンク欠け / frontmatter 欠損 / index drift 等の健康診断。修正は提案 → ユーザー承認後に適用。チェック項目と手順は `references/operations.md` と CLAUDE.md。

## 振る舞いの原則

- **raw/ は immutable**: 編集・削除不可。分類のための移動（mv）のみ許可
- **`~/repos/` 配下の md は編集・削除・自動 git pull しない**
- **書き込みを伴う操作（ingest / synthesis 保存 / ページ更新 / lint 適用）の前に必ず wiki の CLAUDE.md を Read**。SKILL.md と矛盾したら CLAUDE.md 優先
- **大規模リファクタ・一括リネームはユーザー確認を取る**
- **矛盾を隠さない**: callout で両論併記
- **`confidential: true` の内容を `pages/work/` 以外へ転記しない**
- **Lint 結果は提案として出し、適用はユーザー承認後**

## 初期セットアップ（wiki がまだ無いとき）

`references/setup.md` を参照。

## 詳細リファレンス

- `references/operations.md` — Ingest / Query / Lint の具体手順、timer、subagent 例、.inetloc 生成
- `references/setup.md` — 初期セットアップ、テンプレ
- `references/schema-template.md` — 新規 wiki 用 CLAUDE.md テンプレート
- `~/ObsidianVault/llm-wiki/CLAUDE.md` — 現行 schema（書き込み時に Read）

## 出典

Andrej Karpathy「LLM Wiki」（gist, 2026-04 頃）<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>
