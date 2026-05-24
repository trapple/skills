"""Hermes Agent の x_search_tool を呼び出す薄いラッパー。

既定では answer (Markdown) のみを stdout に出力する。
--raw 指定で JSON 全体を出力する。
"""

import json
import sys

from tools.x_search_tool import x_search_tool


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in {"-h", "--help"}:
        print(
            "Usage: run_x_search.py <query> [--raw]\n"
            "  <query>  検索クエリ (自然文)\n"
            "  --raw    JSON 全体を出力 (既定は answer のみ)",
            file=sys.stderr,
        )
        return 2

    query = args[0]
    raw = "--raw" in args[1:]

    result = x_search_tool(query)

    if raw:
        print(result)
        return 0

    data = json.loads(result)
    if not data.get("success", True):
        print(result, file=sys.stderr)
        return 1
    print(data.get("answer", result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
