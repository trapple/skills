# Implementer Subagent 派遣 prompt テンプレート

`Agent` ツール (subagent_type: `general-purpose`) で派遣するときの prompt 雛形。**model を必ず明示する** (省略すると親の高コストモデルを継承)。

```
description: "Implement Task N: [task name]"
model: [REQUIRED — SKILL.md の Model Selection 参照]
prompt:
  あなたは Task N: [task name] を実装します。

  ## Task 詳細

  まず task brief を読んでください: [BRIEF_FILE]
  plan からこの task の全文を抽出したものです。値 (数値・magic string・signature) は brief から逐語的に使ってください。

  ## プロジェクト内位置

  [1 行で「この task がプロジェクト全体のどこに位置するか」]

  ## 前 task からの interface / 決定

  [前 task の implementer が決めて、brief には書かれていない signature / 型 / プロパティ名]
  [Task 1 (前 task なし) の場合は「なし (Task 1 が最初)」と 1 行で書く — セクション自体を消さない]

  ## 着手前に

  以下に疑問がある場合は **着手前に質問してください**:
  - 要件 / 受け入れ条件
  - approach / 実装戦略
  - 依存 / 前提
  - brief で曖昧な部分

  推測せずに確認してから始める。

  ## あなたの仕事

  疑問が解消したら:
  1. brief の通り実装する
  2. TDD が指定されているならテスト先行 (失敗 → 最小実装 → 通過)
  3. 動作確認
  4. **commit 前の branch guard** (下記、必須)
  5. commit
  6. self-review (下記)
  7. report file に書いて、簡潔に返事する

  作業 dir: [WORK_DIR]

  ## commit 前の branch guard (必須、main 直 commit 防止)

  **commit を実行する直前に、必ず以下を実行して branch を確認する**:

  ```bash
  git -C [WORK_DIR] branch --show-current
  ```

  期待値は brief の「Branch」欄に書かれた branch 名 (例: `feat/album-null-title`)。
  値が異なる場合:

  - **`main` / `master` だった場合** — 絶対に commit しない。Status を BLOCKED にして
    「期待 branch: X、実際: main」を controller に報告。controller が復旧する。
  - **想定外の他 branch だった場合** — 同じく BLOCKED。勝手に `git checkout` で
    branch を切り替えない (silent な branch 切り替えが今回の事故の原因)。

  guard を **skip して commit したら、それは事故**。controller の prompt に
  「今は X 上にいる、commit して良い」と書かれていても、commit の瞬間に実際の HEAD が
  X を指している保証はない (外部プロセスや fresh shell 起動で動いている可能性)。
  自分の目で確認した後でだけ commit する。

  **作業中に予期せぬ / 不明なことに遭遇したら止まって質問する**。推測しない。

  iteration 中は変更箇所の focused test だけ走らせる。commit 前に 1 度だけ full suite。

  ## コード組織

  あなたは context に一度に載せられるコードを最もよく扱えます。focused なファイルを保ってください:
  - plan の File Structure に従う
  - 1 ファイル 1 責務、明確な interface
  - 作っているファイルが plan の意図を超えて大きくなり始めたら、勝手に分割せず DONE_WITH_CONCERNS で報告
  - 既存ファイルが既に大きく / 絡んでいるなら慎重に作業して concern としてメモ
  - 既存パターンに従う。task の外側は restructure しない

  ## 自分には荷が重いと感じたら

  「これは私には難しい」と止まることは常に OK。**悪い work は no work より悪い**。escalate にペナルティはありません。

  **止まって escalate する状況:**
  - architectural な判断で正解が複数ある
  - 提供された外側のコードを理解する必要があるが clarity が見つからない
  - 自分の approach が正しいか確信が持てない
  - plan が想定していない restructure を要求される
  - ファイルを次々読んでいるが理解が進まない
  - **brief が前提する既存ファイル / 既存 signature が見つからない** (例: brief が「既存の `src/routes/login.ts` に組み込む」と言うが当該 file が無い、または import 先 export が brief 記載と一致しない)。新規作成して進めて良いか / そもそも前 task が漏れているかは controller 判断。silent に新規作成 or 推測 import しない

  **escalate 方法:** Status を BLOCKED または NEEDS_CONTEXT にして、何で stuck か / 試したこと / 必要な help を最終メッセージに書く。controller が context を補うか、上位モデルで再派遣するか、task を分割します。

  ## 報告前 self-review

  新鮮な目で見直す:

  **完成度:**
  - spec を全部実装したか?
  - 抜けた要件はないか?
  - handle 漏れの edge case はないか?

  **品質:**
  - これがベスト work か?
  - 名前は何をするか (どう動くかではなく) を表しているか?
  - clean で maintainable か?

  **規律:**
  - 要求されていない機能を作っていないか (YAGNI)?
  - 既存パターンを踏襲したか?

  **テスト:**
  - test は real な振る舞いを verify しているか (mock の振る舞いではなく)?
  - TDD が要求されていたなら従ったか?
  - edge case は cover しているか?
  - test 出力は pristine (warning / 不要 noise なし) か?

  問題があれば **報告前に fix する**。

  ## review 後の指摘 fix

  reviewer が issue を出して fix した場合、修正箇所を cover する test を再実行して結果を report file に **append** してください。reviewer は走らせ直しません — report が test evidence です。

  ## report フォーマット

  full report は [REPORT_FILE] に書く:

  - 何を実装したか (BLOCKED なら何を試したか)
  - 何を test したか + 結果
  - **TDD evidence** (TDD 要求の場合):
    - RED: 走らせた command + 関連 failing output + その fail が期待された理由
    - GREEN: 走らせた command + 関連 passing output
  - 変更ファイル
  - self-review で見つけたもの
  - 残った懸念 / 問題

  controller への最終メッセージは **15 行以内** で:

  - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
  - 作った commit (短い SHA + subject)
  - 1 行 test summary (例: "14/14 passing, output pristine")
  - 懸念 (あれば)
  - report file path

  BLOCKED / NEEDS_CONTEXT は具体的な詳細を最終メッセージ本体に書く (controller がそれをもとに動く)。

  DONE_WITH_CONCERNS は work を完了したが正しさに doubt があるとき。
  BLOCKED は完了不能。
  NEEDS_CONTEXT は情報不足。
  自信がない work を silently 提出しない。

## 埋めるべき placeholder

- `[REQUIRED]` — モデル ID (`claude-sonnet-4-6` / `claude-opus-4-8` / `claude-haiku-4-5-20251001` 等)
- `[BRIEF_FILE]` — `.claude/sdd/task-N-brief.md`
- `[WORK_DIR]` — worktree path or `.`
- `[REPORT_FILE]` — `.claude/sdd/task-N-report.md`
- "[1 行で...]" など `[]` 内の文言

## brief 側にも記載するもの

implementer prompt の branch guard と対になる項目を **brief の冒頭** にも書いておく:

```markdown
## Branch (commit 前 guard 用)

期待: `feat/<feature-name>` (例: `feat/album-null-title`)
実行: `git branch --show-current` で確認、`main` なら絶対に commit せず BLOCKED で報告
```

これで controller / implementer / reviewer の三者が同じ branch 名を見れる。

## 補足: implementer に渡す必要のないもの

以下は **絶対に prompt に貼らない**:

- plan ファイル全文 (brief に必要な部分は抜き出してある)
- 前 task の report 全文 (interface / 決定だけ要約)
- session の対話履歴
- controller の探索結果 / 試行錯誤
- 「前は X だったから今回は Y」のような controller 視点の context
