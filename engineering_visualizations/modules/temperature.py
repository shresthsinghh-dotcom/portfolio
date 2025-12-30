#!/usr/bin/env python3
"""
temperature.py

Utilities to load, compute, and plot surface temperature (°F) from the lwir11 band
of a GeoTIFF. `load_and_compute` can be imported and used without producing plots,
while `plot_from_array` handles visualization.

Usage (imported):
    from temperature import load_and_compute, plot_from_array
    fahrenheit = load_and_compute("durham_summer24.tif")
    plot_from_array(fahrenheit, threshold_f=95.0)

Standalone:
    python temperature.py
"""
from typing import Tuple, Optional

import rasterio as rio
import numpy as np
import matplotlib.pyplot as plt

# Constants from dataset metadata (sensor / dataset provided values).
# SCALE/OFFSET convert raw LWIR counts -> Kelvin according to dataset documentation.
SCALE = 0.00341802
OFFSET = 149.0


def load_and_compute(path: str) -> np.ndarray:
    """
    Load the LWIR band from `path`, fill missing values, convert raw counts -> °F.

    Simple explanation:
      - Reads band 5 (lwir11) from the GeoTIFF.
      - Replaces missing pixels (nodata or zeros) with the median of valid pixels.
      - Applies dataset scale/offset to convert to Kelvin, then converts Kelvin -> °F.

    Parameters
    ----------
    path : str
        Path to the GeoTIFF containing the lwir11 band (assumed at band index 5).

    Returns
    -------
    np.ndarray
        2D array (float) with surface temperatures in degrees Fahrenheit.

    Raises
    ------
    RuntimeError
        If no valid pixels are found to compute a median.
    rasterio.errors.RasterioIOError
        If the file cannot be opened.
    """
    # Read the raw band and nodata metadata. We keep raw as whatever dtype it comes as.
    with rio.open(path) as src:
        raw = src.read(5)                 # expected LWIR band (2D array)
        nodata = src.meta.get("nodata")   # may be None or a numeric value

    # Build a mask of valid pixels. If nodata is present, treat that as invalid.
    # Otherwise (common in these datasets), treat zero as missing.
    if nodata is not None:
        valid_mask = raw != nodata
    else:
        valid_mask = raw != 0

    # Convert valid values to float and compute median; need at least one valid pixel.
    valid_vals = raw[valid_mask].astype(float)
    if valid_vals.size == 0:
        raise RuntimeError("No valid pixels found in the lwir11 band to compute median.")
    median_val = float(np.median(valid_vals))

    # Fill missing pixels with the median, convert to float for arithmetic.
    raw_filled = raw.astype(float)
    raw_filled[~valid_mask] = median_val

    # Convert raw counts -> Kelvin using SCALE/OFFSET, then Kelvin -> Fahrenheit.
    # Combined into one expression for clarity:
    fahrenheit = (raw_filled * SCALE + OFFSET - 273.15) * 9.0 / 5.0 + 32.0

    return fahrenheit


def plot_from_array(fahrenheit: np.ndarray, threshold_f: float = 120.0, title: Optional[str] = None) -> Tuple[int, float]:
    """
    Plot a 2D Fahrenheit temperature array and overlay pixels above `threshold_f`.

    Simple explanation:
      - Shows the temperature map with an inferno colormap.
      - Overlays a semi-transparent red mask where temperature > threshold.
      - Prints and returns the count and percentage of pixels above threshold.

    Parameters
    ----------
    fahrenheit : np.ndarray
        2D array of temperatures in °F (float).
    threshold_f : float, optional
        Threshold in °F for overlay and statistics (default 120.0).
    title : str or None, optional
        Optional title to place on the figure. If None, no title is added.

    Returns
    -------
    Tuple[int, float]
        (count_above_threshold, percent_above_threshold)
    """
    # Basic statistics
    count = int(np.count_nonzero(fahrenheit > threshold_f))
    pct = 100.0 * count / float(fahrenheit.size) if fahrenheit.size > 0 else 0.0
    print(f"Pixels > {threshold_f:.1f}°F : {count}  ({pct:.2f}%)")

    # Plot the temperature array
    fig, ax = plt.subplots(figsize=(9, 7))
    im = ax.imshow(fahrenheit, cmap="inferno", origin="upper", interpolation="nearest")

    # Overlay: semi-transparent red mask where temperature exceeds threshold
    mask = (fahrenheit > threshold_f).astype(float)
    ax.imshow(mask, cmap="Reds", origin="upper", interpolation="nearest", alpha=0.35, vmin=0, vmax=1)

    # Colorbar labeling
    cbar = fig.colorbar(im, ax=ax, fraction=0.036, pad=0.04)
    cbar.set_label("Temperature (°F)")

    # Optional title (omit by default to allow report captions instead)
    if title:
        ax.set_title(title)

    ax.axis("off")
    plt.tight_layout()
    plt.show()

    return count, pct


def main(path: str) -> None:
    """
    Minimal CLI entry point: compute and plot temperatures for the provided file.

    Parameters
    ----------
    path : str
        Path to the GeoTIFF file to analyze.

    Returns
    -------
    None
    """
    fahrenheit = load_and_compute(path)
    # Use a default threshold for the demo; callers can use plot_from_array directly.
    plot_from_array(fahrenheit, threshold_f=120.0, title=None)


if __name__ == "__main__":
    # Example runs for the two region files used in the project
    main("land_cover_québec.tif")
    main("land_cover_alberta.tif")
