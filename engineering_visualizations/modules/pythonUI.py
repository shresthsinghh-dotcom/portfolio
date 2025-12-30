#!/usr/bin/env python3
"""
Big UI with Compare Regions button.

Adds a "Compare Regions" sidebar button that computes mean NDVI and mean
surface temperature for Alberta and Québec, plus the NDVI-vs-temperature
Pearson correlation and a scatter plot.

Dependencies: numpy, rasterio, matplotlib, tkinter, vegetation.compute_ndvi,
temperature.load_and_compute
"""
import os  # used for file path checks and basename
import threading  # used to run heavy work in a background thread so UI stays responsive
import tkinter as tk  # main Tkinter namespace
from tkinter import filedialog, ttk, messagebox  # specific GUI helpers we use

import numpy as np  # array math and NaN-aware ops
import rasterio  # reading GeoTIFF bands
import matplotlib  # plotting library

# Force matplotlib to use TkAgg backend so figures integrate with Tkinter.
# This must be set before importing pyplot when embedding in Tk.
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt  # pyplot interface for creating figures
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # embed a matplotlib figure in Tk

# project-local helpers for computing NDVI and temperature
from vegetation import compute_ndvi
from temperature import load_and_compute

def _stretch_to_uint8(band: np.ndarray) -> np.ndarray:
    """Percentile stretch (2nd-98th) to uint8 for previewing.
    
    Input:
      band - 2D numeric array (float or integer), may contain NaNs for missing pixels.
    Output:
      2D uint8 array in the range 0..255 suitable for display with imshow.

    Why percentile stretch:
      - Satellite bands often have outliers; stretching between low/high percentiles
        (2nd and 98th here) reduces the effect of outliers while preserving contrast.
      - Using percentiles rather than min/max avoids saturating the contrast when
        a few extreme pixels exist (e.g., sensor noise or bright clouds).
    Implementation notes:
      - NaNs are ignored when computing percentiles so missing data doesn't skew stats.
      - If hi == lo (constant band or tiny valid sample), we return zeros to avoid division by zero.
      - 1e-12 prevents divide-by-zero due to floating point rounding when hi-lo is extremely small.
      - np.nan_to_num converts NaNs to 0 in the final image (so missing pixels appear dark).
    """
    band = np.asarray(band, dtype=float)  # ensure we have a float ndarray to compute percentiles & NaNs
    valid = ~np.isnan(band)  # mask of valid (non-NaN) pixels
    if not np.any(valid):
        # no valid pixels — pick a default stretch so image won't crash
        lo, hi = 0.0, 1.0
    else:
        # compute 2nd and 98th percentiles over only valid pixels
        lo = np.percentile(band[valid], 2)
        hi = np.percentile(band[valid], 98)
    # clip values to the computed range so extremes are clamped
    clipped = np.clip(band, lo, hi)
    if hi == lo:
        # degenerate case: avoid dividing by zero; produce zeros so preview is uniform
        scaled = np.zeros_like(clipped)
    else:
        # scale clipped values to 0..1
        scaled = (clipped - lo) / (hi - lo + 1e-12)
    # replace NaNs with 0 and convert to uint8 0..255 for display
    return (np.nan_to_num(scaled) * 255).astype(np.uint8)


def _pearsonr_masked(x: np.ndarray, y: np.ndarray):
    """Compute Pearson r for two 1D arrays after removing NaN pairs.

    Input:
      x, y - 1D arrays (or flattened 2D arrays). They may contain NaNs.
    Output:
      Pearson correlation coefficient (float), or np.nan if not enough valid pairs.

    Behavior:
      - Pairs where either x or y is NaN are excluded.
      - If fewer than 2 valid pairs remain, returns np.nan because correlation is undefined.
      - If denominator is zero (zero variance in x or y), returns 0.0 to indicate no linear relation
        *numerically* (some prefer np.nan here; returning 0.0 is a design choice used in this code).
    """
    x = np.asarray(x).astype(float)
    y = np.asarray(y).astype(float)
    mask = (~np.isnan(x)) & (~np.isnan(y))  # keep only pairs where both are valid
    if mask.sum() < 2:
        return np.nan  # not enough data to compute correlation reliably
    xm = x[mask].mean()  # mean over valid x values
    ym = y[mask].mean()  # mean over valid y values
    # numerator: covariance sum
    num = ((x[mask] - xm) * (y[mask] - ym)).sum()
    # denominator: product of standard deviations (sqrt of sum squares)
    den = np.sqrt(((x[mask] - xm) ** 2).sum() * ((y[mask] - ym) ** 2).sum())
    # protect against zero variance leading to divide-by-zero
    return (num / den) if den != 0 else 0.0

class SimpleViewer:
    """
    Big UI for RGB / Temperature / NDVI preview with a "Compare Regions" button.

    Layout summary:
      - Left sidebar: file chooser, view mode radio buttons, threshold entries, and Compare button.
      - Right area: matplotlib figure used as preview pane embedded in Tk.

    State:
      - self.path: current file path (or None)
      - self.cache: caches to avoid recomputing expensive results across redraws
    """

    def __init__(self, root: tk.Tk):
        # store root window and set window metadata
        self.root = root
        root.title("NDVI & Surface Temp — Big UI (with Compare)")
        root.geometry("1400x900")  # reasonable default size for the embedded figure

        # UI fonts and sizes stored as instance attributes for reuse
        self.BIG_FONT = ("Segoe UI", 18, "bold")
        self.MED_FONT = ("Segoe UI", 14)
        self.SM_FONT = ("Segoe UI", 12)

        # use ttk styling to make controls look nicer; 'clam' is a cross-platform theme
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("Big.TButton", font=self.BIG_FONT, padding=10)
        style.configure("Big.TRadiobutton", font=self.BIG_FONT, padding=8)
        style.configure("Big.TLabel", font=self.BIG_FONT)
        style.configure("Med.TLabel", font=self.MED_FONT)
        style.configure("Med.TEntry", font=self.MED_FONT)

        # top-level container to hold sidebar + preview panel
        container = ttk.Frame(root)
        container.pack(fill="both", expand=True)

        # Sidebar on the left: fixed width, vertical layout
        sidebar = ttk.Frame(container, width=360, padding=12, relief="flat")
        sidebar.pack(side="left", fill="y")

        # File select button — uses select_file method when clicked
        self.btn_select = ttk.Button(sidebar, text="📁  Select File", command=self.select_file, style="Big.TButton")
        self.btn_select.pack(fill="x", pady=(0, 12))

        # Status label shows loaded filename or error messages
        self.status = ttk.Label(sidebar, text="No file loaded", font=self.BIG_FONT, anchor="w", wraplength=320)
        self.status.pack(fill="x", pady=(0, 18))

        # Radio buttons to choose view mode
        ttk.Label(sidebar, text="View mode", style="Big.TLabel").pack(anchor="w", pady=(0, 8))

        self.view_mode = tk.StringVar(value="rgb")  # default view
        rb_frame = ttk.Frame(sidebar)
        rb_frame.pack(fill="x", pady=(0, 18))
        # choices pairs are (value, label). The radiobutton command calls redraw to update preview.
        choices = [("rgb", "🌈  RGB"), ("temp", "🔥  Temperature"), ("ndvi", "🌿  Vegetation")]
        for val, label in choices:
            rb = ttk.Radiobutton(rb_frame, text=label, variable=self.view_mode, value=val, command=self.redraw,
                                 style="Big.TRadiobutton", takefocus=False)
            rb.pack(fill="x", pady=6)

        # Threshold controls for NDVI and temperature overlays
        thr_frame = ttk.Frame(sidebar)
        thr_frame.pack(fill="x", pady=(4, 12))
        ttk.Label(thr_frame, text="NDVI threshold:", style="Med.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.ndvi_th = tk.DoubleVar(value=0.2)  # default NDVI threshold
        self.ndvi_entry = ttk.Entry(thr_frame, textvariable=self.ndvi_th, width=8, font=self.MED_FONT)
        self.ndvi_entry.grid(row=0, column=1, sticky="e", padx=(8, 0))

        ttk.Label(thr_frame, text="Temp threshold (°F):", style="Med.TLabel").grid(row=1, column=0, sticky="w", pady=(8, 6))
        self.temp_th = tk.DoubleVar(value=95.0)  # default temperature threshold (°F)
        self.temp_entry = ttk.Entry(thr_frame, textvariable=self.temp_th, width=8, font=self.MED_FONT)
        self.temp_entry.grid(row=1, column=1, sticky="e", padx=(8, 0))

        ttk.Label(sidebar, text="Tip: change thresholds, then click view mode.", font=self.SM_FONT, foreground="#333").pack(fill="x", pady=(12, 12))

        # New Compare Regions button triggers background work
        self.compare_btn = ttk.Button(sidebar, text="🔎  Compare Regions", command=self.run_compare_thread, style="Big.TButton")
        self.compare_btn.pack(fill="x", pady=(6, 6))

        # Right preview panel holds an embedded matplotlib FigureCanvas
        preview_panel = ttk.Frame(container, padding=8)
        preview_panel.pack(side="left", fill="both", expand=True)
        self.fig = plt.figure(figsize=(10, 7))  # figure matched to window size for nicer preview
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=preview_panel)  # widget that connects matplotlib to Tk
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # State and cache: path is current file; cache holds raw bands and derived products
        self.path = None
        self.cache = {"bands": {}, "rgb": None, "ndvi": None, "temp": None}

        # draw initial placeholder text
        self._draw_placeholder()

    # ---------- file loading ----------

    def select_file(self):
        """Open file dialog and load the first selected GeoTIFF into the cache."""
        # allow selecting multiple but we only use the first — keeping file dialog flexible
        paths = filedialog.askopenfilenames(title="Select GeoTIFF", filetypes=[("TIFF", "*.tif;*.tiff")])
        if not paths:
            return  # user cancelled
        self.path = paths[0]  # choose the first selected file
        try:
            self._load(self.path)  # load bands into cache
            # update status label with base filename for user feedback
            self.status.config(text=f"Loaded: {os.path.basename(self.path)}")
        except Exception as e:
            # show an error dialog if loading fails, and mark status
            messagebox.showerror("Load error", f"Failed to load {self.path}:\n{e}")
            self.status.config(text="Load failed")
        self.redraw()  # refresh preview after loading

    def _load(self, path: str):
        """Read available bands from the GeoTIFF into self.cache['bands'] and clear derived caches."""
        # using 'with' ensures the file handle is closed promptly after reading
        with rasterio.open(path) as src:
            count = src.count  # number of bands in the file
            bands = {}
            # read each band if possible; if a read fails, store None for that band index
            for i in range(1, count + 1):
                try:
                    bands[i] = src.read(i).astype(float)  # convert to float for downstream processing
                except Exception:
                    # reading a band failed (corrupt band, IO issue) — mark as None rather than crash
                    bands[i] = None
        # store raw band arrays and invalidate derived caches so they'll be recomputed lazily
        self.cache["bands"] = bands
        self.cache["rgb"] = None
        self.cache["ndvi"] = None
        self.cache["temp"] = None

    # ---------- drawing ----------

    def _draw_placeholder(self):
        """Show instructions when no file is loaded."""
        self.fig.clf()  # clear the figure
        self.ax = self.fig.add_subplot(1, 1, 1)
        # explanatory text on center of preview pane
        self.ax.text(0.5, 0.5, "Load a GeoTIFF using the button on the left\nthen choose a view (RGB / Temp / Vegetation)",
                     ha="center", va="center", fontsize=18)
        self.ax.axis("off")  # hide axes ticks and borders for cleaner instructions
        self.canvas.draw_idle()  # request a redraw of the embedded canvas

    def redraw(self):
        """Redraw preview according to current view_mode; avoids adding multiple colorbars."""
        self.fig.clf()  # clear existing artists to avoid overlapping plots
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.clear()  # reset axes state

        if self.path is None:
            # if no file selected, show placeholder help text
            self._draw_placeholder()
            return

        mode = self.view_mode.get()  # which preview mode the user selected
        bands = self.cache.get("bands", {})

        # helper closure to pick the desired band but fall back to an alternative if missing
        def get_band(primary, fallback=None):
            b = bands.get(primary)
            if b is None and fallback is not None:
                b = bands.get(fallback)
            return b

        # choose common band indexes (this UI assumes a dataset layout like: 1=NIR,2=Red,3=Green,4=Blue,5=LWIR)
        red_band = get_band(2, 1)
        green_band = get_band(3, 2)
        blue_band = get_band(4, 3)
        nir_band = get_band(1, 4)

        # grab cached derived products if available (avoid recomputation)
        rgb = self.cache.get("rgb")
        ndvi = self.cache.get("ndvi")
        temp = self.cache.get("temp")

        # ---------- RGB view ----------
        if mode == "rgb":
            # if we haven't computed an 8-bit RGB preview but have raw bands, compute it lazily
            if rgb is None and red_band is not None and green_band is not None and blue_band is not None:
                try:
                    # stretch each band to uint8 for display, stack into a 3-channel RGB image
                    r8 = _stretch_to_uint8(red_band)
                    g8 = _stretch_to_uint8(green_band)
                    b8 = _stretch_to_uint8(blue_band)
                    rgb = np.dstack((r8, g8, b8))
                    self.cache["rgb"] = rgb  # cache result so next redraw is fast
                except Exception:
                    rgb = None  # on error, fall back to message

            if rgb is None:
                # if still no RGB data, inform the user in the preview pane
                self.ax.text(0.5, 0.5, "RGB not available for this file", ha="center", va="center", fontsize=18)
                self.ax.axis("off")
            else:
                # show the RGB image; origin="upper" matches typical GeoTIFF orientation for row-major display
                self.ax.imshow(rgb, origin="upper")
                self.ax.set_title("RGB preview", fontsize=18)
                self.ax.axis("off")

        # ---------- Temperature view ----------
        elif mode == "temp":
            if temp is None:
                try:
                    # load_and_compute is expected to read the LWIR band and return a temperature array (°F)
                    temp_try = load_and_compute(self.path)
                    if isinstance(temp_try, np.ndarray):
                        temp = temp_try
                        self.cache["temp"] = temp  # cache temperature for reuse
                except Exception:
                    temp = None

            if temp is None:
                self.ax.text(0.5, 0.5, "Temperature not available for this file", ha="center", va="center", fontsize=18)
                self.ax.axis("off")
            else:
                # display a colormap of temperature, add colorbar, and overlay threshold mask
                im = self.ax.imshow(temp, cmap="inferno", origin="upper")
                self.ax.set_title("Surface Temperature (°F)", fontsize=18)
                self.fig.colorbar(im, ax=self.ax, fraction=0.04)  # small colorbar
                try:
                    thr = float(self.temp_th.get())  # read threshold value from UI; defensive float()
                except Exception:
                    thr = 95.0  # fallback default
                # create a mask where temperature exceeds threshold — mark these as 1.0, others NaN
                mask = np.where(temp > thr, 1.0, np.nan)
                # overlay the mask with some transparency; mask NaNs so non-thresholded pixels are transparent
                self.ax.imshow(np.ma.masked_invalid(mask), cmap="Reds", alpha=0.35, origin="upper")
                self.ax.axis("off")

        # ---------- NDVI view ----------
        elif mode == "ndvi":
            # compute NDVI lazily when needed
            if ndvi is None and red_band is not None and nir_band is not None:
                try:
                    # compute_ndvi expects (red, nir) or (red, nir) depending on implementation — here passed as floats
                    ndvi_try = compute_ndvi(red_band.astype(np.float32), nir_band.astype(np.float32))
                    if isinstance(ndvi_try, np.ndarray):
                        ndvi = ndvi_try
                        self.cache["ndvi"] = ndvi
                except Exception:
                    ndvi = None

            if ndvi is None:
                self.ax.text(0.5, 0.5, "NDVI not available for this file", ha="center", va="center", fontsize=18)
                self.ax.axis("off")
            else:
                # NDVI commonly ranges -1..1; using RdYlGn shows greenness clearly
                im = self.ax.imshow(ndvi, cmap="RdYlGn", vmin=-1, vmax=1, origin="upper")
                self.ax.set_title("NDVI", fontsize=18)
                self.fig.colorbar(im, ax=self.ax, fraction=0.04)
                try:
                    ndt = float(self.ndvi_th.get())
                except Exception:
                    ndt = 0.2
                # overlay mask of pixels with NDVI >= threshold to highlight vegetated areas
                mask = np.where(ndvi >= ndt, 1.0, np.nan)
                self.ax.imshow(np.ma.masked_invalid(mask), cmap="Greens", alpha=0.25, origin="upper")
                self.ax.axis("off")

        else:
            # defensive fallback for unknown view mode value
            self.ax.text(0.5, 0.5, "Unknown view mode", ha="center", va="center", fontsize=18)
            self.ax.axis("off")

        # after preparing the axes, request a canvas update
        self.canvas.draw_idle()

    # ---------- compare feature ----------

    def run_compare_thread(self):
        """Start background thread for comparing the two default region files.

        The heavy compute is done off the main UI thread to keep the application responsive.
        """
        threading.Thread(target=self._compare_regions_thread, daemon=True).start()

    def _compare_regions_thread(self):
        """
        Worker thread: computes mean NDVI, mean temperature, and Pearson r
        for the two region files and displays results + scatter plot.

        Notes:
          - This method contains some UI calls in the original file; GUI operations should be
            run on the main thread. In this implementation the code attempts to schedule message
            boxes via self.root.after(0, ...) in some places to move UI interactions to main thread.
        """
        # default paths (user can change if they want; kept simple here)
        a_path = "land_cover_alberta.tif"
        q_path = "land_cover_québec.tif"

        # if files not present, allow user to pick them
        if not (os.path.exists(a_path) and os.path.exists(q_path)):
            # notify the user on the main thread that defaults weren't found
            self.root.after(0, lambda: messagebox.showinfo("Compare regions", "Default region files not found. Please choose Alberta then Québec TIFFs."))
            # show file dialogs here — note: these are called from the worker thread in the original;
            # the UI should schedule these on the main thread for thread-safety. This code calls them
            # directly which may sometimes work but is not guaranteed to be safe across platforms.
            a_sel = filedialog.askopenfilename(title="Select Alberta GeoTIFF (or Cancel)", filetypes=[("TIFF", "*.tif;*.tiff")])
            if not a_sel:
                return  # user cancelled file selection
            q_sel = filedialog.askopenfilename(title="Select Québec GeoTIFF (or Cancel)", filetypes=[("TIFF", "*.tif;*.tiff")])
            if not q_sel:
                return
            a_path, q_path = a_sel, q_sel

        try:
            # compare_regions is the pure function that does the heavy lifting of reading files
            # and computing statistics — it returns a dictionary with results and arrays for plotting.
            result = compare_regions(a_path, q_path)
        except Exception as e:
            # schedule an error dialog on the main thread so the message box is displayed safely
            self.root.after(0, lambda: messagebox.showerror("Compare error", f"Comparison failed:\n{e}"))
            return

        # define a function that will be executed on the main thread to show results and a plot
        def _show_summary():
            # build a concise textual summary showing mean values and Pearson r's
            msg = (f"Alberta: mean NDVI={result['alberta_mean_ndvi']:.3f}, mean Temp={result['alberta_mean_temp']:.1f}°F\n"
                   f"Québec : mean NDVI={result['quebec_mean_ndvi']:.3f}, mean Temp={result['quebec_mean_temp']:.1f}°F\n\n"
                   f"NDVI↔Temp Pearson r (Alberta): {result['alberta_r']:.3f}\n"
                   f"NDVI↔Temp Pearson r (Québec) : {result['quebec_r']:.3f}\n"
                   f"Cross-region NDVI vs Temp Pearson r: {result['cross_r']:.3f}")
            messagebox.showinfo("Region comparison results", msg)  # display summary in a simple dialog
            # open scatter plot in a separate matplotlib window to show pixel-level relationship
            plt.figure(figsize=(9, 6))
            plt.scatter(result["alberta_ndvi_flat"], result["alberta_temp_flat"], s=10, alpha=0.6, label="Alberta")
            plt.scatter(result["quebec_ndvi_flat"], result["quebec_temp_flat"], s=10, alpha=0.6, label="Québec")
            plt.xlabel("NDVI")
            plt.ylabel("Temperature (°F)")
            plt.legend()
            plt.title("NDVI vs Surface Temp — Alberta (blue) vs Québec (orange)")
            plt.tight_layout()
            plt.show()  # blocks in some backends; in an embedded app consider non-blocking or Toplevel with FigureCanvas

        # schedule the summary/reporting to run on the Tk main loop so dialogs and plotting are safe
        self.root.after(0, _show_summary)

def _flatten_and_mask(arr: np.ndarray):
    """Flatten a 2D array and return 1D array with NaNs preserved.

    This helper simply calls ravel() so the pixel indexing order is row-major.
    We deliberately keep NaNs so downstream callers can mask or ignore them as needed.
    """
    return np.asarray(arr).ravel()


def compare_regions(alberta_path: str, quebec_path: str) -> dict:
    """
    Compare two GeoTIFFs: compute mean NDVI, mean temp, and Pearson r.

    Returns a dict with:
      - alberta_mean_ndvi, alberta_mean_temp
      - quebec_mean_ndvi, quebec_mean_temp
      - alberta_r, quebec_r (NDVI vs temp within-region)
      - cross_r (NDVI vs temp across both regions combined)
      - and flattened arrays for plotting

    High-level steps:
      - Load red + NIR bands to compute NDVI via compute_ndvi.
      - Load LWIR / temperature via load_and_compute.
      - Compute mean values (ignoring NaNs) and correlations after flattening.
    """
    # helper to load and compute NDVI and temperature arrays for a single file
    def load_stats(path):
        # open once to read bands that compute_ndvi needs (NIR and red)
        with rasterio.open(path) as src:
            # follow assumed band ordering for this dataset: 1=NIR, 2=Red
            nir = src.read(1).astype(float)
            red = src.read(2).astype(float)
        # compute_ndvi expects (red, nir) here — returns array with NaNs where division was invalid
        ndvi = compute_ndvi(red, nir)
        # load_and_compute reads the thermal band and returns an array of temperatures in °F (per temperature.py contract)
        temp = load_and_compute(path)
        return ndvi, temp

    # load both regions' NDVI and temp arrays
    a_ndvi, a_temp = load_stats(alberta_path)
    q_ndvi, q_temp = load_stats(quebec_path)

    # compute means ignoring NaNs so masked/missing pixels don't bias the average
    a_mean_ndvi = float(np.nanmean(a_ndvi))
    q_mean_ndvi = float(np.nanmean(q_ndvi))
    a_mean_temp = float(np.nanmean(a_temp))
    q_mean_temp = float(np.nanmean(q_temp))

    # flatten arrays to 1D for correlation and plotting; NaNs are preserved and handled by _pearsonr_masked
    a_ndf = _flatten_and_mask(a_ndvi)
    a_tempf = _flatten_and_mask(a_temp)
    q_ndf = _flatten_and_mask(q_ndvi)
    q_tempf = _flatten_and_mask(q_temp)

    # compute within-region Pearson r (handles NaNs inside)
    a_r = _pearsonr_masked(a_ndf, a_tempf)
    q_r = _pearsonr_masked(q_ndf, q_tempf)

    # combined cross-region arrays and correlation — useful for seeing generality of relationship
    all_ndf = np.concatenate([a_ndf, q_ndf])
    all_tempf = np.concatenate([a_tempf, q_tempf])
    cross_r = _pearsonr_masked(all_ndf, all_tempf)

    # return a dictionary containing both scalar summaries and arrays for plotting / further analysis
    return {
        "alberta_mean_ndvi": a_mean_ndvi,
        "alberta_mean_temp": a_mean_temp,
        "quebec_mean_ndvi": q_mean_ndvi,
        "quebec_mean_temp": q_mean_temp,
        "alberta_r": a_r,
        "quebec_r": q_r,
        "cross_r": cross_r,
        "alberta_ndvi_flat": a_ndf,
        "alberta_temp_flat": a_tempf,
        "quebec_ndvi_flat": q_ndf,
        "quebec_temp_flat": q_tempf,
    }


def main():
    # create the main Tk window and run the app
    root = tk.Tk()
    app = SimpleViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
