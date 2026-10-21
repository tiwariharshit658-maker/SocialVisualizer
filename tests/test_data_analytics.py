import json

import pytest

from socialvisualizer.analytics import keyboard_frequencies, summarize, word_frequencies
from socialvisualizer.data import load_posts, normalize_post, save_posts


def test_normalize_post_supports_common_export_fields():
    post = normalize_post(
        {
            "full_text": "  Hello, world! ",
            "created_at": "2025-01-01T12:00:00Z",
            "author": {"handle": "harshit.example"},
            "id": "post-1",
        }
    )

    assert post == {
        "text": "Hello, world!",
        "created_at": "2025-01-01T12:00:00Z",
        "author": "harshit.example",
        "uri": "post-1",
        "source": "local",
    }


def test_load_json_and_save_round_trip(tmp_path):
    source = tmp_path / "posts.json"
    source.write_text(json.dumps({"posts": [{"text": "Fresh local produce"}]}), encoding="utf-8")

    posts = load_posts(source)
    destination = tmp_path / "nested" / "normalized.json"
    save_posts(posts, destination)

    assert load_posts(destination) == posts


def test_load_csv_and_reject_invalid_posts(tmp_path):
    source = tmp_path / "posts.csv"
    source.write_text("text,author\nA useful post,reader\n", encoding="utf-8")
    assert load_posts(source)[0]["author"] == "reader"

    invalid = tmp_path / "invalid.json"
    invalid.write_text('[{"author":"reader"}]', encoding="utf-8")
    with pytest.raises(ValueError, match="index 0"):
        load_posts(invalid)


def test_analytics_count_terms_activity_and_authors():
    posts = [
        {"text": "Gardens bring fresh food", "created_at": "2025-01-01T12:00:00Z", "author": "a"},
        {"text": "Fresh food for all", "created_at": "2025-01-02T01:00:00+12:00", "author": "b"},
        {"text": "No date here", "created_at": "", "author": "a"},
    ]

    report = summarize(posts)

    assert report["post_count"] == 3
    assert report["author_count"] == 2
    assert report["activity_by_day"] == {"2025-01-01": 2}
    assert report["top_words"][0] == {"word": "fresh", "count": 2}


def test_text_and_keyboard_frequencies():
    assert word_frequencies(["A garden, a GARDEN!"]) == {"garden": 2}
    assert keyboard_frequencies("Aa Z! 1") == {"a": 2, "z": 1}


def test_load_posts_rejects_unsupported_and_missing_files(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_posts(tmp_path / "missing.json")
    unsupported = tmp_path / "posts.txt"
    unsupported.write_text("not a supported export", encoding="utf-8")
    with pytest.raises(ValueError, match="json or .csv"):
        load_posts(unsupported)
