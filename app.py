# app.py
import streamlit as st

from engineering_visualizations.modules.smoothing_algorithm import run as smooth_run
from engineering_visualizations.modules.temperature import run as temp_run
from engineering_visualizations.modules.integrated_analysis import run as integrated_run


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Engineering Visualizations",
    layout="wide"
)

st.title("Interactive Engineering Visualizations")

st.markdown(
    """
    This application showcases Python-based engineering tools for image processing
    and geospatial analysis. Each module demonstrates a complete computational
    pipeline, from raw data ingestion to visualization.
    """
)

# ---------------------------------------------------------
# Sidebar: tool selection
# ---------------------------------------------------------
st.sidebar.header("Tool Selection")

tool = st.sidebar.selectbox(
    "Choose a tool",
    [
        "Image Smoothing",
        "Surface Temperature Analysis",
        "NDVI × Temperature (Integrated Analysis)",
    ]
)


uploaded = st.sidebar.file_uploader(
    "Upload an image or GeoTIFF",
    type=["jpg", "jpeg", "png", "tif", "tiff"]
)

# ---------------------------------------------------------
# IMAGE SMOOTHING TOOL
# ---------------------------------------------------------
if tool == "Image Smoothing":

    st.header("Image Smoothing Algorithm")

    st.write(
        "Applies a spatial averaging filter to each RGB channel to reduce noise "
        "while preserving overall image structure."
    )

    show_original = st.sidebar.checkbox(
        "Show original image",
        value=True
    )

    if uploaded is not None:
        try:
            with st.spinner("Running smoothing algorithm..."):
                fig_orig, fig_smooth = smooth_run(uploaded)

            if show_original:
                st.subheader("Original Image")
                st.pyplot(fig_orig)

            st.subheader("Smoothed Image")
            st.pyplot(fig_smooth)

        except Exception as e:
            st.error("Error running image smoothing.")
            st.exception(e)
    else:
        st.info("Upload an image to run the smoothing algorithm.")

# ---------------------------------------------------------
# TEMPERATURE ANALYSIS TOOL
# ---------------------------------------------------------
elif tool == "Surface Temperature Analysis":

    st.header("Surface Temperature Analysis")

    st.write(
        "Computes surface temperature (°F) from the LWIR band of a GeoTIFF "
        "and highlights regions exceeding a user-defined threshold."
    )

    threshold_f = st.sidebar.slider(
        "Temperature threshold (°F)",
        min_value=80.0,
        max_value=140.0,
        value=120.0,
        step=1.0
    )

    if uploaded is not None:
        try:
            with st.spinner("Computing surface temperature..."):
                fig, count, pct = temp_run(
                    uploaded,
                    threshold_f=threshold_f
                )

            st.subheader("Temperature Map")
            st.pyplot(fig)

            st.markdown(
                f"""
                **Pixels above {threshold_f:.1f}°F**  
                Count: **{count}**  
                Percentage: **{pct:.2f}%**
                """
            )

        except Exception as e:
            st.error("Error running temperature analysis.")
            st.exception(e)
    elif tool == "NDVI × Temperature (Integrated Analysis)":

        st.header("NDVI × Temperature — Integrated Analysis")

        st.write(
            "Aggregates NDVI and surface temperature into region-averages, computes covariance, "
            "and shows an RGB preview plus a scatter of region means."
        )

        n_regions = st.sidebar.slider(
            "Regions per axis",
            min_value=4,
            max_value=40,
            value=10,
            step=1
        )

        show_preview = st.sidebar.checkbox("Show RGB preview", value=True)

        if uploaded is not None:
            try:
                with st.spinner("Running integrated analysis..."):
                    results = integrated_run(uploaded, n_regions=n_regions, show_preview=show_preview)

                if results["rgb_fig"] is not None:
                    st.subheader("RGB Preview")
                    st.pyplot(results["rgb_fig"])

                st.subheader("NDVI vs Temperature (region means)")
                st.pyplot(results["scatter_fig"])

                st.markdown(
                    f"**Regions:** {n_regions} × {n_regions}  \n"
                    f"**Covariance (clean pairs):** {results['covariance_clean']:.4f}"
                )

            except Exception as e:
                st.error("Error running integrated analysis.")
                st.exception(e)
    else:
        st.info("Upload a GeoTIFF with the expected band ordering (NIR, Red, Green, Blue, LWIR).")


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown(
    "📎 **Source code available on GitHub**  \n"
    "_This application was built using Python, NumPy, rasterio, matplotlib, and Streamlit._"
)
