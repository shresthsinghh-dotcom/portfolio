#!/usr/bin/env python3
"""
main.py

Analyzes satellite imagery to examine the correlation between green space (NDVI)
and surface temperatures.

Usage:
    python main.py
"""

# Import the top-level main functions from the modules that perform each analysis.
# Each imported function is expected to accept a path to a GeoTIFF and run its analysis.
from vegetation import main as vegetation_main
from temperature import main as temperature_main
from new_covariance import display_rgb as covariance_main


def main():
    """
    Run the full Green Space analysis for Alberta and Québec.

    What it does (simple):
      - Defines the file paths for two region images (Alberta and Québec).
      - Runs the vegetation module (NDVI) for each file.
      - Runs the temperature module (surface temp) for each file.
      - Runs the covariance/integrated analysis for each file.
      - Prints progress messages to the console.

    Parameters:
      - None (file paths are hard-coded in this script).

    Produces:
      - Console output describing progress.
      - Plots/files created by the called modules (vegetation, temperature, covariance).
    """
    # Paths to the GeoTIFFs for each region we will analyze.
    alberta_file = "land_cover_alberta.tif"   # file for Alberta region
    quebec_file = "land_cover_québec.tif"    # file for Québec region

    # Print a clear header so the console output is easy to read.
    print("=" * 60)
    print("GREEN SPACE PROJECT - A MILESTONE")
    print("Analyzing Québec and Alberta Satellite Imagery")
    print("=" * 60)
    print()

    # Run vegetation analysis for both regions.
    # vegetation_main should compute NDVI maps and save/display them.
    print("Running vegetation analysis...")
    vegetation_main(alberta_file)   # analyze Alberta NDVI
    vegetation_main(quebec_file)    # analyze Québec NDVI
    print()

    # Run temperature analysis for both regions.
    # temperature_main should compute surface temperature arrays and generate plots.
    print("Running temperature analysis...")
    temperature_main(alberta_file)  # analyze Alberta surface temperature
    temperature_main(quebec_file)   # analyze Québec surface temperature
    print()

    # Run integrated covariance / scatter analysis for both regions.
    # covariance_main (display_rgb) performs region-averaged analysis and scatter plots.
    print("Running integrated analysis...")
    covariance_main(alberta_file)   # integrated analysis for Alberta
    covariance_main(quebec_file)    # integrated analysis for Québec

    # Final status message to mark completion.
    print()
    print("=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
