"""
integrated_analysis.py

Streamlit-ready integrated analysis that:
 - Builds an RGB preview for a GeoTIFF
 - Computes NDVI and surface temperature (using your temperature module)
 - Aggregates NDVI & temperature into region means
 - Computes covariance between NDVI and temperature region means
 - Returns figures and numeric results (no plt.show())

Public API:
    run(uploaded_tif, n_regions=10, show_preview=True)

Author: adapted for Streamlit by assistant
"""

from typing import Dict, Any, Tuple
import numpy as np
import rasterio as rio
import matplotlib.pyplot as plt

# Absolute imports from your package (adjusted to your layout)
from engineering_visualizations.modules.vegetation import compute_ndvi
from engineering_visualizations.modules.temperature import load_and_compute


def flatten(array2d: np.ndarray) -> np.ndarray:
    """Flatten a 2D array to 1D (preserves NaNs)."""
    return np.asarray(array2d).ravel()


def covariance1(x: np.ndarray, y: np.ndarray) -> float:
    """
    Compute sample covariance between two 1D arrays.
    Expects arrays of equal length and that caller handles NaNs.
    Returns np.nan if insufficient data.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    if x.size < 2 or y.size < 2:
        return float("nan")
    # unbiased sample covariance
    return float(np.cov(x, y, ddof=1)[0, 1])


def stretch_to_uint8(band: np.ndarray) -> np.ndarray:
    """Percentile stretch (2nd-98th) and scale to uint8 for preview."""
    band = np.asarray(band, dtype=float)
    valid = band[~np.isnan(band)] if np.any(~np.isnan(band)) else band
    lo = float(np.percentile(valid, 2)) if valid.size else 0.0
    hi = float(np.percentile(valid, 98)) if valid.size else 1.0
    clipped = np.clip(band, lo, hi)
    if hi == lo:
        scaled = np.zeros_like(clipped, dtype=float)
    else:
        scaled = (clipped - lo) / (hi - lo)
    return (np.nan_to_num(scaled) * 255).astype(np.uint8)


def _rgb_preview_from_tif(tif_path) -> np.ndarray:
    """
    Read expected bands (NIR, Red, Green, Blue) and produce uint8 HxWx3 preview.
    tif_path may be a path or a file-like object (Streamlit UploadedFile).
    """
    with rio.open(tif_path) as tif_data:
        nir08 = tif_data.read(1).astype(float)
        red = tif_data.read(2).astype(float)
        green = tif_data.read(3).astype(float)
        blue = tif_data.read(4).astype(float)

    r = stretch_to_uint8(red)
    g = stretch_to_uint8(green)
    b = stretch_to_uint8(blue)
    rgb_image = np.dstack((r, g, b))
    return rgb_image, nir08, red, green, blue


def average_by_region(array2d: np.ndarray, x_length: int) -> np.ndarray:
    """
    Divide 2D array into x_length x x_length regions and compute region means.
    Last row/col include remainder pixels.
    """
    arr = np.asarray(array2d)
    if arr.ndim != 2:
        raise ValueError("average_by_region expects a 2D array")

    rows, cols = arr.shape
    region_height = rows // x_length
    region_width = cols // x_length

    region_avgs = np.full((x_length, x_length), np.nan, dtype=float)

    for i in range(x_length):
        Srow = i * region_height
        Erow = rows if i == x_length - 1 else (i + 1) * region_height
        for j in range(x_length):
            Scol = j * region_width
            Ecol = cols if j == x_length - 1 else (j + 1) * region_width
            part = arr[Srow:Erow, Scol:Ecol]
            if part.size:
                region_avgs[i, j] = np.nanmean(part)
            else:
                region_avgs[i, j] = np.nan

    return region_avgs


def plot_rgb_preview(rgb_image: np.ndarray) -> plt.Figure:
    """Return a matplotlib figure showing the RGB preview (uint8 HxWx3)."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(rgb_image)
    ax.axis("off")
    fig.tight_layout()
    return fig


def plot_scatter(ndvi_flat: np.ndarray, temp_flat: np.ndarray) -> plt.Figure:
    """Return a matplotlib scatter figure of NDVI vs Temperature (NaNs allowed)."""
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(ndvi_flat, temp_flat, s=20, alpha=0.8)
    ax.set_xlabel("NDVI")
    ax.set_ylabel("Temperature (°F)")
    fig.tight_layout()
    return fig


def run(tif_file, n_regions: int = 10, show_preview: bool = True) -> Dict[str, Any]:
    """
    Streamlit-ready entry point.

    Parameters
    ----------
    tif_file : path or file-like
        GeoTIFF input (Streamlit UploadedFile or path).
    n_regions : int
        Number of regions per axis for averaging.
    show_preview : bool
        Whether to return an RGB preview figure.

    Returns
    -------
    dict
        {
            "rgb_fig": matplotlib.Figure or None,
            "scatter_fig": matplotlib.Figure,
            "ndvi_regions": ndarray (n_regions x n_regions),
            "temp_regions": ndarray (n_regions x n_regions),
            "ndvi_flat": 1D ndarray,
            "temp_flat": 1D ndarray,
            "covariance": float,
            "covariance_clean": float,
        }
    """
    # Build preview and read bands
    rgb_image, nir08, red, green, blue = _rgb_preview_from_tif(tif_file)

    # Compute NDVI using your vegetation.compute_ndvi (expects red, nir)
    ndvi = compute_ndvi(red, nir08)  # note: compute_ndvi expects (red, nir) in your original code

    # Compute temperature using your streamlit-ready temperature.load_and_compute
    temperature = load_and_compute(tif_file)
    # Ensure shapes match
    if ndvi.shape != temperature.shape:
        raise RuntimeError(f"NDVI shape {ndvi.shape} and temperature shape {temperature.shape} do not match")

    # Region averaging
    ndvi_regions = average_by_region(ndvi, n_regions)
    temp_regions = average_by_region(temperature, n_regions)

    # Flatten (retain NaNs for diagnostics)
    ndvi_flat = flatten(ndvi_regions)
    temp_flat = flatten(temp_regions)

    # Clean (remove any NaN pairs)
    valid_mask = (~np.isnan(ndvi_flat)) & (~np.isnan(temp_flat))
    ndvi_clean = ndvi_flat[valid_mask]
    temp_clean = temp_flat[valid_mask]

    # Compute covariances
    cov_clean = covariance1(ndvi_clean, temp_clean) if ndvi_clean.size >= 2 else float("nan")
    # For raw covariance, compute on paired non-NaN entries (same as cov_clean here)
    cov_raw = cov_clean

    # Prepare figures
    rgb_fig = plot_rgb_preview(rgb_image) if show_preview else None
    scatter_fig = plot_scatter(ndvi_flat, temp_flat)

    return {
        "rgb_fig": rgb_fig,
        "scatter_fig": scatter_fig,
        "ndvi_regions": ndvi_regions,
        "temp_regions": temp_regions,
        "ndvi_flat": ndvi_flat,
        "temp_flat": temp_flat,
        "covariance": cov_raw,
        "covariance_clean": cov_clean,
    }
