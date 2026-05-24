---
name: llm-wiki
description: Karpathyの「LLM Wiki」パターン（永続的・追記型のmarkdown wikiをLLMが維持する個人ナレッジベース手法）を、ObsidianVault 上で運用するためのスキル。Wiki 本体は `~/ObsidianVault/llm-wiki/` に固定、ソースは `~/ObsidianVault/raw/` 配下と外部の `~/repos/<owner>/<repo>/docs/`（v0.11 で追加、git 管理下の個人 OSS / 仕事 PJ ナレッジを wiki から参照可能に）。`raw/Clippings/` は Web Clipper の保存先（未整理の受け皿）、整理済みは `raw/<Category>/`（例 `raw/AI/`, `raw/Tech/`, `raw/Game/`）にユーザーまたは LLM が移動する運用。閲覧ツールは Obsidian、リンクは `[[wikilinks]]` 形式、ページ先頭に YAML frontmatter を必須とする。3 操作（Ingest / Query / Lint）と初期セットアップをカバー。ユーザーが「LLM Wiki」「Karpathy wiki」「永続的なナレッジベース」「Vault に wiki」「このソースを wiki に取り込んで／ingest」「~/repos のドキュメントを ingest」「wiki から〜について調べて／query」「wiki を lint／掃除／健全性チェック」「Clippings を整理して」「memex 的なノート」「Obsidian で LLM がメモを書く」のような発話をしたとき、または `~/ObsidianVault/llm-wiki/` 配下や `~/ObsidianVault/raw/` 配下、`~/repos/<owner>/<repo>/docs/` 配下で作業しているときは、明示されていなくても必ずこのスキルを使う。RAG で都度検索するのではなく、コンパイル済みで相互リンクされた永続 wiki 層を LLM 自身が維持する点が肝。
---

# LLM Wiki

Andrej Karpathy が提唱した「LLM が維持する個人ナレッジベース」のパターンを、Claude Code が ObsidianVault 上で実践するためのスキル。

詳細規約は `~/ObsidianVault/llm-wiki/CLAUDE.md`（既存 wiki の schema、v0.19+）に集約。本 SKILL.md は **起動時の起点・操作判定・経路分岐** に絞る。

## なぜこのパターンか

通常の RAG は質問のたびに raw ソースから断片を引いてきて毎回ゼロから組み立てる。Wiki が育たない、矛盾は毎回検出し直し、合成は揮発的。

このパターンは違う。LLM は **永続的・追記型の wiki 層を維持する**。新しいソースが入ったら、要約だけでなく既存ページを更新し、相互リンクを張り直し、矛盾にフラグを立てる。Wiki は「コンパイル済みの知識」として蓄積される。Obsidian が IDE、LLM がプログラマー、Wiki がコードベース、というメタファーで動く。

## 配置概要

```
~/ObsidianVault/
├── raw/                       # 全ソースのルート（immutable）
│   ├── Clippings/             # Web Clipper 受け皿（未整理）
│   └── <Category>/            # 整理済み（AI/Tech/VFX/XR/Entertainment/Personal/...）
├── llm-wiki/                  # wiki 本体（このスキルが書き換える唯一の場所）
│   ├── CLAUDE.md              # schema（v0.19+、書き込み時に Read）
│   ├── CLAUDE.history.md      # schema 履歴アーカイブ
│   ├── index.md               # 全体カタログ（2 層 index/log の上層）
│   ├── pages/<genre>/         # 9 ジャンル × {index, log, entities, concepts, sources, syntheses}
│   └── .query/manifest.jsonl  # 検索インデックス（grep 用、v0.19）
└── attachments/               # 添付（wiki 対象外）
```

詳細な固定パスとカテゴリ命名は `~/ObsidianVault/llm-wiki/CLAUDE.md` 参照（書き込み時）。

## Obsidian 規約（必須、要約）

- 内部リンクは `[[wikilinks]]` 形式（markdown link `[text](path.md)` は禁止 — Obsidian の backlink/graph が解決しない）
- 全ページに frontmatter 必須: `tags / created / updated`（ページ種別ごとの追加フィールドは CLAUDE.md 参照）
- 主張ごとに `（参照: [[<source-name>]]）` で出典明記
- 矛盾は `> [!warning] 矛盾` callout で残す（隠さない）

詳細・各ページ種別の frontmatter 拡張・命名規則は `~/ObsidianVault/llm-wiki/CLAUDE.md` を Read。

## チャット出力時のリンク変換（必須）

**ユーザーへのチャット応答** で wiki ページや raw ソースに言及するときは、`[[Page Name]]` ではなく `.inetloc` ファイルへの `file://` リンクに変換する。Claude Code のターミナル UI が `obsidian://` の OSC 8 ハイパーリンクを通さないため、`file://` で `.inetloc`（macOS Internet Location File）を開かせ、LaunchServices に Obsidian を起動させる。

- **対象**: query 回答、ingest/lint 報告、その他ユーザーへの全チャット出力
- **対象外**: wiki ファイル本体（`pages/**/*.md`, `index.md`, `log.md` 等）。`[[wikilinks]]` のまま

変換規則と `.inetloc` 自動生成の詳細は `references/operations.md` の「チャット出力時のリンク変換」を参照。

## 操作（3 種）

詳細手順とプロンプト例は `references/operations.md`。ここでは概要だけ。

- **Ingest**: 2 系統あり
  - **(A) raw/ 系**: `~/ObsidianVault/raw/` 配下のソースを読んで `pages/<genre>/sources/<title>.md` に要約、関連 entity/concept ページを新規・更新、ジャンル `index.md`/`log.md` を追記。`raw/Clippings/` のソースは ingest 時にカテゴリ判断 → `raw/<Category>/` への移動を提案
  - **(B) 外部 repo docs/ 系**: `~/repos/<host>/<owner>/<repo>/docs/**/*.md` を ingest。コピー・symlink せず、source ページ frontmatter で外部参照。機密 repo（例: 仕事の private org 配下）は強制 `pages/work/` + `confidential: true`。詳細は CLAUDE.md「外部リポジトリ docs/ ingest 規約」節
  - **どちらの場合も**: ingest の **最後に** 以下 2 つを実行（v0.19、query 高速化用インデックス再生成）
    - `python3 ~/ObsidianVault/scripts/build_query_manifest.py` — `.query/manifest.jsonl` 再生成
    - `python3 ~/ObsidianVault/scripts/build_genre_summaries.py` — 各 `pages/<genre>/_summary.md` 再生成
- **Query**: 種別判定 → 経路分岐（下記節）。良い回答は `pages/<genre>/syntheses/` に再ファイルしてジャンル index/log に追記
- **Lint**: orphan / stale / 矛盾 / リンク欠け / frontmatter 欠損 / data gap を健康診断。修正は提案 → ユーザー承認後に適用

### 引数のディスパッチ（`/llm-wiki <op> [...]`）

スキル起動時の `args` 先頭トークンで操作を判定する。トークンの大文字小文字は無視、引用符は剥がす。

| `args` 先頭 | 操作 | 残りの引数の扱い |
|---|---|---|
| `i` / `ingest` | Ingest | 残り全体をソースパス／ファイル名／識別子として扱う。空なら対象を対話で確認 |
| `q` / `query` | Query | 残り全体を質問文として扱う（`"..."` でクォート可）。空なら質問を対話で確認 |
| `l` / `lint` | Lint | 残りはチェック対象の絞り込み（例: `orphans`, `frontmatter`）。空なら全項目 |

例:
- `/llm-wiki q "LLM Wiki と RAG の違いは？"` → Query で質問を実行
- `/llm-wiki i raw/Clippings/foo.md` → 指定ソースを ingest
- `/llm-wiki i ~/repos/github.com/<owner>/<repo>` → 外部 repo の docs/ を一括 ingest
- `/llm-wiki l orphans` → orphan のみ lint
- `/llm-wiki l stale_external` → external_repo source の SHA 差分チェック

`args` が空 or 上記に該当しない場合は、自然文として内容から操作を推定。

## クエリ種別判定と経路分岐（v0.19、必読）

Query 操作のとき、**最初に問いの種別を判定**して経路を選ぶ。CLAUDE.md と index.md を毎回 Read すると 1 query あたり 20-50K tokens 消費するため、必要なものだけ読む設計。

### 判定基準

| 種別 | 例 | 経路 | 推奨モデル |
|------|-----|------|----------|
| **fact** | 「X を始めたのいつ？」「Y と初めて会ったのは？」「2023 年に何回 Z した？」 | (1) `grep -rln "<keyword>" ~/ObsidianVault/raw/<source-dir>/*/_summary/` で該当月特定 → 該当月の `_summary.md` or 生 `<YYYY-MM>.md` Read → 回答 | **Haiku / Sonnet** で十分（grep 主体、判断少） |
| **lookup** | 「Karpathy って誰？」「Nano Banana って何？」「外部 repo ingest 規約は？」 | (1) `grep '"<keyword>"' .query/manifest.jsonl` または `grep '<keyword>' .query/pages.tsv` で候補抽出（典型 3-10 件）→ (2) 候補ページ 1-3 件 Read → 回答 | **Sonnet** で十分（候補絞り + 短い要約） |
| **compare** | 「A と B の違いは？」 | manifest で各キーワードを並列 grep → 各候補ページ frontmatter + 該当節のみ Read → 比較表を組み立て | **Sonnet**（比較表組み立て） |
| **synthesis** | 「2025 年に何してた？」「アーティスト A のライブまとめは？」「<時系列イベント> の履歴は？」 | (1) 関連ジャンルの `pages/<genre>/_summary.md` (~2 KB、軽量入口、v0.19) を Read で全体像把握 → (2) 詳細が必要なら `pages/<genre>/index.md` → (3) manifest で候補ページ抽出 → (4) 個別ページ複数 Read → (5) raw が必要なら降りる。**ページ数が多い場合 (5+) は Sonnet subagent に Read を委譲**（下記「subagent パターン」参照） | **Opus**（横断判断 + 矛盾検出） |
| **source** | 「この記事の本文は？」（明示的に raw を見る指示） | `raw/<Category>/<file>.md` を直接 Read | **Haiku / Sonnet** |

判定が曖昧なら **lookup を default**。

### モデル切替の指針（v0.21、必読）

Claude Code はメインセッションのモデルが固定（起動時 or `/model` 切替）。**実時間の最大要因は LLM 推論時間**で、Opus は判断力豊富だが遅く、Haiku は速いが判断力が浅い。クエリ種別ごとに以下を考慮:

- **メインを軽量モデルで動かす場合**: ユーザーが `/model sonnet` で切り替えてから query する。fact/lookup/compare/source なら Sonnet 直接で十分速い。判断ループが少なく、回答品質も実用範囲
- **メインを Opus で動かす場合**: synthesis や ingest など判断が複雑なときに使う。**ただし長尺タスクは subagent で Sonnet に委譲**（下記）
- **モデル切替の提案**: query 受信時、種別が fact/lookup/compare/source なのに Opus で動いている場合、回答の最後に「次回から `/model sonnet` で 2-3 倍速くなる可能性」と添えるとよい

### subagent パターン（v0.21、synthesis 専用）

synthesis 経路で **5 ページ以上を Read + 統合** が必要なときは、Agent tool で Sonnet subagent を起動して Read と一次まとめを委譲する。メイン Opus は結果サマリだけ受け取って最終回答を整形。

**メリット**:
- メインのコンテキスト消費を抑える（subagent のコンテキストは独立）
- subagent 内の Read は並列化できる（Bash 多重呼び出し）
- メインは判断・整形に専念、subagent は素直に Read + 抽出に専念

**Agent tool 呼び出し例**:

```
description: "同ジャンル sources 17 件の Read + 集計"
subagent_type: "general-purpose"
model: "sonnet"
prompt: |
  ~/ObsidianVault/llm-wiki/pages/<genre>/sources/ 配下の
  「<キーワード>」を含むファイル 17 件を順次 Read して、各エントリの
  日付・主要メタ情報・要点を表にまとめて返してください。
  ファイルパスは以下:
  - pages/<genre>/sources/<YYYY-MM-DD> <title-1>.md
  - pages/<genre>/sources/<YYYY-MM-DD> <title-2>.md
  ...（17 件のリスト）
  
  出力: マークダウン表（日付 / 主要メタ列 / 特記事項）。
  本文の引用は最小限、200 行以内に収める。
```

**注意**:
- subagent 起動は 1-3 秒のオーバーヘッドあり。**5 ページ未満なら直接 Read の方が速い**
- subagent はメインのコンテキストを継承しない。必要な前提・パス・スキーマ情報は **prompt にすべて埋める**
- 判断が必要なタスク（ページ判断基準の適用、矛盾検出、機微情報の取り扱い）は **subagent に委ねない**——メイン Opus が直接やる
- 結果サマリを受け取った後、メインで「この回答は wiki に保存すべきか？」の判断は通常通り行う

### クエリ計測（v0.22、必須）

`/llm-wiki q` の **総所要時間 + 主要フェーズ別所要時間** を毎回回答末尾に表示する。ユーザーが「最初のプロンプト → 最後の出力」のレイテンシ感を可視化するため。

**手順**:

1. クエリ受信直後の **最初の Bash 呼び出し** で `start`:
   ```bash
   ~/ObsidianVault/scripts/llm_wiki_q_timer.sh start
   ```
   他の grep / Read より前に実行する（種別判定の Bash と並列でも可）。

2. **各フェーズの完了時点で `mark <phase>`**。phase 名は短い英語スネークケース:
   - `manifest_grep` — `.query/manifest.jsonl` への grep
   - `summary_read` — `_summary.md` Read
   - `pages_read_<n>` — wiki ページ Read（複数件をまとめて 1 mark、n に件数）
   - `raw_grep` / `raw_read_<n>` — raw 配下の grep / Read
   - `subagent_<purpose>` — Agent tool 起動
   - `inetloc_gen` — `.inetloc` 自動生成
   - `answer_compose` — 回答整形（end の直前に打つと整形時間も可視化される）

3. **回答末尾の直前** で `end`、出力（コードブロック）を **そのまま回答の最後に貼る**:
   ```bash
   ~/ObsidianVault/scripts/llm_wiki_q_timer.sh end
   ```

出力例:
```
=== /llm-wiki q timing ===
phase                         step(s)
--------------------------------------
manifest_grep                    0.42
pages_read_3                    12.30
inetloc_gen                      0.31
--------------------------------------
total                           24.65
```

**注意**:
- Read tool 単独の所要時間は直接計測できない（LLM 内部処理）。**複数 Read を 1 mark にまとめる** ことで「Read バッチ + その間の LLM 推論時間」を間接捕捉する
- mark を打ちすぎると Bash 起動オーバーヘッド (~0.3s/回) で総時間が歪む。**fact/lookup は 1-2 mark、compare/synthesis は 3-6 mark** が目安
- `start` を忘れた場合、`mark` は警告のみで no-op、`end` は `[no-start]` を返す
- Query 以外の操作（ingest / lint）は計測対象外。並列フェーズ（Agent + Bash 同時実行等）も mark は直列で良い

### 経路ごとの Read 必須範囲

| 種別 | SKILL.md | CLAUDE.md | top index.md | genre _summary | genre index | manifest | 個別ページ |
|------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| fact | ✅ | ❌ | ❌ | ❌ | ❌ | △ (grep) | △ |
| lookup | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ (grep) | ✅ 1-3 件 |
| compare | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ (grep) | ✅ 2-4 件 |
| synthesis | ✅ | △ | △ | ✅ (1-3 ジャンル, ~2 KB ea) | △ | ✅ (grep) | ✅ 3-8 件 |
| **書き込みを伴う場合** (ingest/synthesis 保存/ページ更新/lint 適用) | ✅ | ✅ 必須 | ✅ | △ | ✅ | △ | ✅ |

- **CLAUDE.md は書き込みを伴う操作の前にのみ Read**。読み取り only の query では skip
- schema 履歴 v0.x の詳細は `CLAUDE.history.md` に分離済み（通常 Read 不要）

### manifest の使い方（最重要）

`~/ObsidianVault/llm-wiki/.query/manifest.jsonl` は **全ページを 1 行ずつ要約した検索インデックス**。ingest 時に `build_query_manifest.py` で自動再生成される。

1 行のスキーマ:

```json
{"path":"pages/ai/concepts/foo.md","genre":"ai","type":"concept","title":"Foo","aliases":["..."],"summary":"...","keywords":["..."],"sources":["..."],"updated":"YYYY-MM-DD","size":N}
```

**直接 Read しない**（316 KB ≒ 79K tokens で重い）。**必ず grep で絞り込む**:

```bash
# ジャンル絞り込み
grep '"genre":"ai"' ~/ObsidianVault/llm-wiki/.query/manifest.jsonl

# ジャンル × type
grep '"genre":"twitter"' ~/ObsidianVault/llm-wiki/.query/manifest.jsonl | grep '"type":"synthesis"'

# キーワード横断（title / aliases / keywords / summary すべてを通る）
grep -i 'karpathy' ~/ObsidianVault/llm-wiki/.query/manifest.jsonl

# 複数語の AND（2 段 grep）
grep '"genre":"ai"' ~/ObsidianVault/llm-wiki/.query/manifest.jsonl | grep -i 'claude'
```

絞り込んだエントリの `path` を見て、本当に読む必要があるページだけ Read する。

### Twitter 系 fact のショートカット

`raw/Twitter/<your-handle>/` には月別サマリ層がある（このパターンで運用している場合）。Twitter 系の問いはほぼここで決着する:

```bash
# 年単位の俯瞰
cat ~/ObsidianVault/raw/Twitter/<your-handle>/_yearly/2024.md

# キーワード横断（全アカウント × 全月）
grep -rln "<keyword>" ~/ObsidianVault/raw/Twitter/*/_summary/

# 特定月の詳細
~/ObsidianVault/raw/Twitter/<your-handle>/2015-09.md を Read
```

「いつ」「誰」「何回」型の質問では、まずこちらに直行する。

## 書き込みを伴う操作の規約参照

書き込み（ingest、ページ更新、synthesis 保存、lint 修正適用）の **前に必ず `~/ObsidianVault/llm-wiki/CLAUDE.md` を Read**。以下の判断基準は CLAUDE.md に集約済み:

- ページの作成・更新・分割の判断基準（新規ページ 3 条件、横断ページのタイミング 等）
- Query 保存判断基準（synthesis として保存すべき条件、デフォルト「保存しない」）
- 外部リポジトリ docs/ ingest 規約（機密境界、frontmatter 拡張、stale 検出）
- Ingest workflow の詳細手順（カテゴリ判定、ジャンル判定、entity/concept 作成、index/log 更新）

CLAUDE.md は schema_version で版管理されており、運用ルールの最新版がここにある。SKILL.md（このファイル）と矛盾した場合は CLAUDE.md を優先。

## 振る舞いの原則

- **raw/ は immutable**: 中身の編集・削除は不可。分類整理のための **移動（mv）は許可**
- **`~/repos/` 配下の md は編集・削除しない、自動 git pull もしない**（外部 repo は ingest 対象であって管理対象ではない）
- **大規模リファクタはユーザー確認を取る**: `pages/` の一括リネーム、複数ページの大規模書き換え等
- **矛盾を隠さない**: 新ソースが既存主張を覆すときは callout で両論併記
- **`confidential: true` ページの内容を `pages/work/` 以外のジャンルへ転記しない**（機密境界保持）
- **Lint 結果は提案として出し、適用はユーザー承認後**

## 初期セットアップ（wiki がまだ無いとき）

`references/setup.md` を参照。新規 wiki の作成手順、`index.md` / `log.md` のテンプレ、Obsidian 統合のヒント。

## 詳細リファレンス

- `references/operations.md` — Ingest / Query / Lint の具体的な手順とプロンプト例
- `references/setup.md` — 初期セットアップ、index.md / log.md テンプレ、Obsidian 統合
- `references/schema-template.md` — 新規 wiki 用の `CLAUDE.md` テンプレート
- `~/ObsidianVault/llm-wiki/CLAUDE.md` — 既存 wiki の現行 schema（書き込み時に Read、v0.19+）
- `~/ObsidianVault/llm-wiki/CLAUDE.history.md` — schema 履歴アーカイブ
- `~/ObsidianVault/llm-wiki/.query/manifest.jsonl` — query 用検索インデックス（grep 対象）

## 出典

Andrej Karpathy「LLM Wiki」（gist, 2026-04 頃）<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>。本スキルはこのアイデアを Claude Code + Obsidian + 上記固定配置向けに具体化したもの。
