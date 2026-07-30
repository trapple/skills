#!/usr/bin/env bash
# popup 内で実行される: フォークした Claude Code セッションを起動する。
# CLAUDE_FORK_SID / CLAUDE_FORK_CWD は `herdr plugin pane open --env` 経由で渡される。
set -euo pipefail

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

sid="${CLAUDE_FORK_SID:?CLAUDE_FORK_SID is not set}"
cd "${CLAUDE_FORK_CWD:-$HOME}"

# claude が即死したときに popup が一瞬で閉じてエラーが読めなくなるのを防ぐ
if ! claude --resume "$sid" --fork-session; then
    status=$?
    echo
    echo "[herdr-fork-popup] claude exited with status $status. Press Enter to close."
    read -r
fi
