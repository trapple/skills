---
name: pbcopy
description: Copy content to clipboard when user says "copy", "コピー", or "コピーして"
---

# pbcopy - クリップボードコピー

ユーザーが指定した内容を `pbcopy` でクリップボードにコピーする。

## 前提

- **macOS 専用**。`pbcopy` は macOS 標準コマンド。Linux / Windows では動かない

## 実行手順

1. コピー対象を特定する（ファイル、会話中のコード・出力、テキストなど）
2. 以下のルールで `pbcopy` を実行する:
   - **ファイルの場合**: `cat <ファイルパス> | pbcopy`
   - **テキストの場合**: ヒアドキュメントで安全にコピーする
     ```bash
     cat <<'CLIP' | pbcopy
     コピー対象のテキスト
     CLIP
     ```
3. コピー完了後、何をコピーしたか簡潔に報告する
