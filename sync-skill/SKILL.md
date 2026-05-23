---
name: sync-skill
description: Import or update a skill from another project into this repository's root as a subdirectory package. Use when user says "sync-skill", "スキル同期", "スキルインポート", or "スキル取り込み"
argument-hint: "<source-path> [skill-name]"
---

# sync-skill - 他PJのスキルを本リポジトリに取り込む / 更新する

別プロジェクトの skill ディレクトリを、この `trapple/skills` リポジトリの**ルート直下**にコピーし、必要なら README.md を自動更新する。

このリポジトリは APM の **subdirectory package** パターンを採用しており、各スキルはリポジトリ直下のディレクトリ（`<repo-root>/<skill-name>/SKILL.md`）として配置される。これにより `apm install -g trapple/skills/<skill-name>` で個別インストールできる。

**前提**: このスキルは `trapple/skills` リポジトリのルート（`README.md` と `LICENSE` がある場所、`git remote -v` の URL に `trapple/skills` を含む場所）で実行されることを想定している。`pwd` が想定外なら処理を止めてユーザーに確認すること。

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

`<repo-root>/README.md` には**英語表**と**日本語表**の2つのスキル一覧テーブルがある。両方に行を追加 / 更新する。

各行のフォーマット:

```
| `<skill-name>` | <triggers> | <description-summary> |
```

- `<triggers>`: frontmatter `description` の `Use when user says "X", "Y", or "Z"` 部分から抽出してバッククォート付きで列挙する（例: `` `sync-skill` / `スキル同期` ``）
- `<description-summary>`: 英語表には英語 description の前半（トリガー文を除いた部分）、日本語表には日本語要約を入れる。日本語要約が SKILL.md 本文に書かれていればそれを使い、無ければユーザーに 1〜2 行で書いてもらう
- import の場合: 表の末尾に行を追加
- update の場合: 既存行を Edit で置換

`disable-model-invocation: true` や `user-invocable: false` の skill は、トリガー欄をそれぞれ「手動のみ」「Claude自動のみ」と表記する。

### 6. 完了報告

ユーザーに以下を伝える:

- 取り込んだ skill 名と宛先パス
- README に追加 / 更新した行
- 次のアクション候補: `git diff` で確認 → `/commit` でコミット
- インストールコマンド: `apm install -g trapple/skills/<skill-name>`

## やらないこと

- このリポジトリは subdirectory package パターンのため、ルートに `apm.yml` を置かない。元 skill 側に `apm.yml` があっても**コピーしない**（SKILL.md とアセットのみ取り込む）
- `apm.lock.yaml` は APM が管理するファイルなので触らない
- 元 skill が macOS 依存などのプラットフォーム制約を持っていても**そのままコピー**する。README にはその制約も含めて記述する（既存の `pbcopy` / `init-rules` の書き方を踏襲）

## 関連スキル

- `create-skill`: ゼロから新規 skill を作る場合はこちら
- `commit`: 取り込み後のコミット作成
