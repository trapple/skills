---
name: session-log
description: Dump the raw JSONL session log as a human-readable transcript. Use when user says "session log", "セッションログ", "生ログ見せて", "経緯見せて", or wants to inspect what happened earlier (tool calls, results, assistant replies) in the current or a specific Claude Code session.
argument-hint: "[--session <uuid|prefix>] [--list] [--full] [--tools-only] [--max-chars N]"
---

# session-log - セッション生ログ可視化

`~/.claude/projects/<proj>/<uuid>.jsonl` に保存されている Claude Code の生セッションログを、人間が読める形に整形して出力する。

## 重要: シークレットのマスク（必読）

出力する内容に **API キー / アクセストークン / パスワード / 秘密鍵 / `.env` の値** など機密情報と思われる文字列が含まれていたら、**必ず `****` で塗りつぶしてからユーザーに表示すること**。整形後のテキストはそのまま PR / Issue / Slack / ブログに貼られる可能性があり、生ログを横流しすると事故になる。

**マスク対象は出力されるすべてのブロック**: `tool_result` の中身はもちろん、`tool_use.input`（コマンドラインに API キーや `Authorization: Bearer` を直書きしているケースが多く、見落とすと事故になる）、`user` メッセージ本文（ユーザーが secret を貼り付けていることがある）、`assistant.text` も対象。整形構造のどこに出てきても塗る。

検出対象の例（疑わしきはマスク）:

- API キー prefix: `sk-...`, `sk-ant-...`, `pk-...`, `ghp_...`, `gho_...`, `ghs_...`, `xox[bp]-...`, `AKIA[0-9A-Z]{16}`, `AIza[0-9A-Za-z_-]{35}`, `xai-...`
- 認証ヘッダ: `Authorization: Bearer <...>`, `Authorization: Basic <...>`, `X-Api-Key: <...>`, `Cookie: <...>`
- 代入形式: `password=...`, `token=...`, `secret=...`, `api_key=...`, `PRIVATE_KEY=...`
- ブロック: `-----BEGIN ... PRIVATE KEY-----` 〜 `-----END ... PRIVATE KEY-----`
- ファイル: `.env` / `.env.*` / `credentials.json` / `id_rsa` 等の中身全文
- 接続文字列: `postgres://user:password@host/db`, `mysql://`, `mongodb://`, `redis://` 等のユーザー情報部
- その他: 32 文字以上の高エントロピー英数字列で文脈的にトークンに見えるもの

マスク方法:

- 値部分を `****` に置換する。識別性が欲しければ prefix だけ残す（例: `sk-ant-****`, `ghp_****`, `AKIA****`）。prefix は **トークン種別が識別できる程度（3〜8 文字目安）** に留め、それ以上は残さない
- ブロック型は `-----BEGIN ... PRIVATE KEY-----\n****\n-----END ... PRIVATE KEY-----` に短縮
- `.env` 行は `KEY=****` の形にする（KEY 名は残す）
- 接続文字列は user 部分は残してパスワード部のみ `****` にする（例: `postgres://dbuser:****@db.example.com:5432/myapp`）。URL 全体を塗ってもよい
- `Authorization: Bearer <token>` は `Authorization: Bearer ****` の形
- false positive（実は機密でないものを塗る）は許容。**false negative（漏らす）は不可**。迷ったら塗る

## いつ使うか

- ユーザーが「さっきのBashの経緯見せて」「直前のセッションログ見たい」などと言ったとき
- 自分（Claude）が「前のターンで何を実行したか」を取り戻したいとき
- Skill/slash command 開発のため、実際に流れたツール呼び出しを確認したいとき

## 引数

- `--session <uuid|prefix>`: 特定のセッションを指定（UUID全体 or 先頭数文字）
- `--list`: 現在の project dir 配下のセッション一覧だけ出す
- `--full`: tool_result を省略せずそのまま全部出す（デフォルトは長すぎる場合カット）
- `--tools-only`: ユーザー発話とアシスタント返答を省き、tool_use / tool_result だけ出す
- `--max-chars N`: tool_result の最大文字数（デフォルト 2000, `--full` 指定時は無制限）

引数なしなら「現在のプロジェクトの最新セッション」を整形して出す。

## 手順

### 1. プロジェクトディレクトリを特定

現在の cwd を `-Users-trapple--claude` 形式に変換する。変換ルール:

```
/ → -
. → -
```

実装:

```bash
PROJ=$(pwd | tr '/.' '--')
PROJ_DIR="$HOME/.claude/projects/$PROJ"
```

`$PROJ_DIR` が存在しない場合は、`cwd` フィールドで全セッションを grep して該当するものを探す（フォールバック）:

```bash
if [ ! -d "$PROJ_DIR" ]; then
  PROJ_DIR=$(grep -lF "\"cwd\":\"$(pwd)\"" ~/.claude/projects/*/*.jsonl 2>/dev/null \
             | head -1 | xargs -I{} dirname {})
fi
```

### 2. セッションファイルを決定

- `--session <x>` があれば `$PROJ_DIR/<x>*.jsonl` で先頭一致（prefix で OK）
- 無ければ `ls -t "$PROJ_DIR"/*.jsonl | head -1` で最新
- `--list` なら `ls -lt "$PROJ_DIR"/*.jsonl` を出して終了

### 3. jq で整形出力

基本ワンライナー（そのまま貼って使える形）:

```bash
SESSION=<path-to-jsonl>
MAX=2000  # --full なら 0 = 無制限

jq -r --argjson max "$MAX" '
  def clip(s): if $max == 0 or (s|length) <= $max
               then s
               else s[0:$max] + "\n…(truncated, " + ((s|length)-$max|tostring) + " more chars)" end;

  if .type=="user" and (.message.content|type)=="string" then
    "\n========== USER ==========\n" + .message.content + "\n"
  elif .type=="assistant" then
    (.message.content // [] | map(
      if .type=="thinking"   then "---------- THINKING ----------\n" + (.thinking // "(empty)")
      elif .type=="text"     then "---------- ASSISTANT ----------\n" + .text
      elif .type=="tool_use" then "---------- TOOL_USE: " + .name + " ----------\n" + clip(.input|tostring)
      else empty end) | join("\n\n"))
  elif .type=="user" and (.message.content|type)=="array" then
    (.message.content | map(
      if .type=="tool_result" then "---------- TOOL_RESULT ----------\n" + clip((.content // "")|tostring)
      else empty end) | join("\n\n"))
  else empty end
' "$SESSION"
```

`--tools-only` の場合は `user(string)` と `assistant.text` の分岐を `empty` に置き換えればよい。

### 4. 補足情報

最後にセッションのメタ情報を一行で添える（ユーザーが「どのセッション？」と分かるように）:

```bash
jq -sr '"\n# session: \(.[0].sessionId)  cwd: \(.[0].cwd)  branch: \(.[0].gitBranch // "-")  events: \(length)"' "$SESSION"
```

`-s`（slurp）で全イベントを配列にしてから、メタ情報は `.[0]` から取り、`events` は配列全体の `length` を使う。`.[0] | length` の形にすると最初のオブジェクトのキー数になってしまうので注意。

## 観測済みの仕様メモ

- イベントタイプ: `user` / `assistant` / `system` / `attachment` / `file-history-snapshot` / `permission-mode` / `last-prompt`
- `user` の `message.content` は **string（素の入力）** と **array（tool_result ブロック）** の2パターンある
- `assistant` の `message.content` は `thinking` / `text` / `tool_use` の配列
- `thinking` ブロックはローカルJSONLでは本文が空のことが多い（Opus の思考トークンは残らない）
- `tool_result.content` は巨大になりうる（数MB級もある）ので、デフォルトは `--max-chars` で抑える
- サブエージェント経由の子セッションは `isSidechain: true` で別ファイル `<uuid>/` ディレクトリ下に保存される
- ログは `chmod 600` でローカル保存、クラウド同期はされない

## ユーザーへの返し方

- 整形出力は**必ずシークレットをマスクしてから**見せる（冒頭「シークレットのマスク」節参照）。生の jq 出力をそのままユーザーに渡すのは禁止
- 実行コマンド（jq ワンライナー）と整形出力を両方見せる（ユーザーが後で自分でも叩けるように）。実行コマンド自体にシークレットは入らないが、整形出力側はマスク後を表示
- 長大な場合は冒頭だけ本文表示、残りは「`$SESSION` に保存済み（**未マスクなので外部に貼らないこと**）」と示して終了
- 「さっきのエラーの原因だけ知りたい」のような要求なら、出力を grep してから見せる（grep 結果もマスク対象）
