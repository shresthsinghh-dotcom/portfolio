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
st.markdown(
    """
    <style>
    /* Lock max height for Streamlit pyplot outputs */
    div[data-testid="stPyplot"] img {
        max-height: 350px;
        width: auto;
        margin-left: auto;
        margin-right: auto;
        display: block;
        align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Interactive Engineering Visualizations")

st.markdown(
    "This project was developed as part of an undergraduate engineering course, "
    "where I worked with a team to analyze satellite imagery and extract quantitative "
    "environmental insights using Python-based tools. Over several milestones, we "
    "designed a modular analysis pipeline supporting image preprocessing, surface "
    "temperature evaluation, and vegetation analysis.\n\n"
    "My contributions focused on data processing pipelines, analytical visualization, "
    "and the development of interactive analysis tools. The application supports multiple "
    "built-in datasets as well as user-uploaded GeoTIFF or image files. Use the sidebar "
    "to explore each analysis tool."
)


# ---------------------------------------------------------
# Built-in datasets (EDIT PATHS AS NEEDED)
# ---------------------------------------------------------
DATASETS = {
    "Rural Sample": "engineering_visualizations/data/canada_surface.tif",
    "Urban Sample": "engineering_visualizations/data/durham_summer24.tif",
    "Alberta": "engineering_visualizations/data/land_cover_alberta.tif",
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
        "Surface Temperature Analysis",
        "Integrated Analysis",
        "Interactive Analysis UI",
    ]
)

# ---------------------------------------------------------
# IMAGE SMOOTHING
# ---------------------------------------------------------
if tool == "Image Smoothing":

    st.header("Image Smoothing")
    st.markdown(
    "This tool applies spatial smoothing to satellite imagery using an adjustable "
    "averaging kernel. The original image is shown alongside the smoothed output to "
    "illustrate the effect of kernel size on noise reduction and feature clarity. "
    "This preprocessing step serves as a foundation for subsequent analyses."
)

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
elif tool == "Surface Temperature Analysis":

    st.header("Surface Temperature Analysis")
    st.markdown(
        "This integrated analysis examines the relationship between vegetation density "
        "(NDVI) and surface temperature across spatial regions. Adjusting the number of "
        "regions per axis allows exploration of covariance behavior at different spatial "
        "scales, supporting quantitative interpretation of environmental patterns."
)

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
elif tool == "Integrated Analysis":

    st.header("NDVI × Temperature — Integrated")
    st.markdown(
    "This analysis is used to derive covariance of the surface temperature data. You may notice a slider that controls the regions per axis. " \
    "You can adjust this threshold, which will show you the covariance plot at a small or large scale. " \
    "This is the third milestone tool necessary for the final analysis. Enjoy working with it!" \
    )
    n_regions = st.sidebar.slider("Regions per axis", 4, 40, 10)
    show_preview = st.sidebar.checkbox("Show RGB preview", value=True)

    if input_source:
        rewind(input_source)
        results = integrated_run(
            input_source,
            n_regions=n_regions,
            show_preview=show_preview
        )

        # ---- ERROR HANDLING (THIS WAS MISSING) ----
        if results.get("error"):
            err = results["error"]
            st.error("Integrated analysis failed.")
            if isinstance(err, dict) and "traceback" in err:
                st.text_area("Details", err["traceback"], height=300)
            else:
                st.write(err)
            st.stop()

        # ---- NORMAL RENDER ----
        left, center, right = st.columns([1, 4, 1])
        with center:
            if results.get("rgb_fig"):
                st.subheader("RGB Preview")
                st.pyplot(results["rgb_fig"], use_container_width=True)
                plt.close(results["rgb_fig"])

            st.subheader("NDVI vs Temperature")
            st.pyplot(results["scatter_fig"], use_container_width=True)
            plt.close(results["scatter_fig"])

        st.metric(
            "Covariance",
            f"{results['covariance_clean']:.4f}"
        )
    else:
        st.info("Select a TIFF dataset.")

# ---------------------------------------------------------
# TKINTER → STREAMLIT UI
# ---------------------------------------------------------
elif tool == "Interactive Analysis UI":

    st.header("NDVI / Temperature Explorer")
    st.markdown(
        "This interactive interface consolidates all prior analysis tools into a unified "
        "visual exploration environment. Users can examine RGB imagery, NDVI maps, "
        "temperature thresholds, and correlation plots while adjusting key parameters "
        "to observe their effect on the analysis results."
    )


    # UI labels (canonical) → internal keys (required by module)
    VIEW_MAP = {
        "RGB": "rgb",
        "NDVI": "ndvi",
        "TEMP": "temp",
        "Scatterplot": "scatter",
    }

    view_mode = st.sidebar.selectbox(
        "View",
        list(VIEW_MAP.keys())
    )

    ndvi_thresh = st.sidebar.slider("NDVI threshold", 0.0, 1.0, 0.2)
    temp_thresh = st.sidebar.slider("Temperature threshold (°F)", 70.0, 130.0, 95.0)

    if input_source:
        rewind(input_source)
        results = compare_run(
            input_source,
            view_mode=VIEW_MAP[view_mode],
            ndvi_thresh=ndvi_thresh,
            temp_thresh=temp_thresh
        )

        # ---- CENTERED DISPLAY ----
        left, center, right = st.columns([1, 4, 1])

        with center:
            st.pyplot(results["figure"], use_container_width=True)
            plt.close(results["figure"])

        if "correlation" in results:
            st.metric("Pearson r", f"{results['correlation']:.3f}")
    else:
        st.info("Upload a GeoTIFF.")

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("_Built with Python, NumPy, rasterio, matplotlib, and Streamlit._")

