#!/usr/bin/env bash
#
# herdr-fork-popup
#
# Fork the current Claude Code session into a Herdr session-modal popup
# (80% x 80%). The fork inherits the full conversation history under a NEW
# session ID; the original session is left unchanged.
#
# Requirements: plugin trapple.herdr-fork-popup linked
# (herdr plugin link <skill>/plugin). Session ID resolution is the same
# as herdr-fork: CLAUDE_CODE_SESSION_ID, else the focused Herdr Claude agent.
#
# Session-ID resolution derived from herdr-fork.sh by Tatsuhiko Miyagawa (@miyagawa):
#   https://gist.github.com/miyagawa/cb1a9f6c8695d1219efba0c66d5f78f7
set -euo pipefail

# herdr キーバインド (type="shell") は最小 PATH で走るため、herdr / claude / python3 を解決できるよう補強
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

# herdr キーバインドの shell には HERDR_ENV が渡らないため、サーバー到達性でガードする
if ! herdr status server >/dev/null 2>&1; then
    echo "herdr-fork-popup: no reachable Herdr server" >&2
    exit 1
fi

sid="${CLAUDE_CODE_SESSION_ID:-}"
if [ -z "$sid" ]; then
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
        echo "herdr-fork-popup: CLAUDE_CODE_SESSION_ID is not set and could not resolve the focused Claude session" >&2
        exit 1
    fi
fi

herdr plugin pane open \
    --plugin trapple.herdr-fork-popup \
    --entrypoint fork \
    --env CLAUDE_FORK_SID="$sid" \
    --env CLAUDE_FORK_CWD="$PWD"

echo "forked session $sid -> popup (80% x 80%)"
