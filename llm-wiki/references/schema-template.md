# Schema Template — `~/ObsidianVault/llm-wiki/CLAUDE.md`

新規 wiki を作るときに、この内容をベースに `~/ObsidianVault/llm-wiki/CLAUDE.md` を生成する。**そのままコピーで終わらせず、ユーザーと対話して `<...>` 部分を埋めること**。Schema は wiki と一緒に共進化する生きた文書。

---

```markdown
# <Wiki 名> — Schema

> このファイルは LLM（Claude Code）が `~/ObsidianVault/llm-wiki/` を維持するための規約集。
> 操作のたびに最初に読むこと。Claude Code の CWD が Vault ルートだと自動ロードされないので、明示的に Read する。
> 規約が現実と合わなくなったら、ユーザーと相談して更新する。

## この wiki は何か

- **目的**: <例: Web Clipper で集めた多様な記事の継続的な整理／LLM・AI 関連の知識ベース／読書 companion>
- **読者**: <例: 自分だけ／チーム／公開予定>
- **対象期間**: <例: 2026 年通年／無期限>
- **完成形のイメージ**: <例: 数百ページ規模の相互リンクされた markdown 群、Obsidian graph で星雲状になる>

## 固定パス（このスキル全体の前提）

```
~/ObsidianVault/
├── raw/                       # 全ソースのルート（immutable）
│   ├── Clippings/             # Web Clipper 保存先（未整理の受け皿）
│   ├── AI/                    # 整理済みカテゴリ（例）
│   ├── Tech/
│   └── ...
└── llm-wiki/                  # この wiki
    ├── CLAUDE.md              # このファイル
    ├── index.md
    ├── log.md
    └── pages/
        ├── entities/
        ├── concepts/
        ├── sources/
        └── syntheses/
```

サブディレクトリ（entities/concepts/sources/syntheses）は出発点で、対象ドメインに合わせて増減してよい（例: `pages/papers/`, `pages/timelines/`）。

## ソース場所

LLM は `~/ObsidianVault/raw/` 配下のみを「生ソース」として読む。これ以外の Vault 内ノートは原則無視（手動指示があれば例外）。

- **`raw/Clippings/`** — Obsidian Web Clipper の保存先（未整理の受け皿、フラット）
- **`raw/<Category>/`** — 整理済みカテゴリ。本 wiki で使う命名例：
  - <例: `raw/AI/` — LLM, AI, MCP, エージェント関連>
  - <例: `raw/Tech/` — 一般技術、ファイル形式、ネットワーク>
  - <例: `raw/Game/`, `raw/Finance/`, `raw/Hardware/` 等>

新しいカテゴリを追加するときは、このセクションへ列挙し、`log.md` に `## [YYYY-MM-DD] schema | added category raw/Foo/` で記録する。

## カテゴリ分類フロー

`raw/Clippings/` にフラットに溜まった記事は、ingest 時に LLM がファイル内容からカテゴリを判定して `raw/<Category>/` への移動を提案。ユーザー承認後に `mv` で移動してから ingest 本体を実行する。Obsidian の `[[wikilink]]` はファイル名解決なので、フォルダ移動でリンクは切れない。

## ページ命名規則

- **entities/**: `<正規名>.md`（例: `Geoffrey Hinton.md`, `OpenAI.md`）。別名は frontmatter の `aliases` に書く
- **concepts/**: `<英名 or 日本語名>.md`（混在しないよう統一）
- **sources/**: `<YYYY-MM-DD> <Title>.md`（投稿日 or 取り込み日）
- **syntheses/**: `<YYYY-MM-DD> <slug>.md`

ファイル名は Obsidian の `[[wikilink]]` 解決キーになる。**Vault 全体で一意になるよう** 命名し、衝突しそうなら path 付き表記 `[[pages/concepts/RAG|RAG]]` で参照する。

## frontmatter 規約（必須）

全ページ共通：

```yaml
---
tags: [<カテゴリ>, ...]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

ページ種別ごとの追加フィールド：

- **sources/**:
  ```yaml
  source: "[[<source-name>]]"           # raw/ 配下のファイル名（path-less wikilink）
  source_url: "https://..."             # 元 URL
  authors: [<...>]
  published: YYYY-MM-DD
  entities: ["[[Alice]]", ...]
  concepts: ["[[RAG]]", ...]
  ```
- **entities/** & **concepts/**:
  ```yaml
  aliases: [<別名 1>, <別名 2>]
  sources: ["[[<source-name>]]", ...]   # このページの主張の根拠となる raw/ 一覧
  ```
- **syntheses/**:
  ```yaml
  question: "<元の質問を 1 行で>"
  used_pages: ["[[A]]", "[[B]]"]
  ```

## Wikilinks 規約（必須）

- 内部 wiki ページ: `[[Page Name]]`（一意なら短く） / `[[pages/concepts/RAG|RAG]]`（衝突回避）
- 生ソース: `[[<source-name>]]`（raw/ 配下のファイル名が一意なら path 不要、整理によるフォルダ移動でリンクは切れない）/ `[[<Category>/<source>|<title>]]`（衝突時のみ path 明示）
- 外部 URL のみ markdown 形式 `[text](https://...)`
- `[text](path.md)` 形式は **使わない**（Obsidian の backlink/graph が解決しないため）

## ワークフロー: Ingest

<デフォルトを明示。例:>

1. ソースが `~/ObsidianVault/raw/Clippings/<name>.md`（受け皿）または `~/ObsidianVault/raw/<Category>/<name>.md`（整理済み）にあるか確認
2. このファイル（schema）を Read
3. 全文を読み、要点 3-5 個をユーザーに口頭で示し方向確認（"任せる"なら省略）
4. **カテゴリ判定 + 移動**: `raw/Clippings/` にあった場合、内容からカテゴリを判定して `raw/<Category>/<name>.md` への移動を提案。ユーザー承認後に `mv`
5. `pages/sources/<...>` を生成（前述 frontmatter 込み）
6. 新規 entity / concept ページの作成と既存ページ更新（矛盾は callout で残す）
7. 双方向 `[[wikilinks]]` を張る。ページ末尾に `## See also`
8. `index.md` の該当節に追記、`updated` を更新
9. `log.md` に `## [YYYY-MM-DD] ingest | <タイトル>` のエントリを append（移動先カテゴリも記録）
10. ユーザーへ「N 新規 / M 更新 / 矛盾 K 件」形式で報告

## ワークフロー: Query

1. このファイル（schema）を Read
2. `index.md` から関連ページを絞り込む（3-7 個）
3. ページを読む。必要なら `raw/<Category>/` 配下のソースまで
4. 出典付きで回答（`[[wikilinks]]` 形式）
5. 30 秒以上の合成・新しい接続発見・将来再利用見込みのいずれかなら `pages/syntheses/` に保存し index に追記
6. `log.md` に `## [YYYY-MM-DD] query | <要約>` を append

## ワークフロー: Lint

トリガー: ユーザー発話「lint / 掃除 / 健全性チェック」、または ingest が <例: 15> 件たまった時に提案。

チェック項目: orphan / stale / missing / cross-ref gap / duplicate / index drift / data gap / frontmatter 欠損。

修正は提案として出し、ユーザー承認後に適用。`log.md` に findings と applied/deferred を記録。

## やらないこと

- `~/ObsidianVault/raw/` 配下の中身の編集・削除（immutable）。ただし分類整理のための移動（`raw/Clippings/` → `raw/<Category>/`）は許可
- `pages/` の大規模リファクタや一括リネームをユーザー確認なしで行う
- 矛盾や TODO を「綺麗にするため」削除する（必ず明示として残す）
- 出典の無い主張を新規ページに書く
- markdown link `[](path)` 形式での内部リンク（Obsidian の機能が活きない）

## 報告フォーマット

ユーザーに対する操作後の報告は、**1 行目に件数の骨格**、その後に詳細：

> 3 ページ新設 / 5 ページ更新 / 矛盾 1 件 / log.md 追記済み
>
> - 新設: [A](file:///.../A.inetloc), [B](file:///.../B.inetloc), [C](file:///.../C.inetloc)
> - 更新: [D](file:///.../D.inetloc)（理由）, ...
> - 矛盾: [E](file:///.../E.inetloc) と [F](file:///.../F.inetloc) の主張が割れている

**チャット応答内のリンクは `.inetloc` への `file://` 形式**（クリックで Obsidian が起動）。wiki ファイル本体（`pages/`, `index.md`, `log.md`）に書くリンクは従来通り `[[wikilinks]]`。詳細は `~/.claude/skills/llm-wiki/references/operations.md` の「チャット出力時のリンク変換」を参照。

## このスキーマの版

- v0.1 (YYYY-MM-DD) 初版
- 改訂は `log.md` に `## [YYYY-MM-DD] schema | <変更要約>` で記録する
```

---

## 埋めるとき意識すること

- **「この wiki は何か」セクションを舐めない**: ここが曖昧だと LLM の判断が揺れる。1 行で済ませず、目的・読者・完成形を具体的に書く
- **サブディレクトリ命名は対象ドメイン優先**: `entities/concepts/sources/syntheses` は出発点。論文サーベイなら `papers/methods/datasets/benchmarks` の方が自然なこともある
- **frontmatter のフィールドは「Dataview で集計したい軸」から逆算**: tags だけ機械的に増やしても活きない
- **Ingest 手順 step 3「方向確認」の閾値はユーザー次第**: 全件確認したい人もいれば、信頼して任せたい人もいる。明示しておく
- **「やらないこと」リストはユーザーの懸念を反映**: 「画像を勝手に圧縮しないで」「raw を絶対に move しないで」など個別の制約があれば足す
