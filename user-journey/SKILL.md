---
name: user-journey
description: プロジェクトの重要な要件・ユーザージャーニーを SQLite (data/user_journey.db) に短文で蓄積したナレッジベースを検索・追加する。**設計ドキュメントを書く前 / コード実装に着手する前 / 仕様判断に迷ったときに必ず関連キーワードで検索し、過去にユーザーが表明した要件と整合を取る**。ユーザーが新しい仕様・制約・ルールを表明したときは、要約して 1 レコードとして追加する (追加は write 操作なので必ずユーザーの許可を得る)。Use when user says "要件確認", "ジャーニー検索", "user_journey", "ユーザージャーニー", "○○の要件は", "○○の方針は", "user-journey", or when starting design / implementation work on any feature in this project.
---

# user-journey

このプロジェクトの「ユーザーが繰り返し参照したい重要な要件・制約・ルール」を、
SQLite (`data/user_journey.db`) に短文で蓄積したナレッジベース。
仕様判断の根拠として AI と人間が共通参照する。**コミット対象**。

## なぜあるか

- 同じ要件を複数の場面で何度も確認するのを避ける
- 設計書 (`docs/`) や `DESIGN.md` に書くほどではない短い前提を集約する
- キーワード検索で「過去にユーザーが何を言っていたか」を瞬時に引ける

## いつ使うか (必須)

- **設計ドキュメントを書く前** → 関連キーワードで検索し、矛盾しないか確認
- **コード実装に着手する前** → 同上
- **仕様判断に迷ったとき** → ルール化された要件がないか確認
- **ユーザーが新しい仕様・制約・ルールを表明したとき** → 追加 (write 操作なので要許可)

## スキーマ

```sql
CREATE TABLE user_journey (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  text TEXT NOT NULL
);
```

## 操作

### 検索 (read - 許可不要)

単一キーワード:

```sh
sqlite3 data/user_journey.db "SELECT id, text FROM user_journey WHERE text LIKE '%<keyword>%'"
```

複数キーワード AND（例: 「Spotify でシングル優先のルール」を引き出す）:

```sh
sqlite3 data/user_journey.db "SELECT id, text FROM user_journey WHERE text LIKE '%Spotify%' AND text LIKE '%シングル%'"
```

複数キーワード OR（例: 「Apple Music か YouTube Music への言及」を集める）:

```sh
sqlite3 data/user_journey.db "SELECT id, text FROM user_journey WHERE text LIKE '%Apple Music%' OR text LIKE '%YouTube Music%'"
```

### 全件列挙 (read - 許可不要)

```sh
sqlite3 data/user_journey.db "SELECT id, text FROM user_journey ORDER BY id"
```

### 検索結果の返し方

ヒット件数によって user への提示の粒度を変える。長文の貼り付けは避け、id 付きで簡潔に。

- **0 件**: 「該当する既存要件はありません。新しい仕様として追加候補か確認します」と伝え、
  ユーザーが新ルールを表明している文脈なら追加 (write) の提案フローに進む。
- **1〜3 件**: 各レコードの `id` と `text` をそのまま箇条書きで提示。
  ```
  関連する既存要件:
  - id 7: Spotifyでシングルとアルバムに同じ曲がある場合はシングルを採用する
  - id 8: Spotifyで日本語版と英語版がある曲は基本的に日本語版を採用
  ```
- **4〜9 件**: 件数を伝えて重要度の高い 3〜5 件だけ抜粋、残りは「他 N 件」と要約。
  ユーザーが全件を求めたら追加で列挙する。
- **10 件以上**: フラットな抜粋では情報が落ちすぎるので、**カテゴリ別に整理して提示してよい**
  （例: 「スコープ系 3 件 / データ管理 2 件 / 設計原則 5 件 / ...」）。
  - **件数の方針**: カテゴリ別整理なら **全件提示してよい**（落とすと設計判断材料が欠落するため）。
    ただし関連度が極端に低いカテゴリは「他 N 件（rate limit 詳細など）」と要約で省略可。
  - **カテゴリ内の順序**: 重要度の高いものから並べる。
  - **カテゴリ間の順序**: 重要度の高いカテゴリを先頭に。設計着手前なら
    `スコープ・運用境界 → 主要フロー / 骨格 → ドメインルール → データ管理 → 認証・前提 → エラー詳細`
    の順が標準。仕様変更・追加時は **「矛盾しうるカテゴリ」を最優先** に並べ替える。
- **重要度の判定基準**: 「現在のタスクへの関連度」。
  - 設計着手前なら「フェーズ構造・主要 I/F・スコープ境界」が高、周辺の運用詳細（rate limit
    アルゴリズム、エラー code 等）は低。
  - 新仕様の追加・変更時なら「矛盾しうる既存ルール」が最優先。
  - 迷ったら「user が次の判断に使う情報か？」で切り分ける。
- いずれの場合も検索に使ったキーワードを 1 行で添えて「他にどの語で引きたいか」を
  ユーザーが指示しやすくする。

### 追加 (write - 必ずユーザーの許可を得てから)

ユーザーが新しい要件を表明したら、以下のフローで進める:

1. **要約案を提示** — AskUserQuestion で確認する。標準テンプレ:
   ```json
   {
     "header": "user_journey 追加",
     "question": "○○ に関する要件として『<要約文>』を追加してよいですか？",
     "options": [
       { "label": "はい、この文面で追加", "description": "提示した要約文のまま INSERT を実行" },
       { "label": "文面を直したい",       "description": "要約文を修正してから追加（差し戻し）" },
       { "label": "追加しない",           "description": "今回はナレッジベースに残さない" }
     ]
   }
   ```
2. **承諾されたら INSERT** を実行（`RETURNING id` で新 id を同時取得）:
   ```sh
   sqlite3 data/user_journey.db "INSERT INTO user_journey(text) VALUES('<短文 1〜2 文の要件>') RETURNING id"
   ```
   `RETURNING` が使えない古い SQLite なら別途 `SELECT last_insert_rowid()` で取得。
3. **新 id を user に報告** — 「id N として登録しました」と返す。後で他文書から参照しやすい。

text の規約 (それぞれ理由付き):

- **1 レコード = 1 要件** (複数まとめない) — 検索で一方だけ引きたいときに片方が埋もれるのを防ぐ。
  id で粒度よく引用できる。
- **短文 1〜2 文** — 全文 LIKE 検索なので、長文だとノイズが増えてヒット率が下がる。
- **文脈に依存しない自己完結した記述** — 「これ」「先ほどの」のような指示語を使わない。
  キーワード検索でいきなり 1 件だけ引いても意味が通るように。
- **機能名や対象ドメインを冒頭に含める** (例: 「Spotify 検索で〜」「ビルドプロセスで〜」) —
  ドメイン横断のキーワード検索で確実にヒットさせるため。
- **シングルクォート `'` を含む場合は `''` でエスケープ** — SQLite の文字列リテラル仕様。

### 更新・削除 (write - 必ずユーザーの許可を得てから)

原則として古いレコードを残し、新レコードを追加することで履歴を保つ
(id が連番なので時系列が分かる)。明示的に「古い要件を削除して」「N 番を直して」と
言われた時のみ DELETE / UPDATE する。

```sh
sqlite3 data/user_journey.db "DELETE FROM user_journey WHERE id = <N>"
sqlite3 data/user_journey.db "UPDATE user_journey SET text = '<new>' WHERE id = <N>"
```

### 乖離検知時の取り扱い (id 32 ルール)

ユーザーの新指示が既存レコードと矛盾するとき:

1. 関連既存レコードを検索で発見し、id と本文を引用して **矛盾点を明示する**
   （「id N と新ご要望が矛盾します」と冒頭で言い切る）。
2. AskUserQuestion で取り扱いを確認する。標準テンプレ（4 択）:
   ```json
   {
     "header": "user_journey 乖離検知",
     "question": "id <N> (<既存ルール要約>) と新ご要望 (<新要約>) が矛盾します。どう取り扱いますか？",
     "options": [
       { "label": "新ルールを INSERT (既存は残す)",   "description": "既定。履歴保持の原則どおり古いレコードを残し、新 id を発行。最新が現行ルール。" },
       { "label": "既存 id を UPDATE で上書き",       "description": "履歴を消して現行 1 本に集約。過去の判断根拠を遡らない場合に。" },
       { "label": "追加しない / 一旦保留",             "description": "今回は user_journey に反映せず別途検討。" },
       { "label": "文面を直したい",                   "description": "新要約案を編集してから判断（差し戻し）。" }
     ]
   }
   ```
3. **既定は履歴保持 INSERT**（SKILL.md の「更新・削除」原則と整合）。
   ユーザーが UPDATE を明示選択した場合のみ UPDATE する。
4. 関連するコード・docs にも波及する可能性があれば、その旨を併記する
   （DB 更新と実装変更はセットで対応が必要なケースが多い）。

「AskUserQuestion の選択肢 N 個」は場面に応じて 3〜4 個まで増やしてよい
（「追加」フローは 3 択標準、「乖離検知」は 4 択が標準）。

## 他文書からの引用

`docs/`, `DESIGN.md`, `README.md`, コミットメッセージ等から要件を参照するときは、
**`user_journey id N`** という表記で統一する (例: `user_journey id 13 ルール`)。
これにより:

- 文書間の整合性確認が grep 一発でできる (`rg 'user_journey id'`)
- 要件本文を引用先に転記しないので、要件が更新されても二重管理にならない
- レビュアが id を見て DB を引けば一次情報に到達できる

複数 id をまとめて参照する場合は `user_journey id 1, 7-9` のようにレンジ表記してよい。

## 推奨ワークフロー

タスク着手の最初:

1. 関連キーワード 2〜3 個で検索 (機能名 + ドメイン用語 + 制約タイプ を組み合わせる):
   ```sh
   sqlite3 data/user_journey.db "SELECT id, text FROM user_journey WHERE text LIKE '%Spotify%'"
   sqlite3 data/user_journey.db "SELECT id, text FROM user_journey WHERE text LIKE '%write%' OR text LIKE '%API%'"
   ```
2. ヒットしたら「検索結果の返し方」に沿って user に報告、要件を尊重して設計・実装に進む
3. 矛盾が生じたら、ユーザーに「どちらを優先するか」を確認
4. 新ルールが確定したら write 操作の許可フロー (上記) で INSERT

## 注意

- `data/user_journey.db` はバイナリ (SQLite)。git diff で内容が見えないので、
  追加・更新時はコミットメッセージに具体的な text を書くこと
- `data/` は `.assetsignore` で Cloudflare 配信から除外済み (公開されない)
- DB ファイル破損時は git 履歴から復元
- write 操作のルール (id 13) は本スキル自身にも適用される
