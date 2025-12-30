from PIL import Image
import numpy as np
import rasterio

from engineering_visualizations.modules.display_image import display_image


def normalize(arr: np.ndarray) -> np.ndarray:
    arr = arr.astype(float)
    arr -= arr.min()
    max_val = arr.max()
    if max_val != 0:
        arr /= max_val
    return (arr * 255).astype("uint8")


def smooth_channel(channel: np.ndarray, k: int = 3) -> np.ndarray:
    """
    Fast k×k mean filter using NumPy padding.
    k must be odd.
    """
    channel = channel.astype(float)
    pad = k // 2

    padded = np.pad(channel, pad_width=pad, mode="edge")
    smoothed = np.zeros_like(channel)

    # Sliding window mean (still loops, but far fewer operations than Python lists)
    for i in range(channel.shape[0]):
        for j in range(channel.shape[1]):
            smoothed[i, j] = padded[i:i+k, j:j+k].mean()

    return smoothed.astype("uint8")


def run(uploaded_image, kernel_size: int = 3):
    """
    Apply fast NumPy smoothing with adjustable kernel size.
    Returns (original_fig, smoothed_fig).
    """

    filename = uploaded_image.name.lower()

    # ---------------------------------------------------------
    # TIFF
    # ---------------------------------------------------------
    if filename.endswith((".tif", ".tiff")):
        with rasterio.open(uploaded_image) as src:
            data = src.read()

        if data.shape[0] >= 3:
            red = normalize(data[0])
            green = normalize(data[1])
            blue = normalize(data[2])
        else:
            band = normalize(data[0])
            red = green = blue = band

    # ---------------------------------------------------------
    # JPEG / PNG
    # ---------------------------------------------------------
    else:
        img = Image.open(uploaded_image).convert("RGB")
        img = np.array(img)
        red = img[:, :, 0]
        green = img[:, :, 1]
        blue = img[:, :, 2]

    # Original
    fig_original = display_image(red.tolist(), green.tolist(), blue.tolist())

    # Smoothed (FAST)
    smoothed_red = smooth_channel(red, kernel_size)
    smoothed_green = smooth_channel(green, kernel_size)
    smoothed_blue = smooth_channel(blue, kernel_size)

    fig_smoothed = display_image(
        smoothed_red.tolist(),
        smoothed_green.tolist(),
        smoothed_blue.tolist()
    )

    return fig_original, fig_smoothed
