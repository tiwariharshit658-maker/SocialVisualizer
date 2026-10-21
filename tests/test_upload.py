import base64
import json
from urllib.parse import parse_qs
from unittest.mock import patch

import pytest

from socialvisualizer.upload import upload_image


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps({"success": True, "data": {"link": "https://i.imgur.com/example.png"}}).encode()


def test_imgur_upload_encodes_form_data_and_returns_link(tmp_path):
    image = tmp_path / "image.png"
    image.write_bytes(b"\x00\x01image")

    with patch("socialvisualizer.upload.urlopen", return_value=FakeResponse()) as urlopen:
        link = upload_image(image, client_id="test-client")

    request = urlopen.call_args.args[0]
    form = parse_qs(request.data.decode("ascii"))
    assert form["image"] == [base64.b64encode(image.read_bytes()).decode("ascii")]
    assert request.get_header("Authorization") == "Client-ID test-client"
    assert link == "https://i.imgur.com/example.png"


def test_imgur_upload_requires_a_client_id(tmp_path, monkeypatch):
    image = tmp_path / "image.png"
    image.write_bytes(b"image")
    monkeypatch.delenv("IMGUR_CLIENT_ID", raising=False)

    with pytest.raises(ValueError, match="IMGUR_CLIENT_ID"):
        upload_image(image)
