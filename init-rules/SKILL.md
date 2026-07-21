---
name: init-rules
description: "ルールテンプレートをプロジェクトに導入する。Use when user says \"init-rules\", \"ルール導入\", or \"ルールテンプレート\""
---

# init-rules - ルールテンプレートの導入

このスキルにバンドルされたテンプレートを、現在のプロジェクトの `.claude/rules/` にコピーして導入する。
コピー後はプロジェクトごとに自由に編集可能。

## 実行方針（速い方を選ぶ）

- **mac / Linux（`sh` が使える環境）** → 「高速手順（sh）」を使う。
  探索・一覧生成・コピーをそれぞれ 1 コマンドで済ませ、ファイルを個別に Read しない。
- **Windows（PowerShell のみ）** → 「フォールバック手順（Windows）」を使う。

## 高速手順（sh / mac・Linux）

### 1. テンプレート探索＋一覧表示（1 コマンド）

次のスクリプトをそのまま実行する。テンプレートディレクトリの決定・`description` 抽出・
既存 `.claude/rules/` との重複判定（NEW / 済）・番号付き一覧の表示を一括で行う。

```sh
sh -c '
TPLDIR=""
for d in \
    "$HOME/.claude/skills/init-rules/rules-templates" \
    "./.claude/skills/init-rules/rules-templates" \
    "$HOME/.claude/rules-templates"; do
  [ -d "$d" ] && { TPLDIR="$d"; break; }
done
[ -z "$TPLDIR" ] && TPLDIR=$(find "$HOME/.apm/packages" -type d -path "*/init-rules/rules-templates" 2>/dev/null | head -1)
[ -z "$TPLDIR" ] && { echo "テンプレートが見つかりません"; exit 1; }

echo "出典: $TPLDIR"
echo
i=0
for f in "$TPLDIR"/*.md; do
  i=$((i+1))
  name=$(basename "$f")
  desc=$(sed -n "s/^description:[[:space:]]*//p" "$f" | head -1 | sed "s/^\"//;s/\"$//")
  if [ -f ".claude/rules/$name" ]; then badge="[済] "; else badge="[NEW]"; fi
  printf "%2d. %s %-26s %s\n" "$i" "$badge" "$name" "$desc"
done
'
```

出力の `出典:` 行を導入元として、番号付き一覧をユーザーにそのまま提示する。
`テンプレートが見つかりません` が出たらその旨を通知して終了。

### 2. 選択されたテンプレートをコピー（1 コマンド）

ユーザーが選んだ番号を一覧のファイル名に対応づけてコピーする。`TPLDIR` は手順 1 と同じ
探索結果を使う（下記スクリプトは同じ探索を内蔵しているのでそのまま渡せる）。

個別選択（例: `docs-management.md error-handling.md`）:

```sh
sh -c '
TPLDIR=""
for d in \
    "$HOME/.claude/skills/init-rules/rules-templates" \
    "./.claude/skills/init-rules/rules-templates" \
    "$HOME/.claude/rules-templates"; do
  [ -d "$d" ] && { TPLDIR="$d"; break; }
done
[ -z "$TPLDIR" ] && TPLDIR=$(find "$HOME/.apm/packages" -type d -path "*/init-rules/rules-templates" 2>/dev/null | head -1)
mkdir -p .claude/rules
for name in "$@"; do
  cp "$TPLDIR/$name" ".claude/rules/$name" && echo "導入: $name"
done
' _ docs-management.md error-handling.md
```

全部導入する場合は末尾の引数を `*.md` 相当に置き換える:

```sh
sh -c '
TPLDIR=""
for d in \
    "$HOME/.claude/skills/init-rules/rules-templates" \
    "./.claude/skills/init-rules/rules-templates" \
    "$HOME/.claude/rules-templates"; do
  [ -d "$d" ] && { TPLDIR="$d"; break; }
done
[ -z "$TPLDIR" ] && TPLDIR=$(find "$HOME/.apm/packages" -type d -path "*/init-rules/rules-templates" 2>/dev/null | head -1)
mkdir -p .claude/rules
cp "$TPLDIR"/*.md .claude/rules/ && echo "全テンプレートを導入しました"
'
```

### 3. 後処理

既存ドキュメント（`docs/` 配下など）にルール適用が必要な場合は提案する。

## フォールバック手順（Windows）

`sh` が使えない環境では、以下を手動で行う。

1. 次を順に探し、最初に見つかったディレクトリをテンプレート出典とする:
   - `~/.claude/skills/init-rules/rules-templates/`（global install）
   - `./.claude/skills/init-rules/rules-templates/`（project install）
   - `~/.apm/packages/**/init-rules/rules-templates/`（APM パッケージ展開先）
   - `~/.claude/rules-templates/`（レガシー / 手動配置）
   - 見つからなければ「テンプレートが見つかりません」と通知して終了。
2. ディレクトリ内のテンプレート一覧（`*.md`）を取得する。
3. 各テンプレートの `description`（frontmatter）を読み取り、一覧を表示する。
4. 既にプロジェクトの `.claude/rules/` に同名ファイルがある場合は「導入済み」と表示する。
5. ユーザーに導入したいテンプレートを選んでもらう（「全部」もOK）。
6. 選択されたテンプレートを `.claude/rules/` にコピーする。
7. 既存ドキュメント（`docs/` 配下など）にルール適用が必要な場合は提案する。

## 表示フォーマット例

```
利用可能なルールテンプレート（出典: ~/.claude/skills/init-rules/rules-templates/）:

 1. [NEW] docs-management.md - ドキュメント管理ルール（frontmatter・ステータス運用）
 2. [済]  error-handling.md  - エラーハンドリングルール
 3. [NEW] plan-output.md     - planモード出力先ルール

導入するテンプレートを選んでください（番号、カンマ区切り、または「全部」）
```
