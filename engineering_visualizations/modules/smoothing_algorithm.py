from PIL import Image
import numpy as np
import rasterio

from engineering_visualizations.modules.display_image import display_image


def normalize(arr: np.ndarray) -> np.ndarray:
    """
    Normalize an array to 0–255 uint8 for display.
    """
    arr = arr.astype(float)
    arr -= arr.min()
    max_val = arr.max()
    if max_val != 0:
        arr /= max_val
    return (arr * 255).astype("uint8")


def run(uploaded_image):
    """
    Load an image (JPEG/PNG or scientific TIFF), apply smoothing
    to each channel, and return matplotlib figures for the
    original and smoothed images.

    Parameters:
        uploaded_image: Streamlit UploadedFile

    Returns:
        fig_original, fig_smoothed
    """

    filename = uploaded_image.name.lower()

    # ---------------------------------------------------------
    # CASE 1: Scientific TIFF (e.g., land cover, raster data)
    # ---------------------------------------------------------
    if filename.endswith((".tif", ".tiff")):
        with rasterio.open(uploaded_image) as src:
            data = src.read()  # shape: (bands, height, width)

        # Multi-band raster
        if data.shape[0] >= 3:
            red = normalize(data[0])
            green = normalize(data[1])
            blue = normalize(data[2])
        else:
            # Single-band raster → grayscale
            band = normalize(data[0])
            red = green = blue = band

    # ---------------------------------------------------------
    # CASE 2: Standard image (JPEG / PNG)
    # ---------------------------------------------------------
    else:
        img = Image.open(uploaded_image).convert("RGB")
        img = np.array(img)

        red = img[:, :, 0]
        green = img[:, :, 1]
        blue = img[:, :, 2]

    # ---------------------------------------------------------
    # Display original image
    # ---------------------------------------------------------
    fig_original = display_image(red.tolist(), green.tolist(), blue.tolist())

    # ---------------------------------------------------------
    # Apply smoothing to each channel
    # ---------------------------------------------------------
    smoothed_red = smooth_channel(red.tolist())
    smoothed_green = smooth_channel(green.tolist())
    smoothed_blue = smooth_channel(blue.tolist())

    fig_smoothed = display_image(
        smoothed_red,
        smoothed_green,
        smoothed_blue
    )

    return fig_original, fig_smoothed


def smooth_channel(channel: list[list[int]]) -> list[list[int]]:
    """
    Smooth a 2D channel using a 3×3 averaging filter
    with edge replication.
    """

    height = len(channel)
    width = len(channel[0])

    def get(y, x):
        y = min(max(y, 0), height - 1)
        x = min(max(x, 0), width - 1)
        return channel[y][x]

    smoothed = [[0] * width for _ in range(height)]

    for y in range(height):
        for x in range(width):
            total = 0
            count = 0

            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    total += get(y + dy, x + dx)
                    count += 1

            smoothed[y][x] = total // count

    return smoothed
