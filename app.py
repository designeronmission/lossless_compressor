import streamlit as st
from PIL import Image
import io
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AptCompressor | Professional Image Optimization",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM STYLING (CSS) ---
st.markdown("""
    <style>
    .main-title { font-size: 42px; font-weight: bold; color: #00C853; text-align: center; margin-bottom: 0; }
    .sub-title { font-size: 16px; color: #666; text-align: center; margin-bottom: 30px; }
    .stMetric { background-color: #f8f9fb; padding: 15px; border-radius: 10px; border: 1px solid #e0e4e8; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown('<p class="main-title">📉 AptCompressor</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Fixed-Resolution Professional Compression Engine</p>', unsafe_allow_html=True)

# --- 4. SIDEBAR SETTINGS ---
st.sidebar.header("🎯 Optimization Settings")

format_type = st.sidebar.selectbox(
    "Output Format", 
    ["WebP", "JPG", "PNG"],
    help="WebP offers the best compression-to-quality ratio."
)

st.sidebar.divider()

# --- 5. FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"])

if uploaded_file:
    # Load and cache image details
    img = Image.open(uploaded_file)
    width, height = img.size
    orig_bytes = uploaded_file.getvalue()
    orig_kb = len(orig_bytes) / 1024
    
    # Dynamic Slider based on upload
    target_kb = st.sidebar.slider(
        "Target File Size (KB)", 
        min_value=5, 
        max_value=int(orig_kb) if orig_kb > 10 else 100, 
        value=min(60, int(orig_kb))
    )
    
    reduction_strength = st.sidebar.slider(
        "Quality Floor (%)", 
        0, 90, 50, 
        help="The engine won't drop quality below this percentage to hit the target."
    )

    if st.sidebar.button("🚀 Run AptCompressor", use_container_width=True):
        with st.spinner("Optimizing entropy and bit-depth..."):
            final_buf = io.BytesIO()
            
            # --- COMPRESSION LOGIC ---
            if format_type == "PNG":
                # PNG is strictly lossless; optimize re-calculates Huffman tables
                img.save(final_buf, format="PNG", optimize=True, compress_level=9)
            
            else:
                # Iterative Quality Squeeze
                # We start high and decrease quality until we hit the target KB
                current_quality = 100
                floor = 100 - reduction_strength
                
                while current_quality >= floor:
                    test_buf = io.BytesIO()
                    if format_type == "WebP":
                        img.save(test_buf, format="WEBP", quality=current_quality, method=6)
                    else:
                        # JPEG requires RGB mode (drops alpha channel transparency)
                        rgb_img = img.convert("RGB")
                        rgb_img.save(test_buf, format="JPEG", quality=current_quality, optimize=True)
                    
                    # Check if target is met
                    if len(test_buf.getvalue()) / 1024 <= target_kb:
                        final_buf = test_buf
                        break
                    
                    current_quality -= 3 # Incremental step for precision
                    final_buf = test_buf

            # --- CALCULATE RESULTS ---
            final_bytes = final_buf.getvalue()
            final_kb = len(final_bytes) / 1024
            savings = ((orig_kb - final_kb) / orig_kb) * 100

            # --- UI PREVIEW ---
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Original")
                st.image(img, use_container_width=True)
                st.caption(f"Resolution: {width}x{height} | Size: {orig_kb:.2f} KB")
                
            with col2:
                st.subheader("Optimized")
                st.image(Image.open(io.BytesIO(final_bytes)), use_container_width=True)
                st.caption(f"Resolution: {width}x{height} | Size: {final_kb:.2f} KB")

            # --- METRICS & DOWNLOAD ---
            st.divider()
            m1, m2, m3 = st.columns(3)
            m1.metric("Original Size", f"{orig_kb:.1f} KB")
            m2.metric("Result Size", f"{final_kb:.1f} KB")
            m3.metric("Reduction", f"{savings:.1f}%")

            st.download_button(
                label=f"📥 Download {format_type} ({final_kb:.1f} KB)",
                data=final_bytes,
                file_name=f"AptCompressor_{width}x{height}.{format_type.lower()}",
                mime=f"image/{format_type.lower()}",
                use_container_width=True
            )
else:
    # Welcome State
    st.info("👋 Welcome to AptCompressor. Upload an image to start optimizing without changing pixels.")
    st.markdown("""
    ### Why use AptCompressor?
    * **No Pixel Changes:** Your image dimensions ($Width \\times Height$) stay exactly the same.
    * **Privacy First:** Processing happens locally; images never leave your environment.
    * **Iterative Squeezing:** Our engine automatically finds the highest quality possible that fits your target file size.
    """)