---
name: fable5-prompt-tuning
description: Diagnose and rewrite instructions (system prompts, Claude Code skills, CLAUDE.md, agent prompts) to match Claude Fable 5's behavior instead of older models like Opus 4.8 — trims over-prescriptive control, adds explicit boundaries, grounds long-run progress claims in tool evidence, advises on effort settings. Use when user says "Fable5向けに最適化", "Fable 5 prompting", "fable5チューニング", "このプロンプトをFable5向けに直して", or asks to adapt/review a prompt, skill, or CLAUDE.md for Claude Fable 5 / Mythos 5.
argument-hint: "[対象ファイルパス or 貼り付けテキスト]"
---

# Fable 5 向け指示最適化

渡された指示文書（システムプロンプト / skill の `SKILL.md` / `CLAUDE.md` / エージェント向けプロンプトなど）を Claude Fable 5（/ Mythos 5）の挙動特性に照らして診断し、Before/After の差分形式で修正案を提示する。目的は元ネタページの暗唱ではなく文書を直すこと。該当項目がなければ「変更不要」と結論してよい。

各項目の背景・根拠と、そのまま/文脈に合わせて使える指示文言（[Anthropic公式ガイド](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)からの引用）は同梱の `patterns.md` にある。**診断前に必ず読むこと。**

## 手順

1. **対象文書を読み、性質を見極める。** 短い一発タスク向けか、長時間自律実行・サブエージェント委任を伴うか。実行環境も確認する: effort は API パラメータ／ハーネスのセッション設定であり、CLAUDE.md や skill 本文からは制御できない。その場合 (2) は文書修正ではなくユーザーへの運用助言として出す。

2. **診断チェックリストを当てる**（番号は `patterns.md` の節に対応）:
   - [ ] (1) 長時間実行を想定しているのに、過剰計画の抑制やクライアント側タイムアウト/進捗表示への言及がない — Fable 5 は高 effort で1リクエストが長時間化し、自律実行は数時間に及ぶ
   - [ ] (2) effort 設定への言及・推奨がない — effort が知能/レイテンシ/コストの主要コントロール。既定 `high`、最重要 `xhigh`、定型 `medium`/`low`
   - [ ] (3) 手順・選択肢・ユーザー確認場面を逐一列挙している — Fable 5 は指示追従が強く、短い誘導文で足りる。列挙は削って推奨に一本化できないか
   - [ ] (4) 長時間実行なのに、進捗報告をツール結果で裏付けさせる指示がない — でっち上げ報告対策
   - [ ] (5) やって良いこと/悪いことの境界が曖昧 — 頼まれていない行動（勝手なメール下書き・防御的 git branch 作成等）対策
   - [ ] (6) サブエージェントの委任基準がない、またはブロッキング前提になっている — Fable 5 は並列・非同期の委任が得意
   - [ ] (7) 教訓を記録・参照するメモリの仕組みがなく、あると効く性質のタスクである
   - [ ] (8) 自律パイプラインなのに「完了 or ユーザーしか出せない入力待ち以外でターンを終えるな」がない — 「これからやります」で止まる早期停止対策
   - [ ] (9) ハーネスが残コンテキストを見せるのに、安心付与の一文がない — 新セッション提案・作業縮小対策
   - [ ] (10) 依頼の背景・目的（Why）が書かれていない
   - [ ] (11) 最終サマリーの可読性指示がない — 矢印チェーン・独自略語のまま報告してくる対策
   - [ ] (12) 内部推論を本文に書き出させる指示（「思考過程を書け」等）がある — `reasoning_extraction` 拒否と Opus 4.8 への fallback を誘発。除去し、thinking ブロック読み取りか send-to-user に置き換える
   - [ ] (13) 長時間非同期タスクなのに、途中経過を逐語で見せる手段（send-to-user ツール）がない

3. **該当項目だけ Before/After の diff 形式で提案する。** `patterns.md` の文言は文脈に合わせて改変し、日本語文書には自然な日本語に訳す。文書の性質に無関係な項目（例: 短い一発タスクの skill への進捗申告対策）は挙げない。適用はユーザーの承認後、全文書き換えではなく該当箇所への差分で行う。
