---
name: using-git-worktrees
description: "Use when starting feature work that needs isolation from current workspace or before executing implementation plans — ensures an isolated workspace exists. Use when user says \"worktree\", \"並行開発\", \"並列実装\", \"隔離環境\", \"using-git-worktrees\"."
---

# using-git-worktrees — 隔離 workspace を確保する

並行開発のため、独立した workspace を用意する。プラットフォームのネイティブ worktree ツールを最優先、無ければ `git worktree add` フォールバック。

**Core principle:** **既存の隔離を先に検出する**。そのあと native tools。最後に git。harness と戦わない。

**着手の合図:** `using-git-worktrees スキルで隔離 workspace を用意します。` と 1 行宣言してから始める。

## Step 0: 既存の隔離を検出する

新しい worktree を作る前に、**いま既に linked worktree の中にいないか** 確認する。

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**submodule gard:** `GIT_DIR != GIT_COMMON` は submodule の中でも true。「既に worktree にいる」と判断する前に submodule でないことを確認:

```bash
# パスが返ったら submodule の中。worktree ではない (通常の repo として扱う)
git rev-parse --show-superproject-working-tree 2>/dev/null
```

**判定:**
- `GIT_DIR != GIT_COMMON` かつ submodule でない → 既に linked worktree 内。Step 2 (project setup) へ。**新しい worktree を作らない**
- `GIT_DIR == GIT_COMMON` か submodule の中 → 通常 repo checkout。Step 1 へ

報告例:
- on branch: `既に隔離 workspace 内: <path> on <branch>`
- detached HEAD: `既に隔離 workspace 内: <path> (detached HEAD, 外部管理。完了時に branch 作成が必要)`

ユーザーが指示で worktree 利用方針を表明済みなら、それに従う。表明が無ければ、新規 worktree 作成前に同意を取る:

> 隔離 worktree を切ってもいいですか? 現在の branch に変更が漏れないようにします。

declined なら in-place で作業して Step 2 へ。

## Step 1: 隔離 workspace を作る

**2 段構え。順に試す。**

### 1a. Native worktree ツール (優先)

cmux のような外部ツール / harness の `EnterWorktree` / `WorktreeCreate` / `/worktree` コマンドが使えるか確認する。あれば **必ずそちらを使う**。

native ツールは:
- ディレクトリ配置を自動で決める
- branch 作成 / cleanup まで面倒見る
- harness が状態を tracking できる (`git worktree add` で作ると harness から不可視の phantom state ができる)

cmux 上の運用なら、cmux 側の worktree 機能を優先する。判断不能なら **ユーザーに聞く**。

native ツールがない確証が取れたら 1b へ。

### 1b. git worktree フォールバック

#### 配置先

優先順位 (上が強い):

1. **ユーザーが事前に declare している場所** — それに従う
2. **既存の project-local worktree ディレクトリ:**
   ```bash
   ls -d .claude/worktrees 2>/dev/null
   ls -d .worktrees 2>/dev/null
   ls -d worktrees 2>/dev/null
   ```
   PJ で既にいずれかが使われているならそれを採用する
3. それも無ければ `.claude/worktrees/` (project root 直下、hidden) を default にする

#### .gitignore 確認 (project-local の場合は必須)

worktree を作る **前** に対象 dir が ignored か確認:

```bash
git check-ignore -q .claude/worktrees 2>/dev/null && echo "ignored" || echo "NOT IGNORED"
```

**ignored でないなら:** .gitignore に追記して commit してから作成する:

```bash
echo ".claude/worktrees/" >> .gitignore
git add .gitignore
git commit -m "chore: ignore .claude/worktrees/"
```

**なぜ critical か:** worktree の中身が誤って commit されると、main branch の git log が汚れる。

#### worktree 作成

```bash
BRANCH_NAME="<branch-name>"
LOCATION=".claude/worktrees"
PATH_FULL="$LOCATION/$BRANCH_NAME"

git worktree add "$PATH_FULL" -b "$BRANCH_NAME"
cd "$PATH_FULL"
```

**sandbox fallback:** `git worktree add` が permission error で落ちたら、sandbox がブロックしている可能性が高い。ユーザーに「sandbox に阻まれたので in-place で作業します」と告げて Step 2 を current dir で実行する。

## Step 2: project setup

worktree 直後に PJ の依存解決 / build setup を走らせる。**PJ のマニフェストから package manager を検出して install を実行する**。`node_modules/` 等の install 成果物は通常 `.gitignore` 対象なので worktree ごとに独立する。native binding (`better-sqlite3` / `sharp` / `node-gyp` 系) を持つ PJ では worktree でも再 install が必要。

検出順 (見つかったものを実行):

| マニフェスト | コマンド例 |
|------|------|
| `pnpm-lock.yaml` | `pnpm install` |
| `yarn.lock` | `yarn install` |
| `bun.lockb` | `bun install` |
| `package-lock.json` / `package.json` | `npm install` |
| `uv.lock` / `pyproject.toml` | `uv sync` (or `pip install -e .`) |
| `requirements.txt` | `pip install -r requirements.txt` |
| `Gemfile.lock` / `Gemfile` | `bundle install` |
| `Cargo.toml` | `cargo build` (deps は fetch される) |
| `go.mod` | `go mod download` |
| `Makefile` (`install` / `setup` target) | `make install` |
| 独自 setup script (`scripts/setup.sh` 等) | それを実行 |

sub-project (monorepo の workspace、native app 等) があり今回触らないなら skip してよい。判断不能なら PJ README / CLAUDE.md を確認、それでも分からなければユーザーに聞く。

## Step 3: baseline テスト

worktree が clean state で始まることを確認する。**PJ の標準テストコマンド** を実行する。

候補の検出順:

- `package.json` の `scripts` に `test` / `test:unit` / `test:lib` 等 → `npm test` (or pnpm/yarn 系)
- `Makefile` の `test` target → `make test`
- `Cargo.toml` → `cargo test`
- `go.mod` → `go test ./...`
- `pyproject.toml` + `pytest` → `pytest` / `uv run pytest`
- 独自スクリプト (`scripts/test*.sh`) → それを実行

PJ CLAUDE.md / README に「主要テストコマンド」が明示されていればそれを優先する。

**pass しないとき:** どのテストが落ちているか報告し、続行可否を確認する。既存の不安定テストなのか、worktree 作成時点で broken なのかを切り分ける。

**pass したとき:** 完了報告:

```
Worktree ready at <full-path>
Tests: <N> passing, 0 failing
Branch: <branch-name>
Ready to implement <feature-name>.
```

テスト基盤が存在しない PJ の場合は build / lint を代替に使い、「テスト不在のため build のみで baseline 確認」と明示する。

## クイック対応表

| 状況 | アクション |
|------|----------|
| 既に linked worktree 内 | Step 0 で検出して新規作成しない |
| submodule 内 | 通常 repo として扱う |
| cmux 等 native tool あり | それを使う (Step 1a) |
| native tool なし | git worktree fallback (Step 1b) |
| `.claude/worktrees/` 存在 | これを使う (ignored 確認後) |
| ignored になっていない | .gitignore 追記 → commit してから worktree 作成 |
| permission error | sandbox fallback、in-place 作業 |
| baseline テスト fail | 報告して続行可否を聞く |

## よくあるミス

- **harness と戦う:** native worktree tool があるのに `git worktree add` で作る → phantom state
- **検出を skip:** linked worktree の中で重ねて worktree を作って迷子
- **ignored 確認 skip:** worktree 内のファイルが git status に出てきて事故
- **配置先決め打ち:** 慣習を見ずに `tmp/` 等に作る
- **fail したテストを無視して進む:** 後で「新規変更で壊れた」のか「最初から壊れていた」のか分からなくなる
- **install を skip:** native binding 系 (`better-sqlite3` / `sharp` / `node-gyp`) は worktree でも install が必要

## Red Flags

**やってはいけない:**
- Step 0 で既に隔離だと検出されたのに worktree を作る
- native worktree tool があるのに `git worktree add` を使う (一番ありがちな罠 — あれば必ず使う)
- Step 1a を skip して直接 Step 1b に飛ぶ
- `.gitignore` 確認なしで project-local worktree を作る
- baseline test を skip する
- failing test を確認せずに進む

**必ずやる:**
- Step 0 検出を最初に
- native tool > git fallback
- 配置先優先順位: ユーザー指示 > 既存 dir > default
- project-local なら `.gitignore` 確認 → 追記 → commit
- PJ の package manager を検出して install
- baseline test 実行
