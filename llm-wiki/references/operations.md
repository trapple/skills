# Operations: Ingest / Query / Lint

3 操作の具体的な手順。SKILL.md と併読すること。各操作は **必ず最後に `~/ObsidianVault/llm-wiki/log.md` へ追記** する。

固定パス前提：

- 生ソース: `~/ObsidianVault/raw/**`
  - **`raw/Clippings/`** — Web Clipper の保存先（未整理の受け皿、フラット）
  - **`raw/<Category>/`** — 整理済みカテゴリ（例: `raw/AI/`, `raw/Tech/`, `raw/Game/`, `raw/Finance/`）
- 運用: ingest 時に LLM がカテゴリ判断 → ユーザー承認 → `raw/Clippings/<file>` を `raw/<Category>/<file>` へ移動 → ingest 実行
- Wiki: `~/ObsidianVault/llm-wiki/{CLAUDE.md, index.md, log.md, pages/{entities,concepts,sources,syntheses}/**}`
- リンクは Obsidian の `[[wikilinks]]` 形式必須、frontmatter 必須
- **raw/ は immutable**: 中身の編集・削除は不可。分類整理のための **移動（mv）は許可**

---

## チャット出力時のリンク変換

**3 操作すべての横断ルール**。ユーザーへのチャット応答（query 回答 / ingest 報告 / lint 報告 / その他）で wiki ページや raw ソースに言及するときは、`[[Page Name]]` ではなく `.inetloc` ファイルへの `file://` 形式の markdown リンクに変換する。

### なぜこの形式か

Claude Code のターミナル UI は OSC 8 ハイパーリンクで `obsidian://` スキームを弾く（`https`/`file` のみ通る）。`.inetloc`（macOS Internet Location File）に `obsidian://` を埋めて `file://` リンクで開かせると、LaunchServices が中の `obsidian://` を解釈して Obsidian が起動する。これでチャット出力からワンクリックで対象ノートが開ける。

**wiki ファイル本体（`pages/**/*.md`, `index.md`, `log.md`, `raw/` 配下のソース要約等）には絶対に適用しない**。これらは `[[wikilinks]]` で書く——Obsidian の graph view・backlink・Quick Switcher が `file://.inetloc` を解決できず、wiki としての機能が壊れるため。

### 変換規則

チャット出力に書こうとした wikilink を、以下の形式に変換する：

| 元の wikilink | チャット出力での表記 |
|---|---|
| `[[Page Name]]` | `[Page Name](file://$HOME/ObsidianVault/.obsidian-links/Page%20Name.inetloc)` |
| `[[Path/To/Page\|Display]]` | `[Display](file://$HOME/ObsidianVault/.obsidian-links/Page.inetloc)` |
| `[[source-name]]`（raw 参照） | `[source-name](file://$HOME/ObsidianVault/.obsidian-links/source-name.inetloc)` |

`.inetloc` のファイル名はターゲットノートの **basename**（パス無し、拡張子無し）。ノート名はスペースを `%20` 等で URL エンコード。`$HOME` の部分は出力時に実行ユーザーの絶対ホームパス（例: `/Users/alice` や `/home/alice`）に展開すること（`file://` URI 仕様上、相対パスや `~` は使えない）。

### `.inetloc` 自動生成

ターゲットの `.inetloc` が無ければその場で生成する。

```bash
# 初回のみ
mkdir -p ~/ObsidianVault/.obsidian-links
```

ファイル `~/ObsidianVault/.obsidian-links/<Page Name>.inetloc` の中身：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>URL</key>
	<string>obsidian://open?vault=ObsidianVault&amp;file=<URL-encoded Page Name></string>
</dict>
</plist>
```

`obsidian://` の `file=` には URL エンコード済みのページ名を入れる。Obsidian は vault 全体でファイル名を一意解決するので、通常は basename だけで十分。同名衝突する場合のみ `file=<Category>%2F<Name>` のように相対パスを渡す。XML 中の `&` は `&amp;` にエスケープ必須。

### 運用上の注意

- **生成は lazy**: query 等で言及したページ分だけ作る。事前一括生成はしない
- **リネーム/削除追従は lint で**: ページがリネームされた場合 `.inetloc` は古い名前のまま残る。lint 時に `.obsidian-links/` の orphan を検出して提案する
- **`.obsidian-links/` は Obsidian で非表示**: ドット始まりのため Obsidian の File Explorer には出ない（git 管理対象外にする場合は `.gitignore` に追加）
- **ローカル運用前提**: `.inetloc` は macOS 専用。他 OS では別手段（無変換 or `_LinkName_` 斜体）が必要

---

## Ingest

新しいソースを wiki に統合する。1 ソースが平均で 5〜15 ページに波及する想定。

### 手順

1. **対象ソース確認**: ソースが `~/ObsidianVault/raw/Clippings/<name>.md`（受け皿）または `~/ObsidianVault/raw/<Category>/<name>.md`（整理済み）にあるか確認。Web Clipper で取り込んだものは `raw/Clippings/` にあるはず。ソースフォルダ外にしか無いものは、ユーザー確認の上で `raw/Clippings/` に配置する。
2. **カテゴリ分類**: 対象が `raw/Clippings/` にある場合、ファイル内容を読んでからカテゴリを判定し、`raw/<Category>/<name>.md` への移動を提案。ユーザー承認後に `mv` で移動してから ingest を継続する。schema 登録済みカテゴリに該当があればそれを使い、新カテゴリが必要なら schema に追記提案も同時に行う。既に `raw/<Category>/` にあれば省略。
2. **schema を読む**: 操作前に `~/ObsidianVault/llm-wiki/CLAUDE.md` を Read（CWD によっては自動ロードされない）。
3. **ソース全文を読む**: 長い場合は要点把握のため複数パスでもよい。
4. **要点をユーザーと対話**: 「このソースの中で wiki に載せるべき要点はどれか」を 3-5 個挙げ、ユーザーに方向を確認する。**ユーザーが「任せる」と言った場合は省略可**。
5. **ソース要約ページを生成**: `~/ObsidianVault/llm-wiki/pages/sources/<YYYY-MM-DD> <Title>.md`
   - **frontmatter（必須）**:
     ```yaml
     ---
     tags: [source, <topic>]
     created: YYYY-MM-DD
     updated: YYYY-MM-DD
     source: "[[<name>]]"
     authors: [<...>]
     entities: ["[[Alice]]", "[[Acme Corp]]"]
     concepts: ["[[RAG]]", "[[LLM Wiki Pattern]]"]
     ---
     ```
   - 構成: 冒頭 1 段落の要旨 → 主要主張の箇条書き → 引用（短く） → 派生して更新／新設したページ一覧（`[[wikilinks]]`）
6. **影響を受けるページを更新**:
   - 既存 entity ページ：新事実・引用を該当節に追加。文末に `（参照: [[<source-name>]]）`（衝突時のみ `[[<Category>/<name>|<title>]]`）
   - 既存 concept ページ：主張が補強される／覆る／拡張されるなら反映。**矛盾は callout で残す**：
     ```markdown
     > [!warning] 矛盾
     > [[source-A]] と [[source-B]] で主張が割れている。現時点の暫定解は…
     ```
   - 該当 entity / concept のページが無ければ新設（必要十分な範囲で。判断基準は次節）
7. **相互リンクを張る**: 新規ページから既存ページ、既存ページから新規ページ、双方向に `[[wikilinks]]` を入れる。orphan を作らない。各ページ末尾に `## See also` セクションを設けるとリンク密度が安定する。
8. **`index.md` を更新**: 新規ページを該当セクションに 1 行で追記（`- [[Page Name]] — 1 行説明`）。frontmatter の `updated` を当日に。
9. **`log.md` に append**:
   ```markdown
   ## [YYYY-MM-DD] ingest | <ソースタイトル>
   - Source: [[<name>]]
   - New pages: [[X]], [[Y]]
   - Updated: [[Z]]（理由を 1 行）, [[Index]]
   - Notes: <発見した矛盾や TODO があれば>
   ```
10. **ユーザーに報告**: 1 行目に骨格（「N 新規 / M 更新 / 矛盾 K 件」）、その後に詳細を 3-5 行。

### 失敗パターンと対策

- **要約に終始して既存ページを更新しない** → ソース要約だけ作って終わると wiki が育たない。手順 6 を必ず通る
- **新規ページの乱立** → 「1 ソースに 1 entity」になりがち。**そのページが今後 3 回以上参照される見込みがあるか**を判断基準にする。無ければ既存ページの 1 節として書く
- **frontmatter 抜け** → Dataview 集計が壊れる。テンプレを毎回踏襲
- **`[text](path.md)` 記法を使う** → Obsidian の backlink/graph が解決しない。`[[wikilinks]]` 必須

---

## Query

ユーザーから wiki への問い合わせ。回答が良ければ wiki に再ファイルする。

### 手順

1. **schema を読む**: `~/ObsidianVault/llm-wiki/CLAUDE.md` を Read。
2. **`index.md` を最初に読む**: 関連ページ候補を 3-7 個に絞る。embedding 検索は不要、index がインデックス。
3. **候補ページを読む**: 必要なら `raw/Clippings/` 配下のソースまで遡る。引用は出典付きで取る。
4. **回答を作る**: 形式は質問次第——
   - 短答 → チャットに直接（出典は `[[wikilinks]]`）
   - 比較 → markdown 表
   - 全体像 → 1 ページの synthesis
   - 提案資料 → Marp スライド（`pages/syntheses/` 配下に）
   - データ → matplotlib チャート
5. **回答を wiki にファイルする判断**: 以下のいずれかなら `~/ObsidianVault/llm-wiki/pages/syntheses/<YYYY-MM-DD> <slug>.md` として保存し、`index.md` の Syntheses 節に追記：
   - 比較・分析・統合に **30 秒以上** かけた
   - 同じ問いが将来また来そう
   - 既存ページに含まれない新しい接続を見つけた
   - ユーザーが「これは残しておきたい」と言った

   synthesis ページの frontmatter：
   ```yaml
   ---
   tags: [synthesis, <topic>]
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   question: "<元の質問を 1 行で>"
   used_pages: ["[[A]]", "[[B]]"]
   ---
   ```
6. **`log.md` に append**:
   ```markdown
   ## [YYYY-MM-DD] query | <質問の要約>
   - Used: [[A]], [[B]]
   - Filed answer to: [[<synthesis page>]]（保存した場合のみ）
   ```

### 失敗パターンと対策

- **`raw/` を直接探しに行く** → wiki 層を素通りする悪手。必ず index → pages の順で辿る。ソース本体は最後の手段
- **回答が良かったのにチャット履歴に消える** → 手順 5 を毎回判断する習慣を
- **チャット応答にそのまま `[[wikilinks]]` を書く** → クリックで開けない。本ファイル冒頭「チャット出力時のリンク変換」に従って `.inetloc` への `file://` リンクに変換する
- **synthesis ページ等の wiki 本体に `file://.inetloc` を書く** → Obsidian の graph/backlink が壊れる。wiki に保存する内容内のリンクは `[[wikilinks]]` 必須

---

## Lint

定期的な健康診断。ユーザーが「lint」「掃除」「健全性チェック」と言ったら、または ingest が 10〜20 件たまったタイミングで実施を提案。

### チェック項目

1. **Orphans**: どこからもリンクされていない `pages/` 配下のファイル。検出例：
   ```bash
   # pages 配下の全ノートに対し、index.md と他ページからの被リンクを確認
   ls ~/ObsidianVault/llm-wiki/pages/**/*.md | while read f; do
     name=$(basename "$f" .md)
     count=$(grep -rl "\[\[$name" ~/ObsidianVault/llm-wiki | grep -v "/$name.md$" | wc -l)
     [ "$count" -eq 0 ] && echo "ORPHAN: $f"
   done
   ```
2. **Stale claims**: 新ソース（`log.md` の最新数件）と既存 concept ページの主張を照らし合わせ、覆されている／補強されている主張を検出。
3. **Missing pages**: 複数ページから言及されているが、実ファイルが無い `[[wikilink]]`。Obsidian の "Unresolved links" 機能でも見える。
4. **Cross-reference gaps**: 同じ entity/concept を扱う 2 ページが互いにリンクしていない箇所。
5. **Duplicates**: 同じ事項を別名で書いた複数ページ（例: `RAG.md` と `Retrieval Augmented Generation.md`）。統合候補を提案。
6. **Index drift**: `index.md` の記載と実ファイルの差分。新ページが index に無い／index にあるが実ファイルが消えている。
7. **Data gaps**: ページ内に「TODO」「要検証」「不明」が残っている箇所。Web 検索や追加ソース読み込みで埋める提案。
8. **Frontmatter 欠損**: `tags`, `created`, `updated`, ページ種別固有フィールド（sources の `source`、syntheses の `question` 等）が抜けているページ。
9. **`.obsidian-links/` の orphan**: `~/ObsidianVault/.obsidian-links/*.inetloc` のうち、対応する wiki ページ／raw ソースが存在しないもの（リネーム・削除に取り残された残骸）。削除提案を出す。

### 出力形式

修正は **提案として出し、ユーザー確認後に適用**。勝手にページを削除・統合しない。

```markdown
# Lint report — [YYYY-MM-DD]

## Orphans (3)
- [[Bob]] — どこからもリンクされていない。削除 or [[Project X]] からリンクを張る
- ...

## Stale (1)
- [[RAG]] の「埋め込み次元は 1024 が標準」 → [[2026-04 New Embedding Model]] で 4096 が一般化していると判明。書き換え案を提示
- ...

## Missing pages (2)
- [[Y]] が 3 ページから参照されているが実ファイル無し。新設候補

## Index drift
- 新ページ [[Z]] が index に未登録
- index にあるが実ファイル無し: [[Old Page]]

...
```

### `log.md` への記録

```markdown
## [YYYY-MM-DD] lint
- Findings: orphans=3, stale=1, missing=2, dup=1
- Applied: orphan [[Bob]] を [[Project X]] からリンク, stale [[RAG]] を更新
- Deferred: dup 候補の統合はユーザー判断待ち
```

---

## 横断的な原則

- **副作用は最小単位で**: 1 つの操作で触るファイル群を「何を、なぜ」セットで `log.md` に残す。後から追跡可能にする
- **ユーザーへの報告は件数を先に**: 「3 ページ新設 / 5 ページ更新 / 矛盾 1 件」を冒頭に。詳細はその後
- **CLAUDE.md（schema）の更新を恐れない**: ワークフローが変化したら schema を改訂する。schema が陳腐化すると wiki も陳腐化する
- **すべてのリンクは `[[wikilinks]]`**: markdown link `[](path)` は外部 URL のみに使う
