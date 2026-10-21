"""Command-line interface for SocialVisualizer."""

import argparse
import json
import sys
from pathlib import Path

from .analytics import summarize
from .data import load_posts, save_posts
from .sources import search_bluesky
from .upload import upload_image
from .visualizations import create_keyboard_heatmap, create_wordcloud


def _analyze(posts: list[dict[str, str]], output_dir: Path, upload: bool) -> None:
    if not posts:
        raise ValueError("No posts to analyze.")
    output_dir.mkdir(parents=True, exist_ok=True)
    posts_path = output_dir / "posts.json"
    report_path = output_dir / "report.json"
    wordcloud_path = output_dir / "wordcloud.png"
    keyboard_path = output_dir / "keyboard_heatmap.png"
    save_posts(posts, posts_path)

    report = summarize(posts)
    report["images"] = {
        "wordcloud": wordcloud_path.name,
        "keyboard_heatmap": keyboard_path.name,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    texts = [post["text"] for post in posts]
    create_wordcloud(texts, wordcloud_path)
    create_keyboard_heatmap("\n".join(texts), keyboard_path)

    print(f"Analyzed {len(posts)} posts.")
    print(f"Report: {report_path}")
    print(f"Word cloud: {wordcloud_path}")
    print(f"Keyboard heatmap: {keyboard_path}")
    if upload:
        print(f"Imgur word cloud: {upload_image(wordcloud_path)}")
        print(f"Imgur keyboard heatmap: {upload_image(keyboard_path)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="socialvisualizer",
        description="Analyze social posts and create word-cloud and keyboard heatmap images.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    analyze = commands.add_parser("analyze", help="Analyze a local JSON or CSV export.")
    analyze.add_argument("input", type=Path, help="Path to a JSON or CSV post export.")
    analyze.add_argument("--output-dir", type=Path, default=Path("output"))
    analyze.add_argument("--upload", action="store_true", help="Upload generated images to Imgur.")

    collect = commands.add_parser("collect", help="Search public Bluesky posts, then analyze them.")
    collect.add_argument("--query", required=True)
    collect.add_argument("--limit", type=int, default=100)
    collect.add_argument("--output-dir", type=Path, default=Path("output"))
    collect.add_argument("--upload", action="store_true", help="Upload generated images to Imgur.")

    keyboard = commands.add_parser("keyboard", help="Create a keyboard heatmap from a UTF-8 text file.")
    keyboard.add_argument("input", type=Path)
    keyboard.add_argument("--output", type=Path, default=Path("keyboard_heatmap.png"))
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "analyze":
            _analyze(load_posts(args.input), args.output_dir, args.upload)
        elif args.command == "collect":
            posts = search_bluesky(args.query, args.limit)
            _analyze(posts, args.output_dir, args.upload)
        else:
            text = args.input.read_text(encoding="utf-8-sig")
            create_keyboard_heatmap(text, args.output)
            print(f"Keyboard heatmap: {args.output}")
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0
