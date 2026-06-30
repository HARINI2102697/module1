!pip install streamlit
import streamlit as st
import anthropic
import base64
from PIL import Image
import io
# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VisionAI – Image Description Tool",
    page_icon=" ",
    layout="centered"
)
# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');
html, body, [class*="css"] {
font-family: 'Inter', sans-serif;
background-color: #0D0D0D;
color: #E8E8E8;
}
.stApp {
background-color: #0D0D0D;
}
/* Header */
.hero-title {
font-family: 'Space Grotesk', sans-serif;
font-size: 2.8rem;
font-weight: 700;
color: #FFFFFF;
letter-spacing: -1px;
line-height: 1.1;
}
.hero-accent {
color: #7C6FFF;
}
.hero-sub {
font-size: 1rem;

color: #888;
margin-top: 0.5rem;
font-weight: 300;
}
/* Card container */
.result-card {
background: #161616;
border: 1px solid #2A2A2A;
border-radius: 12px;
padding: 1.5rem;
margin-top: 1.2rem;
}
.result-label {
font-family: 'Space Grotesk', sans-serif;
font-size: 0.75rem;
font-weight: 600;
color: #7C6FFF;
letter-spacing: 2px;
text-transform: uppercase;
margin-bottom: 0.6rem;
}
.result-text {
font-size: 1rem;
color: #D4D4D4;
line-height: 1.75;
}
/* Divider */
.divider {
border: none;
border-top: 1px solid #222;
margin: 1.5rem 0;
}
/* Buttons */
.stButton > button {
background: #7C6FFF !important;
color: white !important;
border: none !important;
border-radius: 8px !important;
font-family: 'Space Grotesk', sans-serif !important;
font-weight: 600 !important;
font-size: 0.95rem !important;
padding: 0.6rem 2rem !important;

transition: opacity 0.2s !important;
width: 100%;
}
.stButton > button:hover {
opacity: 0.85 !important;
}
/* Select box */
.stSelectbox label {
color: #888 !important;
font-size: 0.85rem !important;
}
/* File uploader */
.stFileUploader {
background: #161616 !important;
border: 1.5px dashed #333 !important;
border-radius: 10px !important;
}
/* Spinner */
.stSpinner > div {
border-top-color: #7C6FFF !important;
}
/* Badge */
.mode-badge {
display: inline-block;
background: #1A1A2E;
color: #7C6FFF;
border: 1px solid #7C6FFF44;
border-radius: 20px;
font-size: 0.75rem;
font-weight: 600;
padding: 2px 12px;
margin-bottom: 1.2rem;
}
</style>
""", unsafe_allow_html=True)
# ─── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 1.5rem 0 0.5rem 0;">
<div class="hero-title">Vision<span class="hero-accent">AI</span></div>
<div class="hero-sub">Upload any image → get an instant AI-powered description</div>
</div>

<hr class="divider">
""", unsafe_allow_html=True)
# ─── Sidebar / Settings ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Settings")
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    st.markdown("---")
    description_mode = st.selectbox(
        "Description Style",
        ["Detailed Analysis", "Simple & Short", "Technical (for developers)", "Creative / Poetic"]
    )
    language = st.selectbox("Output Language", ["English", "Tamil", "Hindi", "French", "Spanish"])
    st.markdown("---")
    st.markdown("<small style='color:#555;'>Powered by Claude claude-sonnet-4-6 Vision</small>", unsafe_allow_html=True)
# ─── Mode prompt map ─────────────────────────────────────────────────────────────
MODE_PROMPTS = {
    "Detailed Analysis": (
        "Describe this image in thorough detail. Include: what objects/people are present, "
        "colors, mood, composition, background, any text visible, and any interesting observations."
    ),
    "Simple & Short": (
        "Give a brief, clear 2-3 sentence description of this image. Keep it simple and easy to understand."
    ),
    "Technical (for developers)": (
        "Provide a technical description of this image suitable for alt-text or accessibility metadata. "
        "List main subjects, spatial layout, dominant colors (hex if possible), and any UI elements if present."
    ),
    "Creative / Poetic": (
        "Describe this image in a creative, evocative, and poetic way. "
        "Use vivid language and metaphors. Make it feel like a piece of micro-fiction or a poem."
    )
}
LANG_INSTRUCTION = {
    "English": "",
    "Tamil": " Respond entirely in Tamil.",
    "Hindi": " Respond entirely in Hindi.",
    "French": " Respond entirely in French.",
    "Spanish": " Respond entirely in Spanish."
}
# ─── Main Upload Area ────────────────────────────────────────────────────────────
st.markdown(f'<div class="mode-badge">Mode: {description_mode}</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(

    "Drop your image here or click to browse",
    type=["jpg", "jpeg", "png", "webp", "gif"],
    label_visibility="visible"
)
if uploaded_file:
    # Show preview
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_btn = st.button(" Describe This Image")
    if analyze_btn:
        if not api_key:
            st.error(" Please enter your Anthropic API key in the sidebar.")
        else:
            with st.spinner("Analyzing image..."):
                try:
                    # Convert image to base64
                    buf = io.BytesIO()
                    fmt = image.format if image.format else "JPEG"
                    image.save(buf, format=fmt)
                    img_bytes = buf.getvalue()
                    img_b64 = base64.standard_b64encode(img_bytes).decode("utf-8")
                    # Media type
                    media_map = {
                        "JPEG": "image/jpeg", "JPG": "image/jpeg",
                        "PNG": "image/png", "WEBP": "image/webp", "GIF": "image/gif"
                    }
                    media_type = media_map.get(fmt.upper(), "image/jpeg")
                    # Build prompt
                    prompt = MODE_PROMPTS[description_mode] + LANG_INSTRUCTION[language]
                    # Call Anthropic API
                    client = anthropic.Anthropic(api_key=api_key)
                    response = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=1024,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {

                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": media_type,
                                            "data": img_b64
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": prompt
                                    }
                                ]
                            }
                        ]
                    )
                    description = response.content[0].text
                    # Display result
                    st.markdown(f"""
<div class="result-card">
<div class="result-label">AI Description · {description_mode}</div>
<div class="result-text">{description}</div>
</div>
""", unsafe_allow_html=True)
                    # Copy-friendly text area
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.text_area(" Copy Description", value=description, height=150)
                except anthropic.AuthenticationError:
                    st.error(" Invalid API key. Please check your Anthropic API key.")
                except Exception as e:
                    st.error(f" Error: {str(e)}")
else:
    st.markdown("""
<div style="text-align:center; color:#444; padding: 3rem 0; font-size: 0.9rem;">
No image uploaded yet — drop one above to get started
</div>
""", unsafe_allow_html=True)
