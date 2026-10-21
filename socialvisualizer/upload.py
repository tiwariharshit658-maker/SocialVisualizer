"""Optional Imgur anonymous image uploads."""

import base64
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

IMGUR_UPLOAD_URL = "https://api.imgur.com/3/image"


def upload_image(path: str | Path, client_id: str | None = None) -> str:
    """Upload one image to Imgur and return its public link."""
    image_path = Path(path)
    if not image_path.is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")
    client_id = client_id or os.environ.get("IMGUR_CLIENT_ID")
    if not client_id:
        raise ValueError("Set IMGUR_CLIENT_ID before using --upload.")

    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    body = urlencode({"image": encoded, "type": "base64"}).encode("ascii")
    request = Request(
        IMGUR_UPLOAD_URL,
        data=body,
        headers={
            "Authorization": f"Client-ID {client_id}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Imgur upload failed (HTTP {error.code}): {detail}") from error
    except URLError as error:
        raise RuntimeError(f"Could not connect to Imgur: {error.reason}") from error

    link = payload.get("data", {}).get("link")
    if not payload.get("success") or not link:
        raise RuntimeError("Imgur did not return a successful image link.")
    return link
