import streamlit as st
from PIL import Image, ImageDraw

def app():
    # Function to round the corners of the image
    def round_corners(image, radius=30):
        width, height = image.size
        rounded_mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(rounded_mask)
        draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)

        # Create a new image with transparency and paste the original image onto it
        rounded_image = Image.new('RGBA', (width, height))
        rounded_image.paste(image, (0, 0), rounded_mask)
        return rounded_image

    # Centered Hero Section
    import os
    current_dir = os.path.dirname(__file__)
    image_path = os.path.join(current_dir, 'images', 'CancerDetective.png')
    try:
        image = Image.open(image_path)
        # Higher aspect ratio for hero look
        resized_image = image.resize((1400, 450))
        rounded_image = round_corners(resized_image, radius=30)
        st.image(rounded_image, use_column_width=True)
    except Exception as e:
        st.error(f"Error loading hero image: {e}")

    # Main Intro Card
    st.markdown("""
        <div class="main">
            <h1 class="title-font" style="font-size: 2.8rem; margin-bottom: 20px;">🔬 Welcome to Cancer Detective</h1>
            <p>
                Our web app harnesses the power of advanced <b>Artificial Intelligence</b> 🧠 to assist in the early detection of cancer. 
                Focused on lung and skin cancers, Cancer Detective analyzes complex medical images 📷 to provide rapid, reliable diagnostic insights.
            </p>
            <p>
                By bridging the gap between cutting-edge ML research and clinical support, we aim to empower 👩‍⚕️👨‍⚕️ and patients 🧑‍⚕️ 
                with tools that make early detection accessible 🌍, fast ⚡, and accurate 🎯.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Key Features Section using a grid-like layout with custom cards
    st.markdown('<h2 class="sub-title" style="text-align: center; margin-top: 50px;">🌟 Core Capabilities</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="feature-box">
                <h3>🎯 Precision Detection</h3>
                <p>Advanced Deep Learning architectures (CNNs) trained on vast medical datasets to identify anomalies with clinical-grade accuracy.</p>
            </div>
            <div class="feature-box">
                <h3>⚡ Real-time Analysis</h3>
                <p>Instantaneous processing and visualization of results, reducing waiting times for critical diagnostic feedback.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class="feature-box">
                <h3>🩺 Multi-Cancer Support</h3>
               <p>Comprehensive screening toolkit for Lung (Tissue) and Skin (Lesions) in a single unified interface.</p>
            </div>
            <div class="feature-box">
                <h3>🖱️ Professional Dashboards</h3>
                <p>An intuitive interface designed for focus, minimal clutter, and maximum accessibility for medical staff.</p>
            </div>
        """, unsafe_allow_html=True)

    # Bottom Call to Action or Footer-like info
    st.markdown("""
        <div style="text-align: center; margin-top: 40px; padding: 20px; color: #64748b;">
            <p>❤️ Early detection saves lives. Start your analysis on the <b>Detection</b> page.</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    app()
