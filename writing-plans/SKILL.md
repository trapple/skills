---
name: writing-plans
description: "Use when you have a spec or requirements for a multi-step task, before touching code. Use when user says \"プラン書いて\", \"実装計画\", \"writing plans\", \"plan を作って\", or after brainstorming approves a spec."
---

# writing-plans — 実装プランを書く

spec / 要件を入力に、ゼロ context のエンジニアでも実行可能な実装プランを書く。bite-size タスクに分解し、各タスクは「テスト書く → 失敗確認 → 最小実装 → 通過確認 → commit」の単位まで落とす。DRY / YAGNI / TDD / 頻繁な commit が原則。

エンジニアは熟練者だが「このプロジェクト固有のツール / ドメイン」は知らない前提。テスト設計も得意でないと仮定して書く。

**着手の合図:** `writing-plans スキルで実装プランを書きます。` と 1 行宣言してから始める。

**context:** worktree 上で書くなら `using-git-worktrees` スキルで先に隔離環境を作っておくこと。

**保存先:** `.claude/plans/YYYY-MM-DD-<feature-name>.md` (PJ 側に独自の plan 配置規約 — 例: `docs/plans/` — があればそれに従う)

## スコープチェック

spec が複数の独立サブシステムを含んでいる場合、brainstorming 段階で分解しておくべきだった。もし分解せずにここまで来てしまったら **plan を 1 つでも書く前にユーザーに decompose を提案** する。各 plan は単独で動くソフトウェアを生むサイズに収める。

## ファイル構造を先に決める

タスクに分解する前に「どのファイルを作る / 触る」と「各ファイルの責務」をマップする。decomposition の判断はここで lock する。

- 各単位は明確な境界 + well-defined interface。1 ファイル 1 責務
- Claude は文脈に丸ごと載せられるコードに対して最も良く reason できる。小さく focused なファイルを優先する
- 一緒に変わるものは一緒に置く。技術レイヤではなく責務で割る
- 既存コードの慣習に従う。大きいファイルだらけの codebase をいきなり再構成しない。ただし触るファイルが既に大きすぎるなら、その plan の中で分割を含めるのは妥当

このファイル構造がタスク分解の根拠になる。各タスクは独立して意味を持つ自己完結変更を生むべき。

## タスク粒度

タスクは「独立したテストサイクルを持ち、新鮮なレビュアーのゲートを通すに値する最小単位」。

- セットアップ / 設定 / scaffolding / ドキュメントは、それを必要とする deliverable のタスクに畳む
- 隣り合うタスクが片方だけ reject されうるなら分ける、そうでなければ統合
- 各タスクは「独立してテスト可能な deliverable」で終わる

### bite-size step (各 step は 2〜5 分の 1 アクション)

- 「失敗するテストを書く」 — step
- 「実行して失敗確認」 — step
- 「最小実装」 — step
- 「テスト通過確認」 — step
- 「commit」 — step

## plan ドキュメント header

全 plan は以下で始める:

```markdown
# [機能名] 実装プラン

> **実装者向け:** このプランは subagent-driven-development (推奨) または手動実行で消化する。step は `- [ ]` チェックボックスで track する。

**Goal:** [1 文で「何を作るか」]

**Architecture:** [2〜3 文で approach]

**Tech Stack:** [使う主な技術 / ライブラリ]

## Global Constraints

以下の 3 種を **サブセクションに分離して** 列挙する。混ぜない。各タスクの要件にはこのセクションが暗黙に含まれる。**該当情報がないサブセクションは見出しを残し、本文に `該当なし` と 1 行書く** (見出しごと削除しない — テンプレート構造を読者が確認できるようにするため)。

### Spec 由来 (spec から逐語コピー)

[バージョン下限、依存制約、コピー文言、プラットフォーム要件など。値は spec から **逐語的に** コピー。]

### PJ 恒久ルール (CLAUDE.md / `.claude/rules/` 由来)

[Fail Fast、命名規約、コミット規約、外部 API 利用方針など、この plan に関係するもの。PJ 恒久ルールと plan の設計責務が直接衝突する場合 (例: Fail Fast の再 throw vs API レイヤでのエラー応答変換) は、衝突する 1 行の直後に `※ 局所例外: <理由>` と 1 行で明示し、対応するコード step にもコメントとして理由を残す。]

### 運用前提 (brainstorming で確定した実装方式)

[隔離方式 (worktree / branch)、ブランチ名、SDD / 直列、その他 brainstorming で固定された前提。実装フェーズへの引き継ぎ情報。]

---
```

## タスク構造

````markdown
### Task N: [コンポーネント名]

**Files:** *(以下は Create / Modify / Test の 3 種別すべてが発生するケースの例。実際のタスクでは該当する種別行だけ書き、不要種別は **省略する** — 空行や `N/A` を残さない)*
- Create: `exact/path/to/file.mjs`
- Modify: `exact/path/to/existing.mjs:123-145`
- Test: `tests/exact/path/to/file.test.mjs`

**Interfaces:**
- Consumes: [このタスクが前タスクから使うもの — 正確な signature]
- Produces: [後続タスクが依存するもの — 正確な関数名、引数 / 返り値型]

- [ ] **Step 1: 失敗するテストを書く**

```javascript
import { test } from 'node:test';
import assert from 'node:assert/strict';

test('specific behavior', async () => {
  const result = await fn(input);
  assert.equal(result, expected);
});
```

- [ ] **Step 2: 実行して失敗を確認**

実行: `node --test tests/path/to/file.test.mjs`
期待: FAIL ("fn is not defined" など)

- [ ] **Step 3: 最小実装**

```javascript
export function fn(input) {
  return expected;
}
```

- [ ] **Step 4: 実行して通過を確認**

実行: `node --test tests/path/to/file.test.mjs`
期待: PASS

- [ ] **Step 5: commit**

```bash
git add tests/path/to/file.test.mjs src/path/to/file.mjs
git commit -m "feat: add specific feature"
```
````

## placeholder 禁止

各 step は実装者が必要とする実体を持つ。以下は **plan 失敗** — 絶対に書かない。

- "TBD" / "TODO" / "implement later" / "後で詳細"
- "appropriate error handling を追加" / "validation を追加" / "edge case を handle"
- "上記に対するテスト追加" (テストコード本体なし)
- "Task N と同様" (コードを再掲する — 実装者は順番通り読まないかもしれない)
- "何をするか" だけで "どうするか" を示さない step (コード step にはコードブロックが必須)
- どのタスクでも定義していない型 / 関数 / メソッドへの参照

## 守るべきこと

- 正確なファイルパスを毎回書く
- 各 step に完全なコードを置く (code を変える step なら code を書く)
- 正確なコマンド + 期待 output
- DRY / YAGNI / TDD / 頻繁な commit

## セルフレビュー

plan を書き終わったら、新鮮な目で spec と plan を突き合わせる。これは subagent ではなく自分でやる。

1. **spec カバー率:** spec の各セクション / 要件について、対応するタスクを指せるか? 漏れを列挙
2. **placeholder 走査:** 上の「placeholder 禁止」リストに当てはまる箇所を検索 → fix
3. **型一貫性:** 後タスクで使った型 / signature / プロパティ名が前タスクで定義したものと一致しているか? Task 3 で `clearLayers()` だったのに Task 7 で `clearFullLayers()` になっていたら bug
4. **PJ 規約整合:** PJ CLAUDE.md / `.claude/rules/` 配下に定義された原則 (例: Fail Fast、命名規約、コミット規約、外部 API の利用方針など) を侵害していないか

問題を見つけたら直接 inline で fix する。再レビューは不要、直して進む。spec 要件にタスクが対応していなければタスクを足す。

## 実装への引き継ぎ

実装スタイルは **brainstorming スキルの最後に決定済み** が前提。直交 2 軸 (`隔離: worktree or branch` × `並列: SDD or 直列`) で 4 択:

- **A. worktree + SDD** — 隔離環境 × subagent 駆動 (大規模 / 並列向け)
- **B. branch + 直列** — branch のみ、このセッションで私が順に実装 (小〜中規模 / 1 本道)
- **C. worktree + 直列** — worktree で隔離して直列、subagent なし
- **D. branch + SDD** — branch のみ、このセッションで SDD

ブランチ / worktree も brainstorming の段階で既に切られている。writing-plans はそれを前提に plan を書き、保存後はそのまま実装フェーズに引き継ぐ。

### brainstorming を経由せず writing-plans 単独起動した場合

spec / 要件はあるが brainstorming スキップで来た場合、ここで `AskUserQuestion` で 4 択を提示:

> plan を `.claude/plans/<filename>.md` に書きました。実装方式を選んでください (隔離 × 並列の 2 軸):
>
> - **A. worktree + SDD** — 隔離環境 × subagent 駆動 (大規模 / 並列向け)
> - **B. branch + 直列** — branch のみ、このセッションで順に実装 (小〜中規模 / 1 本道)
> - **C. worktree + 直列** — worktree で隔離して直列 (隔離は欲しいが subagent 起動コストは払わない)
> - **D. branch + SDD** — branch のみ、このセッションで SDD (worktree オーバーヘッドなしで並列だけ取る)

選択に応じた動作:

- **A / C (worktree あり)**:
  1. `using-git-worktrees` スキルを呼んで worktree 作成 (新規ブランチ付き)
  2. `cp .claude/plans/<filename>.md <worktree-path>/.claude/plans/<filename>.md` で plan ファイルを worktree に複製
  3. main 作業ツリー側の `.claude/plans/<filename>.md` を `rm` (untracked なので git 影響なし)
  4. 以降の作業は worktree 上で進める (A は `subagent-driven-development`、C は私が直列消化)
- **B / D (worktree なし)**:
  1. 現ディレクトリで `git switch -c <branch>` (main 直コミット禁止)
  2. plan ファイルはそのまま使う
  3. B はこのセッションで Task 1 から私が消化、D は `subagent-driven-development` を起動

### 4 択の選び方早見表

| | 直列 | SDD |
|---|---|---|
| **branch** | **B**: 最も軽量 / 1 本道向け | **D**: 並列したいが worktree オーバーヘッドなし。subagent 間のファイル競合に注意 |
| **worktree** | **C**: 隔離欲しいが subagent 起動コストは払わない | **A**: 大規模・並列。最も重装備 |

判断軸の詳細は `~/.claude/skills/brainstorming/SKILL.md` の「軸ごとの判断材料」参照。

**main 直コミット禁止** — 必ず branch または worktree に切り替えてから実装に入る。

## subagent レビュー (任意)

長大な plan の品質チェックには `plan-reviewer.md` の prompt テンプレートで subagent を派遣できる。
