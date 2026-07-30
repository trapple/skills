#!/usr/bin/env bash
#
# herdr-fork-claude-session [direction]
#
# Based on herdr-fork.sh by Tatsuhiko Miyagawa (@miyagawa):
#   https://gist.github.com/miyagawa/cb1a9f6c8695d1219efba0c66d5f78f7
# Modifications: PATH bootstrap for Herdr keybinding shells, server-reachability
# guard instead of HERDR_ENV, and a `tab` direction that opens a focused new tab.
#
# Fork the current Claude Code session into a new Herdr pane.
# The fork inherits this session's full conversation history under a NEW session
# ID; the original session is left unchanged (see `claude --fork-session`).
#
#   direction   right (default) | down  -- which way to split off the new pane
#
# Requirements: run from inside a Herdr-managed pane (HERDR_ENV=1). The session
# ID comes from CLAUDE_CODE_SESSION_ID; if that is unset, it falls back to the
# session ID of the currently focused Herdr Claude agent. Needs python3 for JSON.
set -euo pipefail

# herdr キーバインド (type="shell") は最小 PATH で走るため、herdr / claude / python3 を解決できるよう補強
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

# herdr キーバインドの shell には HERDR_ENV が渡らないため、サーバー到達性でガードする (gist から変更)
if ! herdr status server >/dev/null 2>&1; then
    echo "herdr-fork-claude-session: no reachable Herdr server" >&2
    exit 1
fi

sid="${CLAUDE_CODE_SESSION_ID:-}"
if [ -z "$sid" ]; then
    # Fall back to the session ID of the currently focused Herdr agent.
    if ! sid=$(herdr agent list |
        python3 -c "
import sys, json
agents = json.load(sys.stdin)['result']['agents']
focused = [a for a in agents if a.get('focused')]
if not focused:
    sys.exit('no focused agent found')
a = focused[0]
if a.get('agent') != 'claude':
    sys.exit(\"focused agent is '%s', not claude\" % a.get('agent'))
print(a['agent_session']['value'])
"); then
        echo "herdr-fork-claude-session: CLAUDE_CODE_SESSION_ID is not set and could not resolve the focused Claude session" >&2
        exit 1
    fi
fi

direction="${1:-right}"
case "$direction" in
    right | down | tab) ;;
    *)
        echo "herdr-fork-claude-session: direction must be 'right', 'down' or 'tab', got '$direction'" >&2
        exit 1
        ;;
esac

if [ "$direction" = "tab" ]; then
    pane=$(herdr tab create --cwd "$PWD" |
        python3 -c "import sys, json; print(json.load(sys.stdin)['result']['root_pane']['pane_id'])")
    # タブ版は「開いたのに何も変わらない」ように見えるため、新しいタブへフォーカスを移す
    tab_id=$(herdr pane get "$pane" |
        python3 -c "import sys, json; print(json.load(sys.stdin)['result']['pane']['tab_id'])")
    herdr tab focus "$tab_id" >/dev/null
else
    pane=$(herdr pane split --current --direction "$direction" --cwd "$PWD" --no-focus |
        python3 -c "import sys, json; print(json.load(sys.stdin)['result']['pane']['pane_id'])")
fi

herdr pane run "$pane" "claude --resume $sid --fork-session"
echo "forked session $sid -> pane $pane"
