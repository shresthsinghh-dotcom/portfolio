#!/usr/bin/env python3
"""
covariance_analysis.py

Compute region-averaged NDVI and surface temperature from a GeoTIFF, then
compute and display covariance / scatter plot between NDVI and temperature.

This script expects a GeoTIFF with at least five bands in the following
assumed ordering for this course dataset:

    1: NIR (nir08)
    2: Red
    3: Green
    4: Blue
    5: LWIR (lwir11 / surface temperature source)

Adjust band indices if your dataset uses a different ordering.
"""
import numpy as np
import rasterio as rio
import matplotlib.pyplot as plt
from vegetation import compute_ndvi
from CMilestone.C03_covariance import flatten, covariance1
from temperature import load_and_compute


def average_by_region(array2d, x_length):
    """
    Split a 2D array into x_length × x_length regions and return region means.

    In plain terms:
      - Divides the input 2D array into a square grid of regions.
      - Computes the mean value within each region (ignoring NaNs).
      - The last row/column regions extend to the array edge so all pixels are used.

    Parameters
    ----------
    array2d : array-like
        2D numeric array (e.g., NDVI or temperature).
    x_length : int
        Number of regions along each axis.

    Returns
    -------
    numpy.ndarray
        2D array (shape: x_length × x_length) of region averages (float).
        Regions with no pixels are set to NaN.
    """
    arr = np.array(array2d)
    if arr.ndim != 2:
        raise ValueError("average_by_region expects a 2D array")

    rows, cols = arr.shape
    # integer region size; last region picks up remainder
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


def display_rgb(tif_path, n_regions: int = 10, show_plots: bool = True):
    """
    Load the TIFF, compute NDVI and temperature, compute region averages, and return results.

    What it does (simple):
      - Reads the expected bands (NIR, Red, Green, Blue).
      - Builds an RGB preview by percentile stretching (2nd–98th).
      - Computes NDVI and surface temperature (using temperature.load_and_compute).
      - Aggregates NDVI and temperature into n_regions × n_regions tiles.
      - Computes covariance and optionally displays preview and scatter plots.

    Parameters
    ----------
    tif_path : str
        Path to the GeoTIFF file.
    n_regions : int
        Number of regions per axis for averaging.
    show_plots : bool
        If True, show matplotlib figures; set False for headless runs.

    Returns
    -------
    dict
        {
            "ndvi_regions": ndarray (n_regions×n_regions),
            "temp_regions": ndarray (n_regions×n_regions),
            "ndvi_flat": 1D ndarray (flattened region means, NaNs included),
            "temp_flat": 1D ndarray (flattened region means, NaNs included),
            "covariance": float (covariance computed over flattened arrays with NaNs kept),
        }
    """
    # read expected bands from file
    with rio.open(tif_path) as tif_data:
        nir08 = tif_data.read(1).astype(float)
        red = tif_data.read(2).astype(float)
        green = tif_data.read(3).astype(float)
        blue = tif_data.read(4).astype(float)
        # note: we call load_and_compute for temperature (it will read needed bands)

    # helper: robust percentile stretch -> uint8 for preview
    def stretch_to_uint8(band):
        valid = band[~np.isnan(band)] if np.any(~np.isnan(band)) else band
        lo = np.percentile(valid, 2) if valid.size else 0.0
        hi = np.percentile(valid, 98) if valid.size else 1.0
        clipped = np.clip(band, lo, hi)
        if hi == lo:
            scaled = np.zeros_like(clipped, dtype=float)
        else:
            scaled = (clipped - lo) / (hi - lo)
        return (np.nan_to_num(scaled) * 255).astype(np.uint8)

    # RGB preview (uint8 HxWx3)
    new_red = stretch_to_uint8(red)
    new_green = stretch_to_uint8(green)
    new_blue = stretch_to_uint8(blue)
    rgb_image = np.dstack((new_red, new_green, new_blue))

    if show_plots:
        plt.figure()
        plt.imshow(rgb_image)
        plt.axis("off")
        plt.tight_layout()
        plt.show()

    # compute NDVI and temperature rasters
    ndvi = compute_ndvi(red, nir08)

    try:
        temperature = load_and_compute(tif_path)
    except Exception as exc:
        raise RuntimeError(f"Failed to compute temperature for {tif_path}: {exc}") from exc

    # ensure NDVI and temperature align
    if ndvi.shape != temperature.shape:
        raise RuntimeError(f"NDVI shape {ndvi.shape} and temperature shape {temperature.shape} do not match")

    # region averages using the requested n_regions
    ndvi_regions = average_by_region(ndvi, n_regions)
    temp_regions = average_by_region(temperature, n_regions)

    # flatten region grids for covariance; keep NaNs for diagnostic plotting, mask later if needed
    ndvi_flat = np.asarray(flatten(ndvi_regions))
    temp_flat = np.asarray(flatten(temp_regions))

    # print basic shapes for quick debugging when interactive
    print("NDVI shape:", ndvi.shape)
    print("Temperature shape:", temperature.shape)
    print("Flattened lengths:", len(ndvi_flat), len(temp_flat))

    # remove pairs where either is NaN for cleaned covariance
    valid_mask = (~np.isnan(ndvi_flat)) & (~np.isnan(temp_flat))
    ndvi_clean = ndvi_flat[valid_mask]
    temp_clean = temp_flat[valid_mask]

    # compute covariance on the cleaned (NaN-free) arrays for a robust scalar
    region_cov_clean = covariance1(ndvi_clean, temp_clean)
    print("Region covariance (NDVI, Temperature) [clean]:", region_cov_clean)

    # compute covariance on raw flattened arrays (may include NaNs -> behaviour depends on covariance1)
    region_cov = covariance1(ndvi_flat[~np.isnan(ndvi_flat)], temp_flat[~np.isnan(temp_flat)]) if np.any(~np.isnan(ndvi_flat)) and np.any(~np.isnan(temp_flat)) else region_cov_clean
    print("Region covariance (NDVI, Temperature):", region_cov)

    # optional scatter of raw region means (useful for quick visual checks)
    if show_plots:
        plt.figure()
        plt.scatter(ndvi_flat, temp_flat, s=20, alpha=0.8)
        plt.xlabel("NDVI")
        plt.ylabel("Temperature (°F)")
        plt.tight_layout()
        plt.show()

    return {
        "ndvi_regions": ndvi_regions,
        "temp_regions": temp_regions,
        "ndvi_flat": ndvi_flat,
        "temp_flat": temp_flat,
        "covariance": region_cov,
    }


if __name__ == "__main__":
    # Example invocation for interactive use
    display_files = ["land_cover_alberta.tif", "land_cover_québec.tif"]
    for f in display_files:
        display_rgb(tif_path=f)
