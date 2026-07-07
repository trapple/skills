# Operations: Ingest / Query / Lint

3 操作の具体的な手順。SKILL.md と併読すること。既存 wiki では `~/ObsidianVault/llm-wiki/CLAUDE.md`（schema）が最優先 — 本ファイルと矛盾したら CLAUDE.md に従う。

固定パス前提：

- 生ソース: `~/ObsidianVault/raw/**`
  - **`raw/Clippings/`** — Web Clipper の保存先（未整理の受け皿、フラット）
  - **`raw/<Category>/`** — 整理済みカテゴリ（例: `raw/AI/`, `raw/Tech/`, `raw/VFX/`）
- Wiki: `~/ObsidianVault/llm-wiki/{CLAUDE.md, index.md, pages/<genre>/{index.md, log.md, _summary.md, entities/, concepts/, sources/, syntheses/}}`
- リンクは Obsidian の `[[wikilinks]]` 形式必須、frontmatter 必須
- **raw/ は immutable**: 中身の編集・削除は不可。分類整理のための **移動（mv）は許可**
- ログは **ジャンル log**（`pages/<genre>/log.md`）に書く。ingest / lint は毎回、query は synthesis を保存したときのみ

---

## チャット出力時のリンク変換

**3 操作すべての横断ルール**。ユーザーへのチャット応答（query 回答 / ingest 報告 / lint 報告 / その他）で wiki ページや raw ソースに言及するときは、`[[Page Name]]` ではなく `.inetloc` ファイルへの `file://` 形式の markdown リンクに変換する。

### なぜこの形式か

Claude Code のターミナル UI は OSC 8 ハイパーリンクで `obsidian://` スキームを弾く（`https`/`file` のみ通る）。`.inetloc`（macOS Internet Location File）に `obsidian://` を埋めて `file://` リンクで開かせると、LaunchServices が中の `obsidian://` を解釈して Obsidian が起動する。

**wiki ファイル本体（`pages/**/*.md`, `index.md` 等）には絶対に適用しない**。これらは `[[wikilinks]]` で書く——Obsidian の graph view・backlink が `file://.inetloc` を解決できず、wiki としての機能が壊れるため。

### 変換規則

| 元の wikilink | チャット出力での表記 |
|---|---|
| `[[Page Name]]` | `[Page Name](file://$HOME/ObsidianVault/.obsidian-links/Page%20Name.inetloc)` |
| `[[Path/To/Page\|Display]]` | `[Display](file://$HOME/ObsidianVault/.obsidian-links/Page.inetloc)` |
| `[[source-name]]`（raw 参照） | `[source-name](file://$HOME/ObsidianVault/.obsidian-links/source-name.inetloc)` |

`.inetloc` のファイル名はターゲットノートの **basename**（パス無し、拡張子無し）。ノート名はスペースを `%20` 等で URL エンコード。`$HOME` は実行ユーザーの絶対ホームパスに展開すること（`file://` URI では `~` 不可）。

### `.inetloc` の生成

**wiki 全ページ分は `update_indexes.py` が事前生成する**ので、query 時に生成が必要になるのは raw ソース等の wiki 外ノートだけ。無ければその場で生成:

```bash
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

`file=` には URL エンコード済みページ名。Obsidian は vault 全体でファイル名を一意解決するので通常 basename で十分（衝突時のみ `file=<Category>%2F<Name>`）。XML 中の `&` は `&amp;` にエスケープ必須。

- **リネーム/削除追従は lint で**: `.obsidian-links/` の orphan を検出して削除提案
- **ローカル運用前提**: `.inetloc` は macOS 専用

---

## Ingest

新しいソースを wiki に統合する。1 ソースが平均で 5〜15 ページに波及する想定。詳細な判断基準（新規ページ 3 条件・横断ページ等）は CLAUDE.md。

### 手順

1. **schema を読む**: `~/ObsidianVault/llm-wiki/CLAUDE.md` を Read（書き込みを伴う操作の前は必須）
2. **対象ソース確認 + カテゴリ分類**: `raw/Clippings/` にある場合、内容からカテゴリ判定 → `raw/<Category>/<name>.md` への移動を提案 → 承認後 `mv`。既に `raw/<Category>/` にあれば省略
3. **ソース全文を読む**
4. **要点をユーザーと対話**: 「このソースの中で wiki に載せるべき要点はどれか」を 3-5 個挙げ、ユーザーに方向を確認する。**ユーザーが「任せる」と言った場合は省略可**
5. **ソース要約ページを生成**: `pages/<genre>/sources/<YYYY-MM-DD> <Title>.md`（frontmatter 規約は CLAUDE.md）。構成: 冒頭 1 段落の要旨 → 主要主張の箇条書き → 短い引用 → 派生して更新／新設したページ一覧
6. **影響を受けるページを更新**: 既存 entity/concept へ新事実追加（`（参照: [[<source-name>]]）` 付き）、矛盾は callout で両論併記、無ければ新設（判断基準は CLAUDE.md「ページの作成・更新・分割の判断基準」）
7. **相互リンクを張る**: 双方向 `[[wikilinks]]`、各ページ末尾に `## See also`。orphan を作らない
8. **ジャンル `log.md` に append**:
   ```markdown
   ## [YYYY-MM-DD] ingest | <ソースタイトル>
   - Source: [[<name>]]
   - New pages: [[X]], [[Y]]
   - Updated: [[Z]]（理由を 1 行）
   - Notes: <発見した矛盾や TODO があれば>
   ```
9. **インデックス一括更新（1 コマンド）**:
   ```bash
   python3 ~/ObsidianVault/scripts/update_indexes.py
   ```
   manifest / pages.tsv / ジャンル index.md / _summary.md / .inetloc を増分再生成する。**ジャンル index.md への手動追記は不要**
10. **ユーザーに報告**: 1 行目に骨格（「N 新規 / M 更新 / 矛盾 K 件」）、その後に詳細を 3-5 行

### 失敗パターンと対策

- **要約に終始して既存ページを更新しない** → ソース要約だけ作って終わると wiki が育たない。手順 6 を必ず通る
- **新規ページの乱立** → 「そのページが今後 3 回以上参照される見込みがあるか」を判断基準にする。無ければ既存ページの 1 節として書く
- **frontmatter 抜け** → manifest / Dataview 集計が壊れる。テンプレを毎回踏襲
- **`[text](path.md)` 記法を使う** → `[[wikilinks]]` 必須
- **update_indexes.py を忘れる** → manifest が陳腐化して query 精度が落ちる。ingest の最後に必ず実行

---

## Query

ユーザーから wiki への問い合わせ。**デフォルトは読み取りのみ・儀式なし**（経路分岐と原則は SKILL.md）。

### 手順

1. **種別判定**（fact / lookup / compare / synthesis / source — SKILL.md の表）
2. **grep で候補を絞る**: manifest（wiki 内）または raw のサマリ層（fact 系）。CLAUDE.md やトップ index.md は読まない
3. **候補ページを読む**: 1-3 件（synthesis は 3-8 件、5+ なら subagent へ）。必要なら raw まで遡る。引用は出典付きで
4. **回答を作る**: 短答はチャット直、比較は表、全体像は 1 ページの synthesis
5. **保存判断**（基準は CLAUDE.md「Query 保存判断基準」）: **保存推奨(✅) or グレー(⚠) のときのみ** 回答末尾に 💾 提案フッターを付ける。保存不要(❌)なら何も付けずに終わる
6. **保存が承認された場合のみ**: `pages/<genre>/syntheses/<YYYY-MM-DD> <slug>.md` に保存 → ジャンル `log.md` に query エントリを append → `python3 ~/ObsidianVault/scripts/update_indexes.py`

### synthesis 用 subagent パターン

5 ページ以上の Read + 統合が必要なとき、Agent tool で Sonnet subagent に Read と一次まとめを委譲する。メインは判断・整形に専念:

```
description: "同ジャンル sources N 件の Read + 集計"
subagent_type: "general-purpose"
model: "sonnet"
prompt: |
  以下のファイルを順次 Read して、各エントリの日付・主要メタ情報・要点を
  マークダウン表（日付 / 主要メタ列 / 特記事項）にまとめて返してください。
  引用は最小限、200 行以内。
  - <絶対パスのリスト>
```

注意: subagent はメインのコンテキストを継承しない（前提・パスは prompt に全部埋める）。5 ページ未満なら直接 Read の方が速い。矛盾検出・機微情報の判断は subagent に委ねずメインが行う。

### クエリ計測 (timer) — オプトイン

ユーザーが「計測して」「timing」「遅い」等と言ったときのみ実施:

1. 最初の Bash で `~/ObsidianVault/scripts/llm_wiki_q_timer.sh start`
2. フェーズ完了ごとに `mark <phase>`（`manifest_grep` / `pages_read_<n>` / `raw_read_<n>` / `subagent_<purpose>` / `answer_compose` 等。fact/lookup は 1-2 mark、synthesis は 3-6 mark）
3. 回答末尾の直前で `end` → 出力コードブロックをそのまま回答末尾に貼る

Read 単体の時間は計測不能なので複数 Read を 1 mark にまとめて間接捕捉する。mark しすぎは Bash 起動 (~0.3s/回) で総時間が歪む。

### 失敗パターンと対策

- **`raw/` を直接探しに行く**（fact 以外で） → wiki 層を素通りする悪手。manifest → pages の順。ソース本体は最後の手段
- **チャット応答にそのまま `[[wikilinks]]` を書く** → クリックで開けない。`.inetloc` への `file://` リンクに変換
- **保存しないのに log 追記や保存フッターを付ける** → 読み取り query に書き込み儀式は付けない（v0.23）
- **synthesis ページ等の wiki 本体に `file://.inetloc` を書く** → graph/backlink が壊れる。wiki 内リンクは `[[wikilinks]]` 必須

---

## Lint

定期的な健康診断。ユーザーが「lint」「掃除」「健全性チェック」と言ったら、または ingest が 15 件たまったタイミングで実施を提案。

### チェック項目

1. **Orphans**: どこからもリンクされていない `pages/` 配下のファイル
2. **Stale claims**: 新ソースと既存 concept ページの主張の食い違い
3. **Missing pages**: 参照されているが実ファイルが無い `[[wikilink]]`（Obsidian の "Unresolved links" でも見える）
4. **Cross-reference gaps**: 相互リンクすべき 2 ページが繋がっていない
5. **Duplicates**: 同じ事項を別名で書いた複数ページ → 統合候補を提案
6. **Index drift**: `index.md` と実ファイルの差分（ジャンル index は update_indexes.py 再実行でほぼ解消）
7. **Data gaps**: 「TODO」「要検証」「不明」が残っている箇所
8. **Frontmatter 欠損**: `tags` / `created` / `updated` / 種別固有フィールドの欠け
9. **`.obsidian-links/` の orphan**: 対応する wiki ページ／raw ソースが存在しない `.inetloc`（リネーム・削除の残骸）→ 削除提案
10. **stale_external**: external_repo source の `source_sha` と現在 HEAD の差分（`git -C <repo> log --oneline <sha>..HEAD -- <rel>`）→ 再 ingest 候補

### 出力形式

修正は **提案として出し、ユーザー確認後に適用**。勝手にページを削除・統合しない。

```markdown
# Lint report — [YYYY-MM-DD]

## Orphans (3)
- [[Bob]] — どこからもリンクされていない。削除 or [[Project X]] からリンクを張る

## Stale (1)
- [[RAG]] の「…」 → [[2026-04 New Embedding Model]] で覆っている。書き換え案を提示

## Index drift
- ...
```

### log への記録

ジャンル横断 lint は `pages/meta/log.md`、1 ジャンル限定なら該当ジャンル log に:

```markdown
## [YYYY-MM-DD] lint
- Findings: orphans=3, stale=1, missing=2, dup=1
- Applied: ...
- Deferred: ...
```

修正適用でページ追加・削除・frontmatter 変更があった場合は最後に `python3 ~/ObsidianVault/scripts/update_indexes.py`。

---

## 横断的な原則

- **副作用は最小単位で**: 1 つの操作で触るファイル群を「何を、なぜ」セットでジャンル log に残す
- **ユーザーへの報告は件数を先に**: 「3 ページ新設 / 5 ページ更新 / 矛盾 1 件」を冒頭に
- **CLAUDE.md（schema）の更新を恐れない**: ワークフローが変化したら schema を改訂する
- **すべての内部リンクは `[[wikilinks]]`**: markdown link `[](path)` は外部 URL のみ
