---
name: cmux-update-check
description: Check cmux for available updates and list release notes between the current installed version and the latest GitHub release. Use when user says "cmux update", "cmuxアップデート", "cmuxの更新確認", "cmuxを更新", "cmuxのリリースノート", or asks what's new in cmux.
allowed-tools: "Bash, WebFetch"
---

# cmux アップデート確認

cmux の現在インストール済みバージョンと GitHub の Latest リリースを比較し、間に含まれるバージョンごとの更新点（注意点・破壊的変更・新機能）を列挙する。

## 手順

### 1. 現在のバージョンを取得

```bash
cmux --version
```

出力からバージョン文字列を抽出する（例: `cmux 0.1.42` → `0.1.42`）。  
`cmux` が PATH にない / 失敗した場合は、ユーザーにインストール状況を確認して中断。

### 2. Latest と中間バージョンの一覧を取得

`gh` CLI が使える環境なら **API 経由が最優先**（JS レンダリング不要・タグ一覧が確実に取れる）。

```bash
gh release list -R manaflow-ai/cmux --limit 50
gh release view --json tagName,name,publishedAt,body -R manaflow-ai/cmux   # Latest
```

`gh` が無い場合のみ WebFetch でフォールバック:

- `https://github.com/manaflow-ai/cmux/releases/latest` → Latest タグを確認
- `https://github.com/manaflow-ai/cmux/releases` → 一覧（ページ送りに注意、必要なら `?page=2`）

### 3. 範囲を決定（semver で必ず 3 分岐に振り分ける）

`v_current` と `v_latest` を semver 比較し、次の 3 つのいずれかに必ず分岐する。エッジを見落とさないこと。
比較前に両者の先頭 `v` プレフィックスを除去して揃える（`cmux --version` は `0.1.42`、GitHub のタグは `v0.1.42` のように表記が割れることがある）。出力・引用に使うタグ表記は `tagName` の値に統一する。

- **`v_current` < `v_latest`（更新あり）**: `(v_current, v_latest]` の範囲のリリースを対象にする（現在バージョン自身は含めない、Latest は含める）。手順 4 へ進む。
- **`v_current` == `v_latest`（最新）**: 「最新です（更新はありません）」と現在 / 最新を添えて報告し終了。手順 4 はスキップ。
- **`v_current` > `v_latest`（先行ビルド）**: 現在が公開 Latest より新しい（dev / プレリリース等）。**「最新です」とだけ言って先行している事実を隠さない**。「お使いのビルド `<v_current>` は最新公開リリース `<v_latest>` より新しい（開発 / プレリリースビルドと思われる）」旨を率直に報告して終了。changelog の捏造や負範囲の計算はしない。

「最新」「先行ビルド」分岐でユーザーが**リリースノートを明示的に要求**している場合のみ、最新公開リリースの実際の本文を **「これは適用すべき更新ではない（参考）」と明示した上で**添えてよい（捏造ではなく実データの参考提示。存在しないノートの創作は不可）。

### 4. 各リリースの本文を取得して要約

各タグについて:

```bash
gh release view <tag> -R manaflow-ai/cmux --json tagName,name,publishedAt,body
```

`gh` が無い場合のみ WebFetch:
`https://github.com/manaflow-ai/cmux/releases/tag/<tag>`

### 5. 出力フォーマット

手順 3 の分岐に応じて 2 つのテンプレートを使い分ける。いずれも日本語で出す。

**(A) 更新ありの場合**（`v_current` < `v_latest`）:

```
現在: <v_current>
最新: <v_latest>
適用範囲: <N> 件のリリース

## <tag> (<published date>)
### 注意点 / 破壊的変更
- ...
### 新機能 / 追加
- ...
### 修正 / その他
- ...

（以下、新しい順に各バージョン）

## まとめ
- 特に注意すべき項目: ...
- 推奨アクション: ...
```

**(B) 最新 / 先行ビルドの場合**（`v_current` == または > `v_latest`）: 「適用範囲」行・各リリース節・まとめ節は出さず、最小構成のみ。

```
現在: <v_current>
最新: <v_latest>
<状態文（「最新です（更新はありません）」または「お使いのビルドは最新公開リリースより新しい（先行ビルド）」）>
```

先行ビルドでユーザーがリリースノートを明示要求した場合のみ、この下に最新公開リリースの本文を
`## <tag> (<date>) ※参考・適用対象外` の見出しで添える（手順 3 の「先行ビルド」分岐を参照）。

抽出ルール（出力見出しは上記 3 つで固定。各 prefix の対応は以下）:

- **注意点 / 破壊的変更**: `Breaking`, `BREAKING CHANGE`, `⚠`, `Migration`, `Deprecated`, `Removed`, 設定ファイル/CLI 互換性に触れる項目
- **新機能 / 追加**: `feat`, `Add`, `New`, `Support`
- **修正 / その他**: `fix`, `chore`, `docs`, `refactor`, `perf`（性能改善や雑務もこの見出しに含む）
- リリース本文がコミットリスト形式（Conventional Commits）の場合は prefix で振り分ける
- 各項目の末尾に由来 prefix を `(fix)` `(perf)` のように併記し、どのルールで分類したか追えるようにする
- 該当が無いセクションは省略してよい

### 6. 列挙対象が多い場合

20 件を超える場合は、注意点 / 破壊的変更のあるバージョンだけを詳細に、それ以外は 1 行サマリで列挙する。

## 注意

- GitHub の rate limit を考慮し、`gh` CLI が使えるなら必ず優先する（認証済み枠を使える）。
- バージョン比較は semver 前提（`0.1.42` < `0.2.0` < `1.0.0`）。プレリリース（`-rc.1` 等）は明示的に除外せず、ユーザーが現在 prerelease を使っているか同一系列に居る場合のみ含める。現在版が Latest より新しいケースの扱いは手順 3 の「先行ビルド」分岐を参照。
