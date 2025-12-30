# temperature.py
from typing import Tuple, Optional, Union
import io
import numpy as np
import matplotlib.pyplot as plt
import rasterio as rio

# Dataset constants (as before)
SCALE = 0.00341802
OFFSET = 149.0


def _rewind(obj):
    """Seek back to start for file-like UploadedFile objects."""
    try:
        obj.seek(0)
    except Exception:
        pass


def _is_path(obj) -> bool:
    return isinstance(obj, str)


def load_and_compute(src: Union[str, "file-like"]) -> np.ndarray:
    """
    Load the LWIR band and convert to °F. Accepts path or file-like object.
    Returns a 2D float ndarray (°F).
    """
    # If file-like, rewind before reading
    if not _is_path(src):
        _rewind(src)

    # Open with rasterio (works with both path and file-like)
    with rio.open(src) as f:
        # try band index 5, fallback to last band if file differs
        count = f.count
        band_index = 5 if count >= 5 else count
        raw = f.read(band_index)  # shape: (H, W)

        # nodata value if present
        nodata = f.meta.get("nodata", None)

    # Ensure raw is float for arithmetic
    raw = raw.astype(float)

    # Mask: treat nodata if available, else treat zeros as missing
    if nodata is not None:
        valid_mask = raw != nodata
    else:
        valid_mask = raw != 0

    valid_vals = raw[valid_mask]
    if valid_vals.size == 0:
        # If no valid pixels, raise an informative error
        raise RuntimeError("No valid LWIR pixels found to compute temperature.")

    median_val = float(np.median(valid_vals))

    # Fill missing with median and convert -> Kelvin -> Fahrenheit
    raw_filled = raw.copy()
    raw_filled[~valid_mask] = median_val

    kelvin = raw_filled * SCALE + OFFSET
    fahrenheit = (kelvin - 273.15) * 9.0 / 5.0 + 32.0
    return fahrenheit


def plot_from_array(fahrenheit: np.ndarray,
                    threshold_f: float = 120.0,
                    title: Optional[str] = None,
                    fig_size: Tuple[int, int] = (7, 5)
                    ) -> Tuple[plt.Figure, int, float]:
    """
    Create a matplotlib figure of the temperature array, overlay mask for > threshold,
    and return (figure, count_above, percent_above).
    """
    if not isinstance(fahrenheit, np.ndarray):
        raise TypeError("fahrenheit must be a numpy.ndarray")

    # compute counts
    mask_above = fahrenheit > threshold_f
    count = int(np.count_nonzero(mask_above))
    total = int(fahrenheit.size)
    pct = 100.0 * count / float(total) if total > 0 else 0.0

    # create figure (no plt.show())
    fig, ax = plt.subplots(figsize=fig_size)
    im = ax.imshow(fahrenheit, cmap="inferno", origin="upper", interpolation="nearest")
    ax.axis("off")
    if title:
        ax.set_title(title)

    # overlay semi-transparent mask (use masked array so non-thresholded pixels are transparent)
    ax.imshow(np.ma.masked_where(~mask_above, mask_above), cmap="Reds", alpha=0.35, origin="upper")

    cbar = fig.colorbar(im, ax=ax, fraction=0.036, pad=0.04)
    cbar.set_label("Temperature (°F)")

    fig.tight_layout()

    return fig, count, pct


def run(src: Union[str, "file-like"], threshold_f: float = 120.0) -> Tuple[plt.Figure, int, float]:
    """
    Streamlit-friendly entrypoint.
    Accepts either a path (str) or a Streamlit UploadedFile (file-like).
    Returns (figure, count_above_threshold, percent_above_threshold).
    """
    # Rewind if file-like
    if not _is_path(src):
        _rewind(src)

    # Compute temperatures
    fahrenheit = load_and_compute(src)

    # Use a reasonable figure size so Streamlit can scale it
    fig, count, pct = plot_from_array(fahrenheit, threshold_f=threshold_f, fig_size=(7, 5))
    return fig, count, pct


# CLI convenience (optional)
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python temperature.py <path-to-tif> [threshold_f]")
        raise SystemExit(1)
    path = sys.argv[1]
    thresh = float(sys.argv[2]) if len(sys.argv) >= 3 else 120.0
    fig, count, pct = run(path, threshold_f=thresh)
    print(f"Count above {thresh}: {count} ({pct:.2f}%)")
    fig.show()
