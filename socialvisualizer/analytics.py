"""Text and activity summaries for normalized social posts."""

import re
from collections import Counter
from datetime import datetime, timezone
from typing import Iterable

DEFAULT_STOPWORDS = frozenset(
    "a an and are as at be been but by can for from had has have he her hers him his "
    "i in is it its me my of on or our ours she that the their them they this to was "
    "we were with you your".split()
)
WORD_PATTERN = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", re.UNICODE)
KEY_PATTERN = re.compile(r"[a-z]", re.IGNORECASE)


def word_frequencies(
    texts: Iterable[str], stopwords: frozenset[str] = DEFAULT_STOPWORDS
) -> Counter[str]:
    """Count case-insensitive words while filtering common English stopwords."""
    counts: Counter[str] = Counter()
    for text in texts:
        counts.update(
            word.lower().replace("’", "'")
            for word in WORD_PATTERN.findall(text)
            if word.lower().replace("’", "'") not in stopwords
        )
    return counts


def keyboard_frequencies(text: str) -> Counter[str]:
    """Count case-insensitive A-Z characters for the keyboard heatmap."""
    return Counter(character.lower() for character in KEY_PATTERN.findall(text))


def summarize(posts: list[dict[str, str]], top_words: int = 20) -> dict:
    """Return aggregate counts and activity by UTC calendar date."""
    authors = {post["author"] for post in posts if post.get("author")}
    days: Counter[str] = Counter()
    for post in posts:
        value = post.get("created_at", "")
        if not value:
            continue
        try:
            created_at = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            continue
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        created_at = created_at.astimezone(timezone.utc)
        days[created_at.date().isoformat()] += 1

    terms = word_frequencies(post.get("text", "") for post in posts)
    return {
        "post_count": len(posts),
        "author_count": len(authors),
        "activity_by_day": dict(sorted(days.items())),
        "top_words": [
            {"word": word, "count": count}
            for word, count in terms.most_common(max(0, top_words))
        ],
    }
