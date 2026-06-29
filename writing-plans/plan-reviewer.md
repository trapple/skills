# Plan Reviewer 用 prompt テンプレート

実装プランを subagent に独立レビューしてもらうときの prompt 雛形。

**目的:** plan が完成形で、spec と整合し、適切にタスク分解されているか検証する。

**派遣タイミング:** plan を書き終え、ユーザーに 2 実行モードを提示する直前 (任意)。

## 派遣方法

`Agent` ツール (subagent_type: `general-purpose` または `Plan`) で、以下の prompt を渡す。

```
あなたは plan document reviewer です。この plan が完成して実装に進められるかを検証してください。

**対象 plan:** [PLAN_FILE_PATH]
**参照 spec:** [SPEC_FILE_PATH]

## チェック項目

| カテゴリ | 何を見るか |
|---------|------------|
| 完成度 | TODO / placeholder / 未完タスク / step 欠落 |
| spec 整合 | plan が spec 要件を全部カバーしているか、scope creep が無いか |
| タスク分解 | タスクの境界が明確、step が actionable |
| Buildability | 実装者がこの plan を読んでスタックせずに進められるか |
| プロジェクト規約 | PJ CLAUDE.md / `.claude/rules/` 配下に定義された恒久ルール (Fail Fast、命名規約、コミット規約、外部 API 利用方針、ドメイン固有の罠など) を侵害していないか |

## 判定基準

**実装段階で本当に問題になる issue だけ** flag する。

- 実装者が「違うものを作りそう」 / 「スタックしそう」 → issue
- 文言の好み、スタイル、「nice to have」 → issue にしない

spec 要件の漏れ、step の矛盾、placeholder、行動不能なほど曖昧なタスク以外は Approved にする。

## 出力フォーマット

## Plan Review

**Status:** Approved | Issues Found

**Issues (if any):**
- [Task X, Step Y]: [具体的問題] - [なぜ実装段階で問題になるか]

**Recommendations (advisory, do not block approval):**
- [改善提案]
```

## レビューア返却物

- Status (Approved / Issues Found)
- Issues (あれば task / step + 問題 + 影響理由)
- Recommendations (任意、承認をブロックしない)

## 使うべきとき / 省くべきとき

**使う:**
- plan が 5 タスク以上の長期計画
- 複数のサブシステムを跨ぐ依存関係がある
- TDD 強制が plan のいたるところで必要

**省く:**
- plan が 1〜3 タスクで自分の目で全部追える
- 既存パターンの繰り返し
- 試作 / 検証目的の短期 plan
