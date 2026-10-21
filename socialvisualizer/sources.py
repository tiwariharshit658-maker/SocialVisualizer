"""Integrations for public social-post sources."""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .data import normalize_post

BLUESKY_SEARCH_URL = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"


def search_bluesky(query: str, limit: int = 100) -> list[dict[str, str]]:
    """Fetch up to ``limit`` public posts from the Bluesky AppView search API."""
    if not query.strip():
        raise ValueError("Search query cannot be empty.")
    if not 1 <= limit <= 1000:
        raise ValueError("Limit must be between 1 and 1000.")

    posts: list[dict[str, str]] = []
    cursor = None
    while len(posts) < limit:
        page_size = min(100, limit - len(posts))
        params = {"q": query, "limit": page_size}
        if cursor:
            params["cursor"] = cursor
        request = Request(
            f"{BLUESKY_SEARCH_URL}?{urlencode(params)}",
            headers={"Accept": "application/json", "User-Agent": "SocialVisualizer/1.0"},
        )
        try:
            with urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Bluesky search failed (HTTP {error.code}): {detail}") from error
        except URLError as error:
            raise RuntimeError(f"Could not connect to Bluesky: {error.reason}") from error

        feed = payload.get("posts", [])
        if not isinstance(feed, list):
            raise RuntimeError("Bluesky returned an unexpected response format.")
        for item in feed:
            post = item.get("post", item)
            record = post.get("record", {})
            author = post.get("author", {})
            post_text = record.get("text")
            if not post_text:
                continue
            posts.append(
                normalize_post(
                    {
                        "text": post_text,
                        "created_at": record.get("createdAt") or post.get("indexedAt"),
                        "author": author.get("handle") or author.get("did"),
                        "uri": post.get("uri"),
                    },
                    source="bluesky",
                )
            )
            if len(posts) >= limit:
                break

        cursor = payload.get("cursor")
        if not feed or not cursor:
            break
    return posts
