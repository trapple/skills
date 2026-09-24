# Plan Reviewer 用 prompt テンプレート

実装プランを、新しい subagent に「ゼロ context の実装者」視点でレビューさせるときの prompt 雛形。`cross-review` スキルの plan ゲートとして使う。

**目的:** plan が spec と整合し、適切にタスク分解され、この plan だけで実装者が迷わず作れるか検証する。

**派遣タイミング:** plan のセルフレビュー後、実装に引き継ぐ前。autonomous では必須、guarded では 5 タスク以上 / 複数サブシステムにまたがるときに実施。

## 派遣方法

`Agent` ツール (`subagent_type: general-purpose`) で新しい subagent を派遣する (モデルの扱いは cross-review スキル 3.1)。以下の prompt を渡す。

```
あなたはこの PJ を今日初めて見る実装者です。手元にあるのはこの plan と spec とリポジトリだけで、作成者に質問はできません。plan を頼りに Task 1 から順に作るとして、どこで詰まるか、どこで作成者の意図と別物を作ってしまいそうかを洗い出してください。「たぶんこういう意味だろう」と補完したくなった箇所は、補完せずに指摘してください。

**対象 plan:** [PLAN_FILE_PATH]
**参照 spec:** [SPEC_FILE_PATH]
**依頼者の元の依頼文 (逐語):**
<<<
[USER_REQUEST_VERBATIM]
>>>
**PJ 規約:** [CLAUDE.md / .claude/rules/ の path。無ければ「なし」]

## チェック項目

| カテゴリ | 何を見るか |
|---------|------------|
| Buildability | plan だけで各 step を実行できるか。前提にしている既存ファイル / 関数 / コマンドは実在するか (実際に ls / grep で確認する) |
| 完成度 | TODO / placeholder / 未完タスク / step 欠落 / コードの無いコード step |
| spec 整合 | spec 要件を全部カバーしているか、scope creep が無いか |
| 型・名前の一貫性 | 前タスクで定義した signature と後タスクでの使い方が一致しているか |
| タスク分解 | 境界が明確か、step が actionable か |
| Gate 付与 | 本番データ / DB migration / データ削除 / 認証 / 課金 / 個人情報 / 秘密情報 / デプロイ / 外部送信 / 公開 API の破壊的変更に触れるタスクに `**Gate: human**` が付いているか |
| プロジェクト規約 | PJ CLAUDE.md / `.claude/rules/` の恒久ルール (Fail Fast、命名規約、コミット規約、外部 API 利用方針など) を侵害していないか |

## 判定基準

**実装段階で本当に問題になる issue だけ** flag する。実装者が「違うものを作りそう」「スタックしそう」なら issue。文言の好み・nice to have は Recommendations へ。

- `Approved` / `Issues Found` / `Needs Human`
- `Needs Human` は、spec と依頼文が食い違っていて plan 側では決められない場合、またはリスク領域の扱いが spec にも plan にも無い場合に限る

## 出力フォーマット

## Cross Review (ゼロ context の実装者)

**Status:** Approved | Issues Found | Needs Human

**Issues:**
- [Task X, Step Y]: [具体的問題] - [実装段階でなぜ問題になるか] - [修正案]

**Needs Human (Status が Needs Human のときのみ):**
- [論点]: [なぜ plan 側で決められないか] - [可逆 / 不可逆]

**Recommendations (承認をブロックしない):**
- [改善提案]
```

## 結果の扱い

`cross-review` スキルの「ループ」節に従う (最大 3 往復、反論 1 回、Needs Human の可逆 / 不可逆による分岐)。
