# app.py
import streamlit as st
from engineering_visualizations.modules.smoothing_algorithm import run

st.set_page_config(page_title="Engineering Visualizations", layout="wide")
st.title("Smoothing Algorithm — Interactive Demo")

# Sidebar controls
st.sidebar.header("Controls")
uploaded = st.sidebar.file_uploader(
    "Upload an image (JPEG/PNG/TIFF)",
    type=["jpg", "jpeg", "png", "tif", "tiff"]
)

show_original = st.sidebar.checkbox("Show original image", value=True)

# Main logic
if uploaded is not None:
    try:
        with st.spinner("Running smoothing algorithm..."):
            fig_orig, fig_smooth = run(uploaded)

        if show_original:
            st.subheader("Original")
            st.pyplot(fig_orig)

        st.subheader("Smoothed")
        st.pyplot(fig_smooth)

    except Exception as e:
        st.error("Error running smoothing algorithm.")
        st.exception(e)
else:
    st.info("Upload a file to run the smoothing algorithm.")
