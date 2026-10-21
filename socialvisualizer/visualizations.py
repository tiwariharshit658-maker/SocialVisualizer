"""PNG visualizations for post text and keyboard character frequencies."""

from pathlib import Path
from typing import Mapping

from .analytics import keyboard_frequencies, word_frequencies

KEY_ROWS = ("qwertyuiop", "asdfghjkl", "zxcvbnm")


def create_wordcloud(texts: list[str], output_path: str | Path) -> Path:
    """Create a word-cloud image from post text."""
    try:
        from wordcloud import WordCloud
    except ImportError as error:
        raise RuntimeError("Install SocialVisualizer's plotting dependencies to create images.") from error

    counts = word_frequencies(texts)
    if not counts:
        raise ValueError("No words remain to visualize after filtering.")
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    WordCloud(width=1400, height=800, background_color="white").generate_from_frequencies(
        counts
    ).to_file(str(destination))
    return destination


def create_keyboard_heatmap(text: str, output_path: str | Path) -> Path:
    """Draw a compact QWERTY heatmap, with warmer colors for frequent letters."""
    return draw_keyboard_heatmap(keyboard_frequencies(text), output_path)


def draw_keyboard_heatmap(
    frequencies: Mapping[str, int], output_path: str | Path
) -> Path:
    """Render a heatmap from precomputed lowercase A-Z frequencies."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.colors import Normalize
        from matplotlib.patches import FancyBboxPatch
    except ImportError as error:
        raise RuntimeError("Install SocialVisualizer's plotting dependencies to create images.") from error

    max_count = max(frequencies.values(), default=0)
    if max_count == 0:
        raise ValueError("Text must contain at least one letter from A to Z.")

    figure, axis = plt.subplots(figsize=(12, 4.8))
    axis.set_xlim(-0.5, 10)
    axis.set_ylim(-0.5, 3.3)
    axis.axis("off")
    color_map = plt.get_cmap("YlOrRd")
    normalize = Normalize(vmin=0, vmax=max_count)
    row_offsets = (0, 0.35, 0.75)
    for row_index, row in enumerate(KEY_ROWS):
        for column, key in enumerate(row):
            x = column + row_offsets[row_index]
            count = frequencies.get(key, 0)
            box = FancyBboxPatch(
                (x, 2 - row_index),
                0.82,
                0.75,
                boxstyle="round,pad=0.06,rounding_size=0.1",
                linewidth=0.8,
                edgecolor="#52525b",
                facecolor=color_map(normalize(count)),
            )
            axis.add_patch(box)
            axis.text(x + 0.41, 2.49 - row_index, key.upper(), ha="center", va="center", fontsize=12)
            axis.text(x + 0.41, 2.18 - row_index, str(count), ha="center", va="center", fontsize=8)
    axis.set_title("Keyboard Character Frequency", fontsize=16, pad=12)
    figure.tight_layout()
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return destination
