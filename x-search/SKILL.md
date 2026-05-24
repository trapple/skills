---
name: x-search
description: Hermes Agent の x_search_tool を呼び出して X (Twitter) を Grok で検索する。Grok による検索結果分析が Markdown (脚注付き URL 引用) で返る。hermes-agent は `uv tool install` でローカル固定済み (毎回 git fetch しない)。Use when user says "x_search", "x-search", "xサーチ", "Xで検索", "Xで調べて", "X検索", "ツイッターで調べて", "Twitterで調べて", "Grok で X を検索", or asks to look up trending posts / sentiment / discussions on X.
---

# x-search

X (Twitter) を Grok 経由で検索するスキル。Hermes Agent の Python API (`tools.x_search_tool`) を、`uv tool install` でローカル固定した hermes-agent venv の Python から直接呼び出す (毎回 git fetch しない / ネットアクセスは初回インストール時のみ)。

## 前提 (ユーザー側で1度だけ手動実行が必要)

以下が未実行の場合、まずユーザーに案内すること。スキル内では自動化しない (ブラウザ操作・グローバル副作用を伴うため)。

1. **uv のインストール**: https://docs.astral.sh/uv/getting-started/installation/
2. **hermes-agent のローカルインストール**:
   ```
   uv tool install git+https://github.com/NousResearch/hermes-agent
   ```
   `~/.local/share/uv/tools/hermes-agent/` 配下に専用 venv が作られ、`hermes` / `hermes-acp` / `hermes-agent` の 3 実行ファイルが `~/.local/bin/` に symlink される。

   - 更新: `uv tool upgrade hermes-agent`
   - アンインストール: `uv tool uninstall hermes-agent`
   - hermes-agent は PyPI に未公開なので、必ず `git+https://...` を指定する (`uv tool install hermes-agent` だけだと `No solution found` で失敗する)

3. **xAI OAuth 認証**:
   ```
   hermes auth add xai-oauth
   ```
   表示された URL をブラウザで開いて認証する。リモート (SSH) の場合は SSH ポートフォワード + `--no-browser` を使う:
   ```
   ssh -L 56121:127.0.0.1:56121 user@remote-host \
     'hermes auth add xai-oauth --no-browser'
   ```

xAI のサブスクリプション (X Premium) が必要。

### `HERMES_HOME` の注意 — グローバル認証 vs プロジェクトローカル認証

Hermes は credential を `$HERMES_HOME/auth.json` に保存する。`HERMES_HOME` が未設定なら `~/.hermes` がデフォルト。

このスキルは**グローバルスキル**として全プロジェクトから呼ばれるが、credential は `HERMES_HOME` ごとに別ファイルになる点に注意。

**推奨セットアップ: グローバル認証**

direnv が効かない場所 (例: ホームディレクトリ) で1回認証して `~/.hermes/auth.json` を作る:

```
cd ~
hermes auth add xai-oauth
```

これで direnv 未設定のプロジェクトすべてからスキルが動く。

**direnv 等で `HERMES_HOME` をプロジェクトローカルに上書きしている場合**

例: `<project>/.envrc` で `export HERMES_HOME=$PWD/.hermes` のような上書きがある場合、そのプロジェクト内では `~/.hermes` ではなく `<project>/.hermes` が使われる。

- そのプロジェクト内で x_search を使いたい場合は、**そのディレクトリ内で別途認証**が必要 (`cd <project> && hermes auth add xai-oauth`)
- 認証ディレクトリと実行ディレクトリの `HERMES_HOME` が一致していないと `No xAI credentials available` で失敗する

**切り分け**

x_search 実行前に以下で確認:
```
echo "HERMES_HOME=$HERMES_HOME"          # 未設定なら ~/.hermes が使われる
ls "${HERMES_HOME:-$HOME/.hermes}/auth.json"  # credential ファイルがあるか
hermes auth list
# → "xai-oauth (N credentials)" が表示されれば OK
```

`xai-oauth` が出てこなければ、その `HERMES_HOME` には認証情報がないので、その場所で認証コマンドを実行する必要がある。

## 実行方法

Bash で以下を実行する。クエリは自然文 (日本語/英語どちらでも可)。`uv tool install` で固定済みの hermes-agent venv の Python を直接叩く (PATH を通す必要は無い)。

```
~/.local/share/uv/tools/hermes-agent/bin/python ~/.claude/skills/x-search/run_x_search.py "<クエリ>"
```

- 既定では `answer` (Markdown, 脚注付き URL 引用) のみを stdout に出力する
- `--raw` を末尾に付けると JSON 全体 (citations / inline_citations / model 等) を出力する

例:
```
~/.local/share/uv/tools/hermes-agent/bin/python ~/.claude/skills/x-search/run_x_search.py "What are people saying about xAI on X?"
```

```
~/.local/share/uv/tools/hermes-agent/bin/python ~/.claude/skills/x-search/run_x_search.py "最近の Claude Code に関する反応" --raw
```

## Bash 実行時の注意

- **タイムアウト**: x_search は 30 秒以上かかることがある。Bash 呼び出し時の `timeout` は **300000 (5分)** 程度を指定すること
- **クエリのクオート**: シェルに渡すクエリは必ず `"..."` でクオートする (空白・記号・日本語のため)
- ローカル固定済みなので uvx の毎回の git fetch / 初回環境構築待ちは発生しない

## 出力の扱い方

- 返ってくる Markdown には `[[N]](https://x.com/...)` 形式の脚注付き URL 引用が含まれる。**そのままユーザーへの回答に含めて構わない** (参照性が高い)
- ユーザーが「生データが欲しい」「引用 URL 一覧が欲しい」と言った場合は `--raw` で JSON を取得し `inline_citations` を整形して返す
- ユーザーが「元ポストの実テキストが欲しい」と言った場合はクエリ自体に「該当ポストの本文も引用して返答してください」等を含める

## エラー対処

- **認証エラー (xai-oauth 未設定 / 期限切れ)**: ユーザーに `hermes auth add xai-oauth` の (再) 実行を促す
- **ModuleNotFoundError: tools.x_search_tool / hermes パスエラー**: ローカル固定された hermes-agent が古い。`uv tool upgrade hermes-agent` を促す
- **`~/.local/share/uv/tools/hermes-agent/bin/python: No such file or directory`**: 前提セットアップ未完了。`uv tool install git+https://github.com/NousResearch/hermes-agent` を促す
- **success: false の JSON**: stderr に JSON 全体を出力して終了コード 1 を返すので、内容をユーザーに提示

## 制約

- これは Grok による検索結果の**分析**であって、X の検索 API そのものではない
- レスポンスは Markdown で要約済み。生ツイートの一覧は得られない (クエリで指示しても完全な raw データにはならない)
- Grok の知識カットオフ・解釈バイアスが乗る
