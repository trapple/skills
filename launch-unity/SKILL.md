---
name: launch-unity
description: Detect which Unity project to launch and start Unity Editor via uloop. Use when user says "unity起動", "Unity起動して", "Unity開いて", "launch unity", or asks to start the Unity Editor.
argument-hint: "[project-path]"
allowed-tools: "Bash, AskUserQuestion, Read"
---

# Unity 起動

対象の Unity プロジェクトを特定し、`uloop launch` で Unity Editor を起動する。

## 検出された Unity プロジェクト候補

!`{ [ -f ProjectSettings/ProjectVersion.txt ] && echo "(current directory is a Unity project)"; find . -maxdepth 4 -name ProjectVersion.txt -path "*ProjectSettings*" -not -path "*/Library/*" 2>/dev/null | sed 's|/ProjectSettings/ProjectVersion.txt||'; } || true`

## 起動対象の決定ルール（上から順に適用）

1. **引数指定あり** (`$ARGUMENTS` にパス): そのパスを起動対象とする
2. **カレントが Unity プロジェクト**（上の候補に `(current directory is a Unity project)` がある）: カレントディレクトリを起動
3. **候補が 1 つだけ**: それを起動
4. **候補が複数**: 会話のコンテキストから判断する
   - 直近で編集・調査していたファイルがどのプロジェクト配下か
   - 会話で話題になっているアプリ名・機能がどのプロジェクトのものか
   - 判断根拠をユーザーに一言伝えてから起動する
5. **コンテキストから判断できない**: AskUserQuestion で候補を選択肢として提示し、ユーザーに選んでもらう。勝手に決めない

## 起動コマンド

```bash
uloop launch <project-path>
```

- カレントを起動する場合はパス省略で `uloop launch`
- `uloop launch` は fire-and-forget ではなく、Unity が CLI 操作可能になるまで待ってから終了する
- Unity の初回起動・インポートには数分かかることがあるため、Bash の timeout は 600000ms（最大）を指定すること
- すでに Unity が起動している場合は既存ウィンドウがフォーカスされる。再起動が必要なときのみ `-r` を付ける

## 起動後

- 出力される Unity バージョンとプロジェクトパスをユーザーに報告する
- エラーで終了した場合は出力をそのまま報告し、勝手にリトライしない
