# Fable 5 プロンプティングパターン（参照資料）

出典: [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)（Anthropic公式ドキュメント、2026年時点）

各項目は `SKILL.md` のチェックリスト番号と対応する。指示文言（コードブロック内）はドキュメントからの引用（英語）。対象文書に組み込むときは、文脈に合わせて改変し、必要なら自然な日本語に翻訳してよい。

## Fable 5 の能力向上点（Opus 4.8比）

- 長時間自律実行（long-horizon autonomy）: 数日規模のゴール志向タスクを、複雑な長時間タスクでも高い指示保持率で完遂できる
- 複雑かつ仕様の明確なタスクの一発正答率
- 視覚認識: 高密度な技術画像・Webアプリ・詳細スクリーンショットの解釈精度、出力トークン効率
- エンタープライズワークフロー: 財務分析・スプレッドシート・スライド・文書作成でのスコープ遵守と品質
- コードレビュー・デバッグ: バグ発見のリコール向上（攻撃的サイバーセキュリティ領域を除く）
- 曖昧さへの対応: 複雑でマルチスレッドな依頼から次のアクションを決める能力
- 委任・協調: 並列サブエージェントの派遣・維持、長時間稼働するサブエージェント/ピアエージェントとの継続的なやり取り

Fable 5 は攻撃的サイバーセキュリティおよびバイオ/ライフサイエンス領域の作業を意図的にサポートしない（該当すると `stop_reason: "refusal"` を返しうる）。良性の作業でも安全分類器が誤検知することがあるため、API利用時は Opus 4.8 への server-side/client-side fallback 設定を検討する。

---

## (1) 長いターンがデフォルトになる／過剰計画の抑制

高effortでは1リクエストが数分〜、自律実行では数時間に及ぶことがある。クライアントのタイムアウト・ストリーミング・進捗表示の見直しが必要。曖昧なタスクで計画倒れしないよう、以下のような指示が有効:

```text
When you have enough information to act, act. Do not re-derive facts already
established in the conversation, re-litigate a decision the user has already
made, or narrate options you will not pursue in user-facing messages. If you
are weighing a choice, give a recommendation, not an exhaustive survey. This
does not apply to thinking blocks.
```

## (2) effortレベルの使い分け

effortは知能/レイテンシ/コストのトレードオフを制御する主要パラメータ。

- `high`: ほとんどのタスクのデフォルト
- `xhigh`: 最も能力が問われるワークロード
- `medium`/`low`: 日常的な定型作業

Fable 5では低effortでも旧モデルのxhighを上回ることが多い。完了はするが時間がかかりすぎる、もっと対話的なテンポにしたい場合はeffortを下げる。一方、高effortでは日常タスクに対して過剰にコンテキスト収集・熟考しがちなので、過剰な整理整頓・リファクタを抑える指示が有効:

```text
Don't add features, refactor, or introduce abstractions beyond what the task
requires. A bug fix doesn't need surrounding cleanup and a one-shot operation
usually doesn't need a helper. Don't design for hypothetical future
requirements: do the simplest thing that works well. Avoid premature
abstraction and half-finished implementations. Don't add error handling,
fallbacks, or validation for scenarios that cannot happen. Trust internal
code and framework guarantees. Only validate at system boundaries (user
input, external APIs). Don't use feature flags or backwards-compatibility
shims when you can just change the code.
```

## (3) 指示追従が強力／簡潔な誘導で足りる

逐一列挙しなくても短い指示で行動を制御できる。無指示だと、試さない選択肢の列挙・長い原因説明・過剰構造化されたPR説明・自明なことを説明するコメントなど、必要以上に冗長になりやすい。簡潔さの指示例:

```text
Lead with the outcome. Your first sentence after finishing should answer
"what happened" or "what did you find": the thing the user would ask for if
they said "just give me the TLDR." Supporting detail and reasoning come
after. Being readable and being concise are different things, and
readability matters more.

The way to keep output short is to be selective about what you include (drop
details that don't change what the reader would do next), not to compress
the writing into fragments, abbreviations, arrow chains like A → B →
fails, or jargon.
```

チェックポイント（ユーザーに確認を取るべき場面）も、個別ケースを列挙するのではなく一文で絞り込める:

```text
Pause for the user only when the work genuinely requires them: a destructive
or irreversible action, a real scope change, or input that only they can
provide. If you hit one of these, ask and end the turn, rather than ending
on a promise.
```

## (4) 長時間実行中の進捗申告を事実に基づかせる

進捗のでっち上げ報告を防ぐ指示（Anthropic社内テストでほぼ解消したと報告されている）:

```text
Before reporting progress, audit each claim against a tool result from this
session. Only report work you can point to evidence for; if something is
not yet verified, say so explicitly. Report outcomes faithfully: if tests
fail, say so with the output; if a step was skipped, say that; when
something is done and verified, state it plainly without hedging.
```

## (5) 境界を明示する

頼まれていない行動（勝手なメール下書き、防御的なgit branch作成など）を防ぐ、明示的な制約の例:

```text
When the user is describing a problem, asking a question, or thinking out
loud rather than requesting a change, the deliverable is your assessment.
Report your findings and stop. Don't apply a fix until they ask for one.
Before running a command that changes system state (restarts, deletes,
config edits), check that the evidence actually supports that specific
action. A signal that pattern-matches to a known failure may have a
different cause.
```

## (6) 並列サブエージェント

Fable 5は以前より積極的にサブエージェントを併用する。委任基準を明示し、ブロッキングではなく非同期のやり取りを優先させる:

```text
Delegate independent subtasks to subagents and keep working while they run.
Intervene if a subagent goes off track or is missing relevant context.
```

長時間稼働し、サブタスク間でコンテキストを保持し続けるサブエージェントは、キャッシュ読み取りによるコスト削減と、最も遅いサブエージェントへのボトルネック回避に有効。

## (7) メモリシステムの構築

過去の教訓を記録・参照させると成績が上がる。シンプルなMarkdownファイルでよい:

```text
Store one lesson per file with a one-line summary at the top. Record
corrections and confirmed approaches alike, including why they mattered.
Don't save what the repo or chat history already records; update an
existing note rather than creating a duplicate; delete notes that turn out
to be wrong.
```

過去セッションからメモリをブートストラップする指示例:

```text
Reflect on the previous sessions we've had together. Use subagents to
identify core themes and lessons, and store them in [X]. Make sure you know
to reference [X] for future use.
```

## (8) 早期停止のレアケース

長時間セッションの終盤で「これから実行します」とだけ言ってツール呼び出しをせずに終了したり、既に十分な情報があるのに許可を求めて止まったりすることがある。自律パイプライン向けのシステムリマインダー例（(3)のチェックポイント指示とセットで使う）:

```text
You are operating autonomously. The user is not watching in real time and
cannot answer questions mid-task, so asking "Want me to...?" or "Shall
I...?" will block the work. For reversible actions that follow from the
original request, proceed without asking. Offering follow-ups after the
task is done is fine; asking permission after already discussing with the
user before doing the work is not. Before ending your turn, check your last
paragraph. If it is a plan, an analysis, a question, a list of next steps,
or a promise about work you have not done ("I'll...", "let me know
when..."), do that work now with tool calls. End your turn only when the
task is complete or you are blocked on input only the user can provide.
```

## (9) コンテキスト予算への過剰反応のレアケース

ハーネスが残トークンのカウントダウンを見せると、新セッション提案や要約・作業縮小をすることがある。可能ならカウントダウン自体を見せない方がよいが、見せる必要がある場合は安心付与の一文を添える:

```text
You have ample context remaining. Do not stop, summarize, or suggest a new
session on account of context limits. Continue the work.
```

## (10) 依頼理由を伝える

背景・目的を伝えると、意図を汲んだ動きをしやすい。特に複数ワークストリームにまたがる長時間エージェントで有効な定型文:

```text
I'm working on [the larger task] for [who it's for]. They need [what the
output enables]. With that in mind: [request].
```

## (11) ユーザー向け説明の読みやすさ

ツール呼び出し間の省略記法（思考の垂れ流し）自体は問題ないが、最終サマリーはそれを見ていない読者向けに書き直すべき。矢印チェーンやハイフン連結、独自略語を避け、結論から完全な文で書かせる指示:

```text
Terse shorthand is fine between tool calls (that's you thinking out loud,
and brevity there is good). Your final summary is different: it's for a
reader who didn't see any of that.

If you've been working for a while without the user watching (overnight,
across many tool calls, since they last spoke), your final message is their
first look at any of it. Write it as a re-grounding, not a continuation of
your working thread: the outcome first, then the one or two things you need
from them, each explained as if new. The vocabulary you built up while
working is yours, not theirs; leave it behind unless you re-introduce it.

When you write the summary at the end, drop the working shorthand. Write
complete sentences. Spell out terms. Don't use arrow chains, hyphen-stacked
compounds, or labels you made up earlier. When you mention files, commits,
flags, or other identifiers, give each one its own plain-language clause.
Open with the outcome: one sentence on what happened or what you found.
Then the supporting detail. If you have to choose between short and clear,
choose clear.
```

## (12) 内部推論をレスポンス本文で再現させない

Claudeに内部推論をエコー・書き写し・説明として応答本文に再現させる指示（「reasoningを説明せよ」「思考過程を書け」等）は `reasoning_extraction` 拒否カテゴリを誘発し、Opus 4.8への意図しないfallbackを増やす。既存のskill・システムプロンプトにこの種の「reflectionせよ」「示せ」指示がないか監査し、あれば除去する。推論の可視性が必要な場合は:

- API側で adaptive thinking の構造化 `thinking` ブロックを読む
- 進捗の可視化には (13) の send-to-user パターンを使う

## (13) send-to-userツールの新設

長時間・非同期のエージェントでは、ターンを終了せずにユーザーに逐語で見せるべきメッセージ（進捗の具体的な数値、生成した成果物、ループ中に聞かれた質問への直接回答）を送る手段が要る。ツール定義例:

```json
{
  "name": "send_to_user",
  "description": "Display a message directly to the user. Use this for progress updates, partial results, or content the user must see exactly as written before the task finishes.",
  "input_schema": {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "description": "The content to display to the user."
      }
    },
    "required": ["message"]
  }
}
```

ツール呼び出し時は入力（message）をUI上にそのまま描画し、ツール結果は単純な受領確認を返す。ツール入力は要約されないため内容がそのまま届く。ツール定義だけでは呼ばれないため、システムプロンプトに誘導文を必ずペアで入れる:

```text
Between tool calls, when you have content the user must read verbatim (a
partial deliverable, a direct answer to their question), call the
send_to_user tool with that content. Use send_to_user only for user-facing
content, not for narration or reasoning.
```

ナレーションや内部推論をこのツール経由にしないよう注意する。定型的な進捗ナレーションだけのエージェントであれば、モデル自身の要約で十分でありこのツールは不要。

---

## 推奨されるスキャフォールディング変更（全体方針）

- 従来より難しいタスクの範囲上限を上げてFable 5に任せてみる（スコーピングや確認質問も含めて委任する）
- 長時間タスクでは自己検証を明示的に指示する。自己批評よりfresh-contextの検証専用サブエージェントの方が優れる傾向:
  ```text
  Establish a method for checking your own work at an interval of [X] as you
  build. Run this every [X interval], verifying your work with subagents
  against the specification.
  ```
- 旧モデル向けに書かれた既存プロンプト/skillを見直す。過剰に規定的な記述はFable 5の出力品質をむしろ下げうるため、デフォルト挙動の方が良い場合は古い指示を削除する。Fable 5はタスク中に学んだことを元にskill自体をその場で更新するのも得意
- (12)の内部推論書き出し指示の監査
- (13)のsend-to-userツールの新設検討
