"""
temperature.py (Streamlit-ready)

Utilities to load, compute, and visualize surface temperature (°F) from the lwir11
band of a GeoTIFF. Designed for use in a Streamlit app.

Core design:
- All computation is separated from UI.
- No hardcoded file paths.
- No plt.show().
- One public entry point: run().
"""

from typing import Optional, Tuple

import rasterio as rio
import numpy as np
import matplotlib.pyplot as plt

# Dataset-specific constants (from metadata)
SCALE = 0.00341802
OFFSET = 149.0

def rewind(file_like):
    try:
        file_like.seek(0)
    except Exception:
        pass


def load_and_compute(uploaded_tiff) -> np.ndarray:
    """
    Load the LWIR band from an uploaded GeoTIFF and compute surface temperature (°F).

    Steps:
      - Reads band 5 (lwir11).
      - Replaces missing pixels (nodata or zeros) with median of valid pixels.
      - Converts raw counts -> Kelvin -> Fahrenheit.

    Parameters
    ----------
    uploaded_tiff : Streamlit UploadedFile
        Uploaded GeoTIFF containing the lwir11 band.

    Returns
    -------
    np.ndarray
        2D array of surface temperatures in degrees Fahrenheit.
    """

    # Open directly from file-like object
    rewind(uploaded_tiff)
    with rio.open(uploaded_tiff) as src:
        raw = src.read(5)
    nodata = src.meta.get("nodata")

    # Determine valid pixels
    if nodata is not None:
        valid_mask = raw != nodata
    else:
        valid_mask = raw != 0

    valid_vals = raw[valid_mask].astype(float)
    if valid_vals.size == 0:
        raise RuntimeError(
            "No valid pixels found in the lwir11 band to compute temperature."
        )

    median_val = float(np.median(valid_vals))

    # Fill missing pixels
    raw_filled = raw.astype(float)
    raw_filled[~valid_mask] = median_val

    # Raw counts -> Kelvin -> Fahrenheit
    fahrenheit = (raw_filled * SCALE + OFFSET - 273.15) * 9.0 / 5.0 + 32.0

    return fahrenheit


def plot_temperature(
    fahrenheit: np.ndarray,
    threshold_f: float = 120.0,
    title: Optional[str] = None,
) -> Tuple[plt.Figure, int, float]:
    """
    Create a temperature visualization with an overlay above a threshold.

    Parameters
    ----------
    fahrenheit : np.ndarray
        2D temperature array (°F).
    threshold_f : float
        Threshold in °F for overlay and statistics.
    title : str or None
        Optional figure title.

    Returns
    -------
    Tuple[Figure, int, float]
        (matplotlib Figure, count_above_threshold, percent_above_threshold)
    """

    count = int(np.count_nonzero(fahrenheit > threshold_f))
    pct = 100.0 * count / float(fahrenheit.size) if fahrenheit.size > 0 else 0.0

    fig, ax = plt.subplots(figsize=(9, 7))

    im = ax.imshow(
        fahrenheit,
        cmap="inferno",
        origin="upper",
        interpolation="nearest"
    )

    # Overlay mask for high-temperature regions
    mask = (fahrenheit > threshold_f).astype(float)
    ax.imshow(
        mask,
        cmap="Reds",
        origin="upper",
        interpolation="nearest",
        alpha=0.35,
        vmin=0,
        vmax=1
    )

    cbar = fig.colorbar(im, ax=ax, fraction=0.036, pad=0.04)
    cbar.set_label("Temperature (°F)")

    if title:
        ax.set_title(title)

    ax.axis("off")
    fig.tight_layout()

    return fig, count, pct


def run(uploaded_tiff, threshold_f: float = 120.0):
    """
    Streamlit-facing entry point.

    Parameters
    ----------
    uploaded_tiff : Streamlit UploadedFile
        Uploaded GeoTIFF file.
    threshold_f : float
        Temperature threshold (°F).

    Returns
    -------
    Tuple[Figure, int, float]
        Figure and statistics for Streamlit rendering.
    """

    fahrenheit = load_and_compute(uploaded_tiff)

    fig, count, pct = plot_temperature(
        fahrenheit,
        threshold_f=threshold_f,
        title=None
    )

    return fig, count, pct
