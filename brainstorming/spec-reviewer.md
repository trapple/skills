# Spec Reviewer 用 prompt テンプレート

design doc (spec) を subagent に独立レビューしてもらうときの prompt 雛形。

**目的:** spec が完成形で、矛盾なく、実装プラン作成に進める状態か検証する。

**派遣タイミング:** spec を `.claude/specs/YYYY-MM-DD-<topic>-design.md` (または PJ 固有の spec 配置先) に書いたあと、ユーザーレビュー前 (任意ステップ — セルフレビューで足りるなら省略可)。

## 派遣方法

`Agent` ツール (subagent_type: `general-purpose` または `Plan`) で、以下の prompt を渡す。

```
あなたは spec document reviewer です。この spec が完成して plan 作成に進められるかを検証してください。

**対象 spec:** [SPEC_FILE_PATH]

## チェック項目

| カテゴリ | 何を見るか |
|---------|------------|
| 完成度 | TODO / placeholder / "TBD" / 未完セクション |
| 整合性 | セクション間の矛盾、要件同士の衝突 |
| 明確さ | 「2 通り解釈可能で、結果として違うものが作られそう」な要件 |
| スコープ | 1 つの plan に収まるか? 独立サブシステムが混在していないか |
| YAGNI | 求められていない機能 / over-engineering |
| プロジェクト整合 | PJ 規約 (CLAUDE.md / .claude/rules/ 配下に定義された原則。例: Fail Fast, main 直コミット禁止 等) との衝突がないか |

## 判定基準

**実装プラン作成段階で本当に問題になる issue だけ** flag する。

- セクション抜け、内部矛盾、2 通り解釈可能な要件 → issue
- 文言の好み、スタイル、「ここはもう少し詳しくても」程度の意見 → issue にしない

重大なギャップで plan が破綻しそうな場合のみ「Issues Found」。それ以外は「Approved」。

## 出力フォーマット

## Spec Review

**Status:** Approved | Issues Found

**Issues (if any):**
- [section X]: [具体的な問題] - [なぜそれが plan 作成で問題になるか]

**Recommendations (advisory, do not block approval):**
- [改善提案]
```

## レビューア返却物

- Status (Approved / Issues Found)
- Issues (あれば section + 問題 + 影響理由)
- Recommendations (任意の改善提案、承認をブロックしない)

## 使うべきとき / 省くべきとき

**使う:**
- spec が長め (200 行超) で見落としが心配
- ユーザーが品質クリティカルな案件と明言している
- 過去のセルフレビューで漏れが多かった領域

**省く:**
- spec が 100 行未満で目視で全て確認できる
- 既存パターンの繰り返しでスコープが明確
- ユーザーがスピード重視の試作と明言している

Brainstorming スキルのチェックリストでは spec セルフレビューが必須、subagent レビューは任意。
