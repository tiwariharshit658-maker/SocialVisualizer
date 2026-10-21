"""Load and normalize social post data from local JSON and CSV files."""

import csv
import json
from pathlib import Path
from typing import Any


def normalize_post(raw: dict[str, Any], source: str = "local") -> dict[str, str]:
    """Convert a platform or export record to the package's stable post schema."""
    text = raw.get("text") or raw.get("full_text") or raw.get("content")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Each post must contain non-empty text, full_text, or content.")

    author = raw.get("author") or raw.get("handle") or ""
    if isinstance(author, dict):
        author = author.get("handle") or author.get("did") or ""

    created_at = raw.get("created_at") or raw.get("indexedAt") or raw.get("date") or ""
    uri = raw.get("uri") or raw.get("id") or ""
    return {
        "text": text.strip(),
        "created_at": str(created_at),
        "author": str(author),
        "uri": str(uri),
        "source": str(raw.get("source") or source),
    }


def load_posts(path: str | Path) -> list[dict[str, str]]:
    """Load posts from a JSON or CSV file, rejecting malformed input clearly."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    if file_path.suffix.lower() == ".json":
        with file_path.open(encoding="utf-8-sig") as file:
            payload = json.load(file)
        records = payload.get("posts") if isinstance(payload, dict) else payload
        if not isinstance(records, list):
            raise ValueError("JSON input must be an array of posts or an object with a 'posts' array.")
    elif file_path.suffix.lower() == ".csv":
        with file_path.open(encoding="utf-8-sig", newline="") as file:
            records = list(csv.DictReader(file))
        if not records:
            raise ValueError("CSV input is empty or has no data rows.")
    else:
        raise ValueError("Input must be a .json or .csv file.")

    posts = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"Post at index {index} must be a JSON object.")
        try:
            posts.append(normalize_post(record))
        except ValueError as error:
            raise ValueError(f"Invalid post at index {index}: {error}") from error
    return posts


def save_posts(posts: list[dict[str, str]], path: str | Path) -> None:
    """Write normalized posts as UTF-8 JSON."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as file:
        json.dump({"posts": posts}, file, ensure_ascii=False, indent=2)
        file.write("\n")
