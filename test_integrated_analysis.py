"""
test_integrated_analysis.py

Minimal test harness to run the integrated analysis without Streamlit.
Use this to debug rasterio, band order, shapes, and covariance logic.
"""

import os
import matplotlib.pyplot as plt

from engineering_visualizations.modules.integrated_analysis import run


def main():
    # CHANGE THIS PATH if needed
    tif_path = "engineering_visualizations/data/land_cover_alberta.tif"

    if not os.path.exists(tif_path):
        raise FileNotFoundError(
            f"Test file not found: {tif_path}\n"
            "Place the TIFF in the project root or update tif_path."
        )

    print("Running integrated analysis on:", tif_path)

    results = run(
        tif_path,
        n_regions=10,
        show_preview=True
    )

    if results.get("error"):
        print("\n❌ ERROR returned by integrated analysis:")
        err = results["error"]
        if isinstance(err, dict):
            print("Message:", err.get("error"))
            print("Traceback:\n", err.get("traceback"))
        else:
            print(err)
        return

    print("\n✅ Analysis completed successfully.")
    print("Covariance (clean):", results.get("covariance_clean"))

    if results.get("rgb_fig") is not None:
        print("Displaying RGB preview...")
        results["rgb_fig"].show()

    print("Displaying scatter plot...")
    results["scatter_fig"].show()


if __name__ == "__main__":
    main()
