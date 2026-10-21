import json
from unittest.mock import patch

import pytest

from socialvisualizer.sources import search_bluesky


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_bluesky_search_normalizes_posts():
    payload = {
        "posts": [
            {
                "post": {
                    "record": {"text": "Public post", "createdAt": "2025-01-01T00:00:00Z"},
                    "author": {"handle": "poster.bsky.social"},
                    "uri": "at://post/1",
                }
            }
        ]
    }
    with patch("socialvisualizer.sources.urlopen", return_value=FakeResponse(payload)):
        posts = search_bluesky("gardens", 1)

    assert posts[0]["text"] == "Public post"
    assert posts[0]["author"] == "poster.bsky.social"
    assert posts[0]["source"] == "bluesky"


@pytest.mark.parametrize("query,limit", [("", 1), ("garden", 0), ("garden", 1001)])
def test_bluesky_search_validates_arguments(query, limit):
    with pytest.raises(ValueError):
        search_bluesky(query, limit)
