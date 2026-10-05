#!/usr/bin/env python3
"""Yahoo!リアルタイム検索で X (Twitter) の投稿を検索する。

標準ライブラリのみ。検索結果ページの __NEXT_DATA__ から 1 ページ目 (最大 40 件) を、
新着順の続きはページ送り API (10 件ずつ) から取得する。
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

BASE = "https://search.yahoo.co.jp/realtime"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
JST = timezone(timedelta(hours=9))
MAX_LIMIT = 200
PAGE_WAIT_SEC = 1.0


def fetch(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ja"})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return res.read().decode("utf-8")


def first_page(query, sort, timeout):
    params = {"p": query, "ei": "UTF-8", "md": "h" if sort == "popular" else "t"}
    html = fetch(f"{BASE}/search?{urllib.parse.urlencode(params)}", timeout)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise RuntimeError("__NEXT_DATA__ が見つからない (Yahoo!側のページ構造が変わった可能性)")
    page = json.loads(m.group(1))["props"]["pageProps"]["pageData"]
    err = (page.get("searchError") or {}).get("errorType")
    if err == "zeromatch":  # ヒットなしは正常な結果として扱う
        return [], 0
    if err:
        raise RuntimeError(f"検索エラー: {err}")
    timeline = page.get("timeline") or {}
    total = (timeline.get("head") or {}).get("totalResultsAvailable")
    return timeline.get("entry") or [], total


def next_page(query, oldest_id, offset, timeout):
    params = {"p": query, "rkf": 3, "b": offset, "oldestTweetId": oldest_id}
    body = fetch(f"{BASE}/api/v1/pagination?{urllib.parse.urlencode(params)}", timeout)
    return (json.loads(body).get("timeline") or {}).get("entry") or []


def clean_text(text):
    # 検索語のハイライト記号 (\tSTART\t / \tEND\t) を除去
    return re.sub(r"\t(START|END)\t", "", text or "")


def clean_url(url):
    parts = urllib.parse.urlsplit(url or "")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def to_post(e):
    created = datetime.fromtimestamp(e["createdAt"], tz=JST) if e.get("createdAt") else None
    return {
        "id": e.get("id"),
        "url": clean_url(e.get("url")),
        "created_at_jst": created.strftime("%Y-%m-%d %H:%M") if created else None,
        "name": e.get("name"),
        "screen_name": e.get("screenName"),
        "text": clean_text(e.get("displayText")),
        "likes": e.get("likesCount", 0),
        "reposts": e.get("rtCount", 0),
        "replies": e.get("replyCount", 0),
        "quotes": e.get("qtCount", 0),
        "is_reply": bool(e.get("inReplyTo")),
        "has_media": bool(e.get("media")),
    }


def search(query, sort, limit, timeout):
    entries, total = first_page(query, sort, timeout)
    posts, seen = [], set()

    def add(batch):
        for e in batch:
            if e.get("id") not in seen and len(posts) < limit:
                seen.add(e.get("id"))
                posts.append(to_post(e))

    add(entries)
    # 話題順は Yahoo!側がページ送りに対応しないので 1 ページ目で終える
    while sort == "time" and len(posts) < limit and entries:
        time.sleep(PAGE_WAIT_SEC)
        entries = next_page(query, posts[-1]["id"], len(posts) + 1, timeout)
        before = len(posts)
        add(entries)
        if len(posts) == before:
            break
    return posts, total


def render_markdown(query, sort, posts, total):
    label = "話題順" if sort == "popular" else "新着順"
    lines = [f"# Yahoo!リアルタイム検索: {query} ({label})", "",
             f"ヒット総数: {total if total is not None else '不明'} 件 / 取得: {len(posts)} 件 (日時は JST)", ""]
    for p in posts:
        flags = " [返信]" if p["is_reply"] else ""
        flags += " [メディアあり]" if p["has_media"] else ""
        lines += [
            f"## {p['created_at_jst']} {p['name']} (@{p['screen_name']}){flags}",
            f"いいね {p['likes']} / リポスト {p['reposts']} / 返信 {p['replies']} / 引用 {p['quotes']}",
            "",
            p["text"],
            "",
            p["url"],
            "",
        ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Yahoo!リアルタイム検索で X の投稿を検索する")
    ap.add_argument("query", help="検索語")
    ap.add_argument("--sort", choices=["time", "popular"], default="time", help="time=新着順 (既定) / popular=話題順 (最大 40 件)")
    ap.add_argument("--limit", type=int, default=40, help=f"取得件数 (既定 40、上限 {MAX_LIMIT})")
    ap.add_argument("--json", action="store_true", help="JSON 配列で出力する")
    ap.add_argument("--timeout", type=float, default=20, help="1 リクエストのタイムアウト秒 (既定 20)")
    args = ap.parse_args()

    limit = max(1, min(args.limit, MAX_LIMIT))
    try:
        posts, total = search(args.query, args.sort, limit, args.timeout)
    except Exception as e:  # 取得失敗は理由を出して非ゼロ終了する
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps({"query": args.query, "sort": args.sort, "total": total, "posts": posts}, ensure_ascii=False, indent=1))
    else:
        print(render_markdown(args.query, args.sort, posts, total))


if __name__ == "__main__":
    main()
