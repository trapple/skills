---
name: decompress
description: Restore a previously saved CCS (Compressed Cognitive State) file to resume work in a new session. Use when user says "decompress", "復元", "CCS復元", or "/decompress".
---

# CCS復元 (Decompress)

圧縮されたCCS（Compressed Cognitive State）を読み込み、作業コンテキストを復元する。

## 実行手順

### 1. CCSファイルの検索

CCSはリポジトリ共通の場所（メイン作業ツリー基準）に保存されている。git worktree内で実行した場合でもメインリポジトリ側の `.claude/memory/` を参照できるよう、`git-common-dir` から保存先を解決してから検索する。

```bash
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  MEMORY_DIR="$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")/.claude/memory"
else
  MEMORY_DIR=".claude/memory"
fi
ls -lt "$MEMORY_DIR"/ccs_*.md
```

**ポイント:** worktree内（`.claude/worktrees/<branch>/` 等）で実行しても、`git-common-dir` は常にメインリポジトリの `.git` を指すため、`.claude/memory/` はworktreeをまたいで同じ場所を参照する。カレントディレクトリ相対の `.claude/memory/` をそのまま使わないこと（worktree内では別ディレクトリを見てしまい、保存済みCCSが見つからない/保存したCCSがworktree削除で消える原因になる）。

### 2. ファイル選択

- ファイルが1つだけの場合: そのファイルを自動選択
- ファイルが複数ある場合: 日時の新しい順に一覧を表示し、ユーザーに選択してもらう
- ファイルが存在しない場合: `.claude/memory/` にCCSファイルが見つからない旨を伝えて終了

### 3. CCSの読み込みとコンテキスト復元

選択されたCCSファイルを読み込み、以下の順序でコンテキストを復元する:

1. **goal_orientation** を確認し、現在のタスク目標を把握する
2. **constraints** を確認し、守るべき制約を認識する
3. **uncertainty_signal** を確認し、未解決の課題を認識する
4. **episodic_trace** で直近の作業内容を把握する
5. **focal_entities** のファイルパスが現在も存在するか確認する
6. **predictive_cue** から次のアクションを特定する

### 4. 復元結果の報告

以下の形式でユーザーに報告する:

```
CCSを復元しました: <ファイル名>

## 復元されたコンテキスト
- 目標: <goal_orientationの要約>
- 直近の作業: <episodic_traceの要約>
- 次のステップ: <predictive_cueの内容>

## 注意事項
- <uncertainty_signalがあれば記載>
- <focal_entitiesのうち存在しないファイルがあれば警告>

何から始めますか？
```

## ポイント

- CCSは「状態の再生成」であり、会話履歴の再生ではない
- focal_entities のファイルが変更・削除されている可能性があるため、存在確認を行う
- 復元後はすぐに作業を開始できる状態にする
