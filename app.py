# app.py
import streamlit as st
import matplotlib.pyplot as plt

from engineering_visualizations.modules.smoothing_algorithm import run as smooth_run
from engineering_visualizations.modules.temperature import run as temp_run
from engineering_visualizations.modules.integrated_analysis import run as integrated_run
from engineering_visualizations.modules.compare_regions_streamlit import run as compare_run


# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------
def rewind(src):
    try:
        src.seek(0)
    except Exception:
        pass


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(page_title="Engineering Visualizations", layout="wide")
st.title("Interactive Engineering Visualizations")

st.markdown(
    "Interactive engineering tools for image processing and geospatial analysis."
)

# ---------------------------------------------------------
# Built-in datasets (EDIT PATHS AS NEEDED)
# ---------------------------------------------------------
DATASETS = {
    "Rural Sample": "engineering_visualizations/data/canada_surface.tif",
    "Urban Sample": "engineering_visualizations/data/durham_summer24.tif",
    "Alberta 2024": "engineering_visualizations/data/land_cover_alberta.tif",
    "Québec": "engineering_visualizations/data/land_cover_québec.tif",
    "Surface Water": "engineering_visualizations/data/surface_water.tif",
}

# ---------------------------------------------------------
# Sidebar: input selection
# ---------------------------------------------------------
st.sidebar.header("Input Data")

dataset_name = st.sidebar.selectbox(
    "Choose a built-in dataset",
    list(DATASETS.keys())
)

uploaded = st.sidebar.file_uploader(
    "Or upload your own TIFF / image",
    type=["jpg", "jpeg", "png", "tif", "tiff"]
)

# Decide input source
if uploaded is not None:
    input_source = uploaded
else:
    input_source = DATASETS[dataset_name]

# ---------------------------------------------------------
# Sidebar: tool selection
# ---------------------------------------------------------
st.sidebar.header("Tool Selection")

tool = st.sidebar.selectbox(
    "Choose a tool",
    [
        "Image Smoothing",
        "Temperature Analysis",
        "NDVI × Temperature (Integrated Analysis)",
        "NDVI / Temp Explorer (Web UI)",
    ]
)

# ---------------------------------------------------------
# IMAGE SMOOTHING
# ---------------------------------------------------------
if tool == "Image Smoothing":

    st.header("Image Smoothing")

    kernel_size = st.sidebar.slider(
        "Smoothing kernel size",
        min_value=3,
        max_value=9,
        step=2,
        value=3
    )

    if input_source:
        rewind(input_source)
        fig_orig, fig_smooth = smooth_run(input_source, kernel_size=kernel_size)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Original")
            st.pyplot(fig_orig, use_container_width=True)
            plt.close(fig_orig)

        with col2:
            st.subheader(f"Smoothed (k={kernel_size})")
            st.pyplot(fig_smooth, use_container_width=True)
            plt.close(fig_smooth)

# ---------------------------------------------------------
# TEMPERATURE ANALYSIS
# ---------------------------------------------------------
elif tool == "Temperature Analysis":

    st.header("Surface Temperature Analysis")

    threshold_f = st.sidebar.slider(
        "Temperature threshold (°F)",
        80.0, 140.0, 120.0
    )

    if input_source:
        rewind(input_source)
        fig, count, pct = temp_run(input_source, threshold_f=threshold_f)

        col1, col2 = st.columns([3, 1])

        with col1:
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        with col2:
            st.metric(
                label="Pixels above threshold",
                value=f"{count}",
                delta=f"{pct:.2f}%"
            )

# ---------------------------------------------------------
# INTEGRATED ANALYSIS
# ---------------------------------------------------------
elif tool == "NDVI × Temperature (Integrated Analysis)":

    st.header("NDVI × Temperature — Integrated")

    n_regions = st.sidebar.slider("Regions per axis", 4, 40, 10)
    show_preview = st.sidebar.checkbox("Show RGB preview", value=True)

    if input_source:
        rewind(input_source)
        results = integrated_run(
            input_source,
            n_regions=n_regions,
            show_preview=show_preview
        )

        if results.get("rgb_fig"):
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("RGB Preview")
                st.pyplot(results["rgb_fig"], use_container_width=True)
                plt.close(results["rgb_fig"])

            with col2:
                st.subheader("NDVI vs Temperature")
                st.pyplot(results["scatter_fig"], use_container_width=True)
                plt.close(results["scatter_fig"])

        st.metric(
            label="Covariance (clean pairs)",
            value=f"{results['covariance_clean']:.4f}"
        )

# ---------------------------------------------------------
# TKINTER → STREAMLIT UI
# ---------------------------------------------------------
elif tool == "NDVI / Temp Explorer (Web UI)":

    st.header("NDVI / Temperature Explorer")

    view_mode = st.sidebar.selectbox(
        "View",
        ["rgb", "ndvi", "temp", "scatter"]
    )

    ndvi_thresh = st.sidebar.slider("NDVI threshold", 0.0, 1.0, 0.2)
    temp_thresh = st.sidebar.slider("Temperature threshold (°F)", 70.0, 130.0, 95.0)

    if input_source:
        rewind(input_source)
        results = compare_run(
            input_source,
            view_mode=view_mode,
            ndvi_thresh=ndvi_thresh,
            temp_thresh=temp_thresh
        )

        col1, col2 = st.columns([3, 1])

        with col1:
            st.pyplot(results["figure"], use_container_width=True)
            plt.close(results["figure"])

        with col2:
            if "correlation" in results:
                st.metric("Pearson r", f"{results['correlation']:.3f}")

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("_Built with Python, NumPy, rasterio, matplotlib, and Streamlit._")
