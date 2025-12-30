"""
compare_regions_streamlit.py

Streamlit-ready replacement for the Tkinter "Big UI".

Provides:
- RGB preview
- NDVI view
- Temperature view
- NDVI vs Temperature scatter
- Pearson correlation
"""

from typing import Dict, Any
import numpy as np
import rasterio
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from engineering_visualizations.modules.vegetation import compute_ndvi
from engineering_visualizations.modules.temperature import load_and_compute


def stretch_to_uint8(band: np.ndarray) -> np.ndarray:
    band = np.asarray(band, dtype=float)
    valid = band[~np.isnan(band)]
    lo = np.percentile(valid, 2) if valid.size else 0.0
    hi = np.percentile(valid, 98) if valid.size else 1.0
    clipped = np.clip(band, lo, hi)
    scaled = (clipped - lo) / (hi - lo + 1e-12)
    return (np.nan_to_num(scaled) * 255).astype(np.uint8)


def pearsonr_masked(x: np.ndarray, y: np.ndarray) -> float:
    mask = (~np.isnan(x)) & (~np.isnan(y))
    if mask.sum() < 2:
        return np.nan
    xm = x[mask].mean()
    ym = y[mask].mean()
    num = ((x[mask] - xm) * (y[mask] - ym)).sum()
    den = np.sqrt(((x[mask] - xm) ** 2).sum() * ((y[mask] - ym) ** 2).sum())
    return num / den if den != 0 else 0.0


def run(uploaded_tif, view_mode: str, ndvi_thresh: float, temp_thresh: float) -> Dict[str, Any]:
    """
    Streamlit entry point replacing the Tkinter UI.
    """

    uploaded_tif.seek(0)
    with rasterio.open(uploaded_tif) as src:
        nir = src.read(1).astype(float)
        red = src.read(2).astype(float)
        green = src.read(3).astype(float)
        blue = src.read(4).astype(float)

    ndvi = compute_ndvi(red, nir)
    uploaded_tif.seek(0)
    temp = load_and_compute(uploaded_tif)

    results = {}

    # ---------- RGB ----------
    if view_mode == "rgb":
        rgb = np.dstack((
            stretch_to_uint8(red),
            stretch_to_uint8(green),
            stretch_to_uint8(blue),
        ))
        fig, ax = plt.subplots()
        ax.imshow(rgb)
        ax.axis("off")
        results["figure"] = fig

    # ---------- NDVI ----------
    elif view_mode == "ndvi":
        fig, ax = plt.subplots()
        im = ax.imshow(ndvi, cmap="RdYlGn", vmin=-1, vmax=1)
        ax.imshow(np.ma.masked_where(ndvi < ndvi_thresh, ndvi),
                  cmap="Greens", alpha=0.3)
        plt.colorbar(im, ax=ax)
        ax.set_title("NDVI")
        ax.axis("off")
        results["figure"] = fig

    # ---------- TEMPERATURE ----------
    elif view_mode == "temp":
        fig, ax = plt.subplots()
        im = ax.imshow(temp, cmap="inferno")
        ax.imshow(np.ma.masked_where(temp < temp_thresh, temp),
                  cmap="Reds", alpha=0.3)
        plt.colorbar(im, ax=ax)
        ax.set_title("Surface Temperature (°F)")
        ax.axis("off")
        results["figure"] = fig

    # ---------- SCATTER ----------
    elif view_mode == "scatter":
        fig, ax = plt.subplots()
        ax.scatter(ndvi.ravel(), temp.ravel(), s=5, alpha=0.5)
        ax.set_xlabel("NDVI")
        ax.set_ylabel("Temperature (°F)")
        r = pearsonr_masked(ndvi.ravel(), temp.ravel())
        ax.set_title(f"NDVI vs Temperature (r = {r:.3f})")
        results["figure"] = fig
        results["correlation"] = r

    return results
