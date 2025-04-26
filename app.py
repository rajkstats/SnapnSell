import streamlit as st
import os
from PIL import Image
import io
from io import BytesIO
import base64
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(f"OPENAI_API_KEY loaded: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"API Key: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else 'INVALID'}")

# Import custom modules
from ai_utils import analyze_image, estimate_price_fallback
from flyer_generator import create_flyer, image_to_base64
from share_utils import get_image_download_link, get_whatsapp_share_link
from image_gen_utils import generate_product_image
from marketplace_flyer import create_marketplace_flyer, format_price
from flyer_gen_api import generate_marketplace_flyer, build_custom_prompt

# Helper function to convert BytesIO to a file-like object for Streamlit
def uploaded_file_to_bytes(bytes_io, filename):
    class UploadedFile:
        def __init__(self, bytes_io, filename):
            self.bytes_io = bytes_io
            self.name = filename
        
        def getvalue(self):
            return self.bytes_io.getvalue()
            
        def read(self):
            return self.bytes_io.read()
    
    return UploadedFile(bytes_io, filename)

# Set page configuration
st.set_page_config(
    page_title="Snap & Sell Web",
    page_icon="📸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown(
    """
<style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        background-color: #008080;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #006666;
    }
    h1, h2, h3 {
        color: #008080;
    }
    .footer {
        margin-top: 3rem;
        text-align: center;
        color: #666;
        font-size: 0.8rem;
    }
    .upload-section {
        border: 2px dashed #008080;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    .price-input {
        font-size: 1.5rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True
)

# Initialize session state variables
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
    st.session_state.analysis_result = None
    st.session_state.flyer_image = None
    st.session_state.processing = False
    st.session_state.use_fallback = False
    st.session_state.last_fallback_state = False
    st.session_state.upload_key = 0
    st.session_state.use_api_flyer = True
    st.session_state.api_error = None
    st.session_state.flyer_displayed_inline = False
if 'upload_key' not in st.session_state:
    st.session_state.upload_key = 0
if 'use_fallback' not in st.session_state:
    st.session_state.use_fallback = False
if 'last_fallback_state' not in st.session_state:
    st.session_state.last_fallback_state = False
if 'image_source' not in st.session_state:
    st.session_state.image_source = None
if 'use_api_flyer' not in st.session_state:
    st.session_state.use_api_flyer = True

# App header
st.title("Snap & Sell Web")
st.subheader("AI-powered second-hand listing creator")
st.markdown("Turn a single photo into a polished listing flyer in under 30 seconds")

# Add a reset button in the top right
reset_col1, reset_col2 = st.columns([6, 1])
with reset_col2:
    if st.button("🔄 Reset", key="reset_btn"):
        # Reset all session state variables except API settings
        use_fallback = st.session_state.use_fallback
        use_api_flyer = st.session_state.use_api_flyer
        
        # Clear session state
        st.session_state.uploaded_image = None
        st.session_state.analysis_result = None
        st.session_state.flyer_image = None
        st.session_state.processing = False
        st.session_state.flyer_displayed_inline = False
        st.session_state.upload_key += 1  # Increment to force file uploader refresh
        
        # Restore API settings
        st.session_state.use_fallback = use_fallback
        st.session_state.use_api_flyer = use_api_flyer
        
        st.rerun()

# Main app layout
col1, col2 = st.columns([1, 1])

# Upload section
with col1:
    st.markdown("### 📸 Upload Item Photo or Generate One")
    if st.session_state.use_fallback:
        st.info("⚠️ Using offline mode due to API issues. The app will work with basic functionality.")
    
    # Create a placeholder for the image preview
    image_preview_placeholder = st.empty()
    
    # If there's no uploaded image, show the dotted border container
    if 'uploaded_image' not in st.session_state or st.session_state.uploaded_image is None:
        with image_preview_placeholder:
            st.markdown('<div class="upload-section" style="height: 200px; display: flex; justify-content: center; align-items: center;"><p style="color: #666;">Your image will appear here</p></div>', unsafe_allow_html=True)
    
    # Tabs for upload and generate
    upload_tab, generate_tab = st.tabs(["Upload Image", "Generate Image"])

    with upload_tab:
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"], key=f"file_uploader_{st.session_state.upload_key}")
        
        if uploaded_file is not None:
            try:
                # Read the image file
                image_bytes = uploaded_file.getvalue()
                image = Image.open(io.BytesIO(image_bytes))
                
                # Replace the dotted border with the actual image
                with image_preview_placeholder:
                    st.image(image, caption="Uploaded Image", use_column_width=True)
                
                # Store the uploaded image in session state
                st.session_state.uploaded_image = uploaded_file
                st.session_state.image_source = "upload"
                
                # Add a single Analyze Image button that works in both modes
                if st.button("Analyze Image", key="analyze_btn", type="primary"):
                    if not st.session_state.use_fallback:
                        with st.spinner("🔍 Analyzing your image with AI..."):
                            st.session_state.processing = True
                            st.session_state.analysis_result = analyze_image(image, use_fallback=st.session_state.use_fallback)
                            st.session_state.processing = False
                            st.rerun()
                    else:
                        # Fallback mode - use basic analysis
                        with st.spinner("🔍 Processing your image..."):
                            st.session_state.processing = True
                            st.session_state.analysis_result = estimate_price_fallback(image)
                            st.session_state.processing = False
                            st.rerun()
            except Exception as e:
                st.error(f"Error processing image: {e}")
                print(f"Error processing uploaded image: {e}")
                import traceback
                traceback.print_exc()

    with generate_tab:
        st.markdown("Let AI generate a product image based on your description")
        product_description = st.text_area("Describe the product", height=100, 
                                        placeholder="Example: A lightly used iPhone 13 Pro in silver color with minor scratches on the back")
        product_category = st.text_input("Product Category (optional)", 
                                        placeholder="Example: Smartphone, Furniture, Clothing")
        
        image_style = st.selectbox("Image Style", 
                                  options=["photorealistic", "product photography", "flat lay", "minimalist"], 
                                  index=0)
        
        if st.button("Generate Image", key="gen_img_btn"):
            if not product_description:
                st.warning("Please provide a product description")
            else:
                with st.spinner("🎨 Generating your product image with AI..."):
                    try:
                        generated_image = generate_product_image(product_description, product_category, image_style)
                        if generated_image:
                            # Replace the dotted border with the generated image
                            with image_preview_placeholder:
                                st.image(generated_image, caption="Generated Product Image", use_column_width=True)
                            
                            # Save the generated image to a BytesIO object
                            img_byte_arr = io.BytesIO()
                            generated_image.save(img_byte_arr, format='PNG')
                            img_byte_arr.seek(0)
                            
                            # Create a file-like object for Streamlit
                            generated_file = uploaded_file_to_bytes(img_byte_arr, "generated_image.png")
                            
                            # Store in session state
                            st.session_state.uploaded_image = generated_file
                            st.session_state.image_source = "generated"
                            
                            if st.button("Use This Image", key="use_gen_img"):
                                if not st.session_state.use_fallback:
                                    with st.spinner("🔍 Analyzing your image with AI..."):
                                        st.session_state.analysis_result = analyze_image(generated_image, 
                                                                                       use_fallback=st.session_state.use_fallback)
                                        st.rerun()
                                else:
                                    with st.spinner("🔍 Processing your image..."):
                                        st.session_state.analysis_result = estimate_price_fallback(generated_image)
                                        st.rerun()
                        else:
                            st.error("Failed to generate image. Please try again or use a different description.")
                    except Exception as e:
                        st.error(f"Error generating image: {e}")
                        print(f"Error in image generation: {e}")
                        import traceback
                        traceback.print_exc()

    # No need to close the div since we're handling it differently now

# Results and editing section
with col2:
    if st.session_state.analysis_result:
        st.markdown("### 📝 Edit Listing Details")
        
        # Get values from analysis result
        result = st.session_state.analysis_result
        
        # Create form fields for editing
        new_category = st.text_input("Category", value=result.get('category', ''), key="category_input")
        new_title = st.text_input("Title", value=result.get('title', ''), key="title_input")
        
        # Features as a text area with bullet points
        features_text = '\n'.join([f"- {f}" for f in result.get('features', [])])
        new_features_text = st.text_area("Features (one per line, starting with '-')", 
                                       value=features_text, 
                                       height=100,
                                       key="features_input")
        
        # Convert features text back to list
        new_features = [f.strip().lstrip('-').strip() for f in new_features_text.split('\n') if f.strip()]
        
        # Price with ₹ symbol
        price_value = result.get('price', '1000')
        new_price = st.text_input("Price (₹)", value=price_value, key="price_input")
        
        # Location
        new_location = st.text_input("Location", value=result.get('location', ''), key="location_input")
        
        # Add some spacing before the generate button
        st.markdown("<br>", unsafe_allow_html=True)

        # === Generate Flyer with OpenAI button ===
        if st.button("Generate Flyer with OpenAI", key="simple_generate_btn"):
            progress = st.empty()
            try:
                progress.info("🎨 Generating your professional flyer with OpenAI...")

                # Update analysis_result with edits
                st.session_state.analysis_result.update({
                    'title': new_title,
                    'category': new_category,
                    'features': new_features,
                    'price': new_price,
                    'location': new_location
                })

                # Build prompt and call API
                image = Image.open(st.session_state.uploaded_image)
                custom_prompt = build_custom_prompt(
                    title=new_title,
                    features=new_features,
                    price=new_price,
                    location=new_location,
                    category=new_category
                )
                
                # Use OpenAI API for flyer generation if enabled
                use_api = st.session_state.use_api_flyer
                
                # Show a spinner with appropriate message
                if use_api:
                    progress.info("🎨 Generating your professional flyer with OpenAI API...")
                else:
                    progress.info("🎨 Generating your flyer locally...")
                
                flyer = generate_marketplace_flyer(
                    image=image, 
                    custom_prompt=custom_prompt,
                    use_api=use_api
                )
                if not flyer:
                    raise ValueError("Received no image from generate_marketplace_flyer()")

                st.session_state.flyer_image = flyer
                # Mark that we've displayed the flyer inline
                st.session_state.flyer_displayed_inline = True
                progress.success("✅ Flyer generated successfully!")
                st.subheader("Your Generated Flyer")
                st.image(flyer, caption="Generated Marketplace Flyer", use_column_width=True)

                buf = io.BytesIO()
                flyer.save(buf, format="PNG")
                href = (
                    f'<a href="data:file/png;base64,{base64.b64encode(buf.getvalue()).decode()}" '
                    'download="marketplace_flyer.png">Download Flyer</a>'
                )
                st.markdown(href, unsafe_allow_html=True)

            except Exception as e:
                progress.error(f"❌ Error generating flyer: {e}")
                print("Traceback (flyer generation):")
                import traceback; traceback.print_exc()

# Display flyer outside editing if not inline
if st.session_state.flyer_image and not st.session_state.get('flyer_displayed_inline', False):
    st.subheader("Your Generated Flyer")
    st.image(st.session_state.flyer_image, caption="Generated Marketplace Flyer", use_column_width=True)
    buf = io.BytesIO()
    st.session_state.flyer_image.save(buf, format="PNG")
    href = f'<a href="data:file/png;base64,{base64.b64encode(buf.getvalue()).decode()}" download="marketplace_flyer.png">Download Flyer</a>'
    st.markdown(href, unsafe_allow_html=True)

# Footer with version info and credits
st.markdown(
    """
<div class="footer">
    <p>Snap & Sell Web - AI-powered second-hand listing creator</p>
    <p>Version 1.0.0 | © 2025 - All rights reserved</p>
    <p><small>Powered by OpenAI GPT-4o and GPT-Image-1</small></p>
</div>
""", unsafe_allow_html=True
)

# Sidebar controls
api_key = os.getenv("OPENAI_API_KEY")
use_fallback = st.sidebar.checkbox("Use offline mode (no API calls)", value=st.session_state.use_fallback, key="fallback_checkbox")
st.session_state.use_fallback = use_fallback

# Flyer generation method
st.sidebar.markdown("### Flyer Generation Method")
use_api_flyer = st.sidebar.checkbox("Use OpenAI API for flyer generation", value=st.session_state.use_api_flyer, key="api_flyer_checkbox")
st.session_state.use_api_flyer = use_api_flyer

if use_api_flyer:
    st.sidebar.info("Using OpenAI Image API (gpt-image-1) for flyer generation")
    if not api_key:
        st.sidebar.warning("OpenAI API key is required for API flyer generation")
else:
    st.sidebar.info("Using local flyer generator (no API calls)")

# === Sidebar: Update API Key ===
new_api_key = st.sidebar.text_input("Update OpenAI API Key", "", type="password")
if new_api_key and st.sidebar.button("Update API Key"):
    os.environ["OPENAI_API_KEY"] = new_api_key
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    lines = open(env_path).read().splitlines()
    with open(env_path, "w") as f:
        for line in lines:
            if line.startswith("OPENAI_API_KEY="):
                f.write(f'OPENAI_API_KEY="{new_api_key}"\n')
            else:
                f.write(line + "\n")
    try:
        from openai import OpenAI
        _ = OpenAI(api_key=new_api_key)
        st.sidebar.success("API key updated successfully!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error updating API key: {e}")

if not api_key and not use_fallback:
    st.sidebar.warning("OpenAI API key not found. Please add it to your .env file or use offline mode.")
    st.sidebar.code("OPENAI_API_KEY=your_api_key_here")
elif api_key and not use_fallback:
    masked = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else api_key
    st.sidebar.success("OpenAI API key found")
    st.sidebar.code(f"API Key: {masked}")
elif use_fallback:
    st.sidebar.info("Using offline mode - AI features will use basic estimation")

st.sidebar.title("How to Use")
st.sidebar.markdown("""
1. Upload a photo of your item
2. Click "Analyze & Create Flyer"
3. Edit details if needed
4. Download or share your listing
""")

st.sidebar.title("About")
st.sidebar.markdown("""
Snap & Sell Web turns a single photo into a polished listing flyer in under 30 seconds—complete with suggested price, catchy copy, and ready-to-share artwork.

Perfect for:
- Quick sales on Facebook Marketplace
- WhatsApp group listings
- Local classifieds
""")
