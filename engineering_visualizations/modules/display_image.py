# engineering_visualizations/modules/display_image.py

import numpy as np
import matplotlib.pyplot as plt


def display_image(
    red: list[list[int]],
    green: list[list[int]],
    blue: list[list[int]]
):
    """
    Create and return a matplotlib figure displaying an RGB image
    constructed from separate red, green, and blue channels.

    Parameters:
        red, green, blue: 2D lists of integers (0–255)

    Returns:
        fig: matplotlib Figure object
    """

    # Stack channels into an RGB array
    rgb = np.stack([red, green, blue], axis=-1).astype("uint8")

    # Create matplotlib figure
    fig, ax = plt.subplots()
    ax.imshow(rgb)
    ax.axis("off")

    return fig
