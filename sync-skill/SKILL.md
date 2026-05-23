---
name: sync-skill
description: Import or update a skill from another project into a subdirectory-package skills repository (the current one or an auto-detected sibling). Use when user says "sync-skill", "スキル同期", "スキルインポート", or "スキル取り込み"
argument-hint: "<source-path> [skill-name]"
---

# sync-skill - 他PJのスキルを skills リポジトリに取り込む / 更新する

別プロジェクトの skill ディレクトリを、ユーザーが管理する **subdirectory package パターンの skills リポジトリ**のルート直下にコピーし、必要なら README.md を自動更新する。

「subdirectory package パターン」とは、各スキルがリポジトリ直下のディレクトリ（`<repo-root>/<skill-name>/SKILL.md`）として配置され、`apm install -g <owner>/<repo>/<skill-name>` で個別にインストールできる構成を指す（例: `mizchi/skills`, `anthropics/skills`）。

## 想定リポジトリの解決

このスキルは特定のリポジトリ名に依存しない。**呼び出し元の `pwd` がスキル管理リポジトリ内とは限らない**ため、以下の順で `<repo-root>` を決定する。

1. **環境変数** — `$AGENT_SKILLS_REPO` が定義されていてディレクトリとして存在し、後述の「skills リポジトリ判定」に合致するなら採用する
2. **pwd** — 現在のディレクトリ（または `git -C . rev-parse --show-toplevel` のリポジトリルート）が skills リポジトリ判定に合致するなら採用する
3. **検索** — リポジトリ名が `skills` のディレクトリを探す:
   ```bash
   find ~/repos -maxdepth 5 -type d -name skills 2>/dev/null \
     | while read d; do [ -d "$d/.git" ] && echo "$d"; done
   ```
   結果が 1 件かつ skills リポジトリ判定に合致するなら採用。0 件 / 複数件は次へ
4. **明示** — 上記で決まらなければ AskUserQuestion でユーザーにフルパスを尋ねる

### skills リポジトリ判定

次のいずれか1つを満たせば「skills リポジトリ」とみなす:

- ルート直下に複数の `<name>/SKILL.md` ディレクトリが存在する（subdirectory package パターンの実体）
- `git -C <repo> remote get-url origin 2>/dev/null` の URL の末尾が `/skills(.git)?$` にマッチする

決定したパスは以降の手順すべての `<repo-root>` として使う。`cd` はせず `git -C <repo-root>` や絶対パスで操作すること。解決結果は必ずユーザー確認（手順3）で提示する。

### owner/repo の抽出（インストールコマンド表示用）

```bash
git -C <repo-root> remote get-url origin \
  | sed -E 's#(git@|https://)([^:/]+)[:/]([^/]+)/([^/.]+)(\.git)?#\3/\4#'
```

これで `<owner>/<repo>` が得られる。完了報告のインストールコマンドに使う。

## 引数

- `$1` (必須): 取り込み元のパス。次のいずれかを許容する:
  - skill ディレクトリ直指定: `~/.claude/skills/foo` / `<repo>/.claude/skills/foo` / `<repo>/.apm/skills/foo` / `<repo>/foo`（サブディレクトリパッケージ形式）
  - `SKILL.md` ファイル直指定: `<path>/SKILL.md`
- `$2` (任意): 取り込み後のスキル名。省略時は frontmatter の `name` または元ディレクトリ名を使う。

引数が空のときは会話の文脈から判断し、不足していればユーザーに聞く。

## 手順

### 1. 取り込み元の解決

1. `$1` を絶対パスに正規化する（`~` 展開を含む）
2. ファイルなら親ディレクトリを skill ディレクトリとみなす
3. skill ディレクトリ直下に `SKILL.md` が存在することを確認。無ければエラー終了
4. `SKILL.md` を Read で読み、frontmatter から `name` / `description` を抽出する

### 2. 宛先の決定と import / update 判定

- 宛先: `<repo-root>/<skill-name>/`
  - `<skill-name>` は `$2` > frontmatter `name` > 元ディレクトリ名 の優先順
  - 既存ビルトインや他スキルと衝突しないこと（`init`, `review`, `security-review` 等）
- `<宛先>` の存在で分岐:
  - **存在しない** → **import** モード
  - **存在する** → **update** モード（既存との `diff` を取りユーザーに提示してから上書き）

### 3. ユーザー確認

import / update どちらでも、実行前に以下を提示して承認を取る:

- 解決された `<repo-root>` のフルパスと、解決手段（環境変数 / pwd / 検索 / 明示）
- モード（import or update）
- コピー元・コピー先のフルパス
- 取り込まれるファイル一覧（`SKILL.md` 以外に同梱資材があれば全部）
- update の場合は `diff -u <宛先>/SKILL.md <元>/SKILL.md` の結果

### 4. コピー実行

```bash
# import (新規)
cp -R <元ディレクトリ> <repo-root>/<skill-name>

# update (既存)
# 宛先側の余剰ファイルは消さない方が安全。差分のあるファイルだけ上書きする
cp -R <元ディレクトリ>/. <repo-root>/<skill-name>/
```

**注意**: `cp -R src/. dst/` の形（末尾 `/.`）にしないと、`dst/<元ディレクトリ名>/` のような入れ子になる。

### 5. README.md の自動更新

`<repo-root>/README.md` を Read して、スキル一覧テーブルの位置を**見出しから検出**する:

- 英語表: `## Included skills` 直後のテーブル
- 日本語表: `### 収録スキル` 直後のテーブル

両方が見つからない場合は README に該当セクションが無い構造とみなし、ユーザーに「テーブルを追加するか」確認する。片方しか無ければ片方だけ更新する。

各行のフォーマット:

```
| `<skill-name>` | <triggers> | <description-summary> |
```

- `<triggers>`: frontmatter `description` から以下のパターン優先順で抽出:
  1. `Use when user says "X", "Y", or "Z"` → バッククォート付きでカンマ区切り（英語表）／スラッシュ区切り（日本語表）
  2. `Use proactively when ...` → `proactive (<理由を1フレーズ>)` / `文脈トリガー（<理由>）`
  3. `TRIGGER when: ...` → `auto (<コード/状況条件>)` / `自動（<条件>）`
  4. `disable-model-invocation: true` → `手動のみ` / `manual only`
  5. `user-invocable: false` → `Claude 自動のみ` / `Claude-auto only`
  6. それ以外（トリガー文無し） → ユーザーに 1 フレーズで要約してもらう
- `<description-summary>`: SKILL.md 本文 H1 直下の最初の段落を 1〜2 文に要約。frontmatter `description` の前半をそのまま使わない（トリガー文混入や情報量不足を避けるため）。プラットフォーム制約（macOS 専用 等）や外部依存（要 X コマンド 等）があれば**`**bold**` 付きで末尾**に明記
- import の場合: 表の末尾に行を追加（Edit で「最後の `|` 終端行」を見つけて差し込む）
- update の場合: 既存行を Edit で置換

### 6. 完了報告

ユーザーに以下を伝える:

- 取り込んだ skill 名と宛先パス
- README に追加 / 更新した行（英日両方）
- 次のアクション候補: `git -C <repo-root> diff` で確認 → `/commit` でコミット
- インストールコマンド: `apm install -g <owner>/<repo>/<skill-name>`（`<owner>/<repo>` は上記の抽出結果）
- **`sync-skill` 自身を更新した場合の追加注意**: 稼働中の SKILL.md は再読み込みされないので、変更は次セッションから反映される

## やらないこと

- subdirectory package パターンのリポジトリではルートに `apm.yml` を置かない運用が一般的なので、元 skill 側に `apm.yml` があっても**コピーしない**（SKILL.md とアセットのみ取り込む）。宛先 repo に元から `apm.yml` がある場合はそれを尊重し、`name`/`version` は触らない
- `apm.lock.yaml` は APM が管理するファイルなので触らない
- `cd` で作業ディレクトリを変更しない。全ての操作は `git -C <repo-root>` や絶対パスで行う
- 元 skill が macOS 依存などのプラットフォーム制約を持っていても**そのままコピー**する。README にはその制約も含めて記述する

## 関連スキル

- `create-skill`: ゼロから新規 skill を作る場合はこちら
- `commit`: 取り込み後のコミット作成
