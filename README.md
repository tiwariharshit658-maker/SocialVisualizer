# SocialVisualizer

SocialVisualizer is a small Python toolkit for collecting public social posts, exploring imported post data, and turning text into shareable visualizations. It supports local JSON/CSV files, public Bluesky search, word clouds, keyboard heatmaps, and optional Imgur uploads.

## Features

- Analyze your own exported or otherwise authorized post data without an account or API credentials.
- Search public Bluesky posts using its public AppView API.
- Summarize post counts, authors, activity by day, and frequently used words.
- Export a word cloud and a QWERTY keyboard character heatmap as PNG images.
- Optionally upload generated images to Imgur using an API client ID supplied through the environment.

## Requirements and setup

Python 3.10 or newer is required.

```sh
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Analyze local data

Input JSON can be an array of posts or an object with a `posts` array. CSV files should have a `text` column; `created_at` and `author` are optional. The loader also recognizes `full_text` and `content`.

```sh
socialvisualizer analyze examples/sample_posts.json --output-dir output
socialvisualizer analyze posts.csv --output-dir output
```

The command writes `posts.json`, `report.json`, `wordcloud.png`, and `keyboard_heatmap.png` to the output directory. The report includes totals, distinct authors, daily activity, and the most common non-stopword terms.

## Search Bluesky

Search is limited to public posts and uses the unauthenticated Bluesky AppView endpoint. The service can change or limit public access; local analysis remains available independently.

```sh
socialvisualizer collect --query "urban gardens" --limit 100 --output-dir output
```

`--limit` accepts 1–1000 posts. Results are fetched in pages of at most 100. Follow Bluesky's terms and rate limits, and use this only for data you are allowed to process.

## Keyboard heatmap

The standalone utility accepts UTF-8 text and colors each letter key by its frequency:

```sh
socialvisualizer keyboard notes.txt --output keyboard_heatmap.png
```

## Optional Imgur upload

Create an Imgur API application and set its client ID in your shell. Never place credentials in source files or commit them.

```powershell
$env:IMGUR_CLIENT_ID = "your-client-id"
socialvisualizer analyze posts.csv --output-dir output --upload
```

On macOS/Linux:

```sh
export IMGUR_CLIENT_ID="your-client-id"
socialvisualizer analyze posts.csv --output-dir output --upload
```

`--upload` uploads both generated PNGs through Imgur's anonymous image-upload API and prints their links. Images and post data are sent to Imgur only when this option is explicitly requested. Uploads are subject to Imgur's terms and retention policies.

## Data format

The normalized post schema is:

```json
{
  "text": "A public post",
  "created_at": "2025-01-01T12:00:00Z",
  "author": "did:plc:example",
  "uri": "at://...",
  "source": "bluesky"
}
```

The example dataset is synthetic and included only to make the local workflow easy to try.

## Development

```sh
python -m pytest
```

The core import, normalization, and analytics features use only the Python standard library. Plotting dependencies are installed with the package.
