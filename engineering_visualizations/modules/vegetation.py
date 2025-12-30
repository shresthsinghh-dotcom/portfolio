"""
vegetation.py

Computes and visualizes NDVI (Normalized Difference Vegetation Index) from
satellite imagery to identify and quantify vegetation.

Assumes the TIFF uses:
    Band 1 = NIR
    Band 2 = Red
Adjust band indices if your dataset differs.
"""

import numpy as np
import matplotlib.pyplot as plt


def compute_ndvi(red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
    """
    Compute NDVI using the formula: (NIR - Red) / (NIR + Red).

    Simple explanation:
        NDVI tells how "green" each pixel is.
        Values near +1 = strong vegetation.
        Values near 0 = weak or no vegetation.
        Values < 0 = non-vegetated surfaces (water, shadows, etc.).

    Parameters
    ----------
    red_band : np.ndarray
        Red channel values.
    nir_band : np.ndarray
        Near-infrared channel values.

    Returns
    -------
    np.ndarray
        NDVI array with same shape as the inputs.
    """
    red_f = red_band.astype(np.float64)
    nir_f = nir_band.astype(np.float64)

    numerator = nir_f - red_f
    denominator = nir_f + red_f

    # Avoid division by small numbers
    eps = 1e-10
    ndvi = np.where(np.abs(denominator) < eps, 0.0, numerator / denominator)

    return ndvi


def calculate_vegetation_percentage(ndvi_array: np.ndarray, threshold: float = 0.2) -> float:
    """
    Compute how much of the image is classified as vegetation.

    Simple explanation:
        If NDVI >= threshold, count it as “vegetation.”

    Parameters
    ----------
    ndvi_array : np.ndarray
        NDVI values to analyze.
    threshold : float, optional
        Minimum NDVI value to classify as vegetation (default 0.2 because Above 0.2: 
        Surfaces start exhibiting vegetation characteristics (cooling effects, carbon uptake, etc.)

    Returns
    -------
    float
        Percentage of pixels above the threshold.
    """
    veg_pixels = np.sum(ndvi_array >= threshold)
    total = ndvi_array.size
    return (veg_pixels / total) * 100.0


def plot_ndvi(ndvi_array: np.ndarray, title: str | None = None) -> None:
    """
    Display an NDVI image using the red-yellow-green colormap.

    Parameters
    ----------
    ndvi_array : np.ndarray
        NDVI data.
    title : str or None
        Optional title. Use None to omit titles in lab figures.
    """
    plt.figure()
    plt.imshow(ndvi_array, cmap="RdYlGn", vmin=-1, vmax=1)
    plt.colorbar(label="NDVI Value")
    if title:
        plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def main(filename: str) -> None:
    """
    Load a GeoTIFF, compute NDVI, display it, and print vegetation percentage.

    Simple explanation:
        Opens the image, extracts NIR + Red, computes NDVI, plots the NDVI map,
        and prints how much vegetation (%) the region contains.

    Parameters
    ----------
    filename : str
        Path to the GeoTIFF.

    Returns
    -------
    None
    """
    import rasterio as rio  # imported here so module can be imported without rasterio installed

    with rio.open(filename) as tif:
        nir08 = tif.read(1)  # Band 1 = NIR
        red = tif.read(2)    # Band 2 = Red

    ndvi = compute_ndvi(red, nir08)
    plot_ndvi(ndvi, title=None)

    veg_pct = calculate_vegetation_percentage(ndvi)
    print(f"Vegetation percentage: {veg_pct:.2f}%")


if __name__ == "__main__":
    main("land_cover_québec.tif")
    main("land_cover_alberta.tif")
