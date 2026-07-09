---
name: compress
description: Compress the current conversation into a CCS (Compressed Cognitive State) file so work can resume in a new session after /clear. Use when user says "compress", "圧縮", "CCS", or "/compress".
---

# 会話コンテキスト圧縮 (ACC - Agent Cognitive Compressor)

会話履歴を圧縮し、新しいセッションで継続できるようにする。

## 概要

このスキルは論文「AI Agents Need Memory Control Over More Context」のACC（Agent Cognitive Compressor）概念に基づき、会話をCCS（Compressed Cognitive State）形式で圧縮する。

## 実行手順

### 1. 現在の会話を分析し、以下のCCS形式で圧縮する

```markdown
# Compressed Cognitive State (CCS)

## goal_orientation（現在の目標）
- 現在取り組んでいるタスクの最終目標
- 達成すべきマイルストーン

## constraints（制約条件）
- 守るべきルール・制約
- 技術的制約
- ユーザーの好み・要望

## uncertainty_signal（不確実な情報）
- 未解決の疑問点
- 確認が必要な事項
- 仮定している前提

## episodic_trace（直近の作業履歴）
- 最近実行した重要なアクション（3-5件）
- 変更したファイル
- 実行したコマンド

## semantic_gist（対話の要点）
- 会話全体の要約（3-5文）
- 重要な決定事項

## focal_entities（重要なエンティティ）
- 関連するファイルパス
- 重要な変数・関数名
- キーとなる技術・ツール

## relational_map（因果関係）
- 問題と原因の関係
- 依存関係
- 影響範囲

## predictive_cue（次のステップ）
- 次に実行すべきアクション
- 残タスク
- 推奨される次の作業
```

### 2. 圧縮結果をファイルに保存

保存先: `.claude/memory/ccs_<timestamp>.md`（**リポジトリ共通**。git worktree内で実行してもメイン作業ツリー基準の同じ場所に保存する）

```bash
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  MEMORY_DIR="$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")/.claude/memory"
else
  MEMORY_DIR=".claude/memory"
fi
mkdir -p "$MEMORY_DIR"
```

**ポイント:** カレントディレクトリ相対で `.claude/memory` に保存すると、worktree内（`using-git-worktrees` スキルが作る `.claude/worktrees/<branch>/` 等）で実行した場合にworktree専用の場所に保存されてしまう。`.claude/worktrees/` は通常 `.gitignore` 対象でworktree削除時に中身ごと消えるため、保存したCCSが失われる。`git-common-dir` 基準の解決により、メインリポジトリでもworktreeでも常に同じ `.claude/memory/` に保存・参照できるようにする。

### 3. ユーザーへの案内

圧縮完了後、以下を案内する:

1. **保存されたファイルパス**を表示
2. **会話クリア方法**: `/clear` コマンドまたは新しいセッション開始
3. **記憶ロード方法**: 新セッションで `/decompress` を実行

## 圧縮のポイント

- **goal_orientation, constraints, uncertainty_signal** が特に重要
- 履歴を「保存して再生」するのではなく「今の状態を再生成」する
- 不要な詳細は省略し、本質的な情報のみを残す
- コードの具体的な内容より「何をしたか」「なぜしたか」を重視

## 使用例

ユーザー: `/compress`

Claude:
```
現在の会話を分析してCCS形式で圧縮します...

# Compressed Cognitive State (CCS)

## goal_orientation
- React アプリにダークモード機能を追加する
- 設定画面にトグルスイッチを配置

## constraints
- 既存のTailwind CSSを使用
- localStorage で設定を永続化
- アクセシビリティ対応必須

## uncertainty_signal
- システム設定との連動は未確認
- 既存コンポーネントへの影響範囲

## episodic_trace
- ThemeContext.tsx を作成
- useTheme フックを実装
- Settings.tsx にトグル追加

## semantic_gist
ダークモード機能の実装を進行中。Context APIでテーマ状態を管理し、
Tailwindのdarkクラスで切り替える方式を採用。基本実装完了、テスト未実施。

## focal_entities
- src/contexts/ThemeContext.tsx
- src/hooks/useTheme.ts
- src/pages/Settings.tsx
- tailwind.config.js

## relational_map
- ThemeContext → useTheme → 各コンポーネント
- localStorage ← ThemeContext（永続化）

## predictive_cue
- [ ] 既存コンポーネントにdarkクラス追加
- [ ] 単体テスト作成
- [ ] E2Eテスト作成

---
保存先: .claude/memory/ccs_20250206_1430.md

次のステップ:
1. /clear で会話をクリア
2. 新セッションで /decompress を実行して継続
```
