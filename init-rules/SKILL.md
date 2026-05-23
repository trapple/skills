---
name: init-rules
description: "ルールテンプレートをプロジェクトに導入する。Use when user says \"init-rules\", \"ルール導入\", or \"ルールテンプレート\""
---

# init-rules - ルールテンプレートの導入

このスキルにバンドルされたテンプレートを、現在のプロジェクトの `.claude/rules/` にコピーして導入する。
コピー後はプロジェクトごとに自由に編集可能。

## テンプレートの探索

以下を順に探し、最初に見つかったディレクトリを使う:

1. **このスキルに同梱されたテンプレート**（APM 配布版）
   - `~/.claude/skills/init-rules/rules-templates/`（global install）
   - `./.claude/skills/init-rules/rules-templates/`（project install）
   - `~/.apm/packages/**/init-rules/rules-templates/`（APM パッケージ展開先）
2. **レガシー / 手動配置**
   - `~/.claude/rules-templates/`

シェルでの探索例:

```bash
for d in \
    ~/.claude/skills/init-rules/rules-templates \
    ./.claude/skills/init-rules/rules-templates \
    ~/.claude/rules-templates; do
  [ -d "$d" ] && { echo "$d"; break; }
done
```

見つからない場合はユーザーに「テンプレートが見つかりません」と通知して終了。

## 手順

1. 上記の探索でテンプレートディレクトリを決定する
2. ディレクトリ内のテンプレート一覧（`*.md`）を取得する
3. 各テンプレートの `description`（frontmatter）を読み取り、一覧を表示する
4. 既にプロジェクトの `.claude/rules/` に同名ファイルがある場合は「導入済み」と表示する
5. ユーザーに導入したいテンプレートを選んでもらう（「全部」もOK）
6. 選択されたテンプレートを `.claude/rules/` にコピーする
7. 既存ドキュメント（`docs/` 配下など）にルール適用が必要な場合は提案する

## 表示フォーマット例

```
利用可能なルールテンプレート（出典: ~/.claude/skills/init-rules/rules-templates/）:

1. [NEW] docs-management.md - ドキュメント管理ルール（frontmatter・ステータス運用）
2. [済]  error-handling.md  - エラーハンドリングルール
3. [NEW] plan-output.md     - planモード出力先ルール

導入するテンプレートを選んでください（番号、カンマ区切り、または「全部」）
```
