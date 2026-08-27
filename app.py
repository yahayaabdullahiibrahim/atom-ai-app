import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import PyPDF2
import docx
import io
import urllib.parse
import uuid
import random

# 1. Page Configuration
st.set_page_config(
    page_title="ATOM AI - Modern Workspace", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Advanced Modern Dark Theme CSS (Fixing Text Visibility)
st.markdown("""
    <style>
    /* Global Styles & Text Visibility Fix */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0B0E14; /* Darker Background */
        font-family: 'Space Grotesk', sans-serif;
        color: #E2E8F0; /* Off-White Text globally */
    }
    
    /* Ensuring all generic Streamlit texts are visible */
    .stText, .stMarkdown, p, span, label {
        color: #E2E8F0 !important;
    }

    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #111420 0%, #1A1F35 100%);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #2D3748;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.5);
        text-align: center;
    }
    
    .main-title {
        color: #FFFFFF;
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #A5B4FC 0%, #FFFFFF 50%, #A5B4FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-subtitle {
        color: #94A3B8;
        font-size: 1.1rem;
        margin-top: 10px;
        font-weight: 400;
    }

    /* Modern Badge */
    .badge {
        background: rgba(99, 102, 241, 0.1);
        color: #A5B4FC;
        padding: 5px 15px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(99, 102, 241, 0.3);
        display: inline-block;
        margin-bottom: 15px;
        letter-spacing: 1px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: #111420;
        padding: 10px;
        border-radius: 15px;
        border: 1px solid #2D3748;
        justify-content: center;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 10px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 1rem;
        border: none;
        padding: 0px 25px;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #FFFFFF;
        background-color: rgba(255, 255, 255, 0.05);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 5px 15px rgba(79, 70, 229, 0.4);
    }

    /* Sidebar Custom Styling */
    section[data-testid="stSidebar"] {
        background-color: #07090D;
        border-right: 1px solid #2D3748;
    }

    /* Modern Cards & Containers */
    .studio-card {
        background-color: #111420;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #2D3748;
        margin-bottom: 20px;
        color: #E2E8F0;
    }
    
    .image-container {
        background-color: #07090D;
        padding: 10px;
        border-radius: 15px;
        border: 2px dashed #3A445E;
        text-align: center;
        min-height: 400px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #94A3B8;
    }

    /* Buttons Styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        padding: 12px 20px;
        font-weight: 700;
        font-size: 1rem;
        border-radius: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(79, 70, 229, 0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.5);
    }
    
    /* Inputs Styling - Crucial for dark mode visibility */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #07090D !important;
        border: 1px solid #3A445E !important;
        color: #FFFFFF !important; /* White text inside inputs */
        border-radius: 10px !important;
        padding: 12px !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }
    
    /* Fixing Chat Input kalar rubutu */
    [data-testid="stChatInput"] textarea {
        color: #FFFFFF !important;
        background-color: #111420 !important;
        border: 1px solid #3A445E !important;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Session State Storage Initialization
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {"title": "Sabuwar Hira", "messages": []}
    st.session_state.current_chat_id = new_id

def start_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {"title": "Sabuwar Hira", "messages": []}
    st.session_state.current_chat_id = new_id

# 4. Main Header Section
st.markdown("""
    <div class="main-header">
        <div class="badge">ATOM NEXT-GEN WORKSPACE</div>
        <div class="main-title">🤖 ATOM AI Pro</div>
        <div class="main-subtitle">Ingantaccen tsarin AI na zamani domin hira, takardu, bincikar hotuna, da zane-zane na kwararru.</div>
    </div>
""", unsafe_allow_html=True)

# 5. Sidebar Configuration & Chat History
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>⚙️ Saituna</h2>", unsafe_allow_html=True)
    api_key = st.text_input("🔑 Saka Gemini API Key:", type="password", help="Sami API key daga Google AI Studio")
    st.markdown("---")
    
    if st.button("➕ Sabuwar Hira (New Chat)", use_container_width=True):
        start_new_chat()
        st.rerun()

    st.markdown("<h3 style='color: #94A3B8;'>💬 Saved Topics</h3>", unsafe_allow_html=True)
    
    chat_ids = list(st.session_state.chats.keys())
    for cid in reversed(chat_ids):
        chat_data = st.session_state.chats[cid]
        title = chat_data["title"]
        
        if cid == st.session_state.current_chat_id:
            button_label = f"💬  {title}"
        else:
            button_label = f"📁 {title}"
            
        if st.button(button_label, key=f"btn_{cid}", use_container_width=True):
            st.session_state.current_chat_id = cid
            st.rerun()

# 6. Main Application Logic
if api_key:
    # Ensuring API Key has api_key parameter explicitly for the 401 error fix
    clean_api_key = api_key.strip()
    client = genai.Client(api_key=clean_api_key)
    
    system_prompt = """
    Sunanka ATOM Pro. Kai gwanin AI ne mai matukar basira da iyawa.
    Amsoshinka su kasance na kwararru, a tsara, masu kyawun fasali da girmamawa cikin harshen Hausa ko Turanci.
    """

    current_id = st.session_state.current_chat_id
    current_messages = st.session_state.chats[current_id]["messages"]

    tab1, tab2, tab3 = st.tabs(["💬 Hira & Takardu", "🖼️ Bincikar Hoto", "🎨 ATOM Image Studio Pro"])

    # ---------------- TAB 1: CHAT & DOCUMENTS ----------------
    with tab1:
        col1, col2 = st.columns([1, 2], gap="large")
        
        with col1:
            st.markdown("<div class='studio-card'><h5>📄 Loda Takarda<h5>", unsafe_allow_html=True)
            uploaded_doc = st.file_uploader("Saka Fayil (PDF, DOCX, TXT):", type=["pdf", "docx", "txt"])
            st.markdown("</div>", unsafe_allow_html=True)
            doc_text = ""
            
            if uploaded_doc:
                if uploaded_doc.type == "application/pdf":
                    reader = PyPDF2.PdfReader(uploaded_doc)
                    for page in reader.pages:
                        doc_text += page.extract_text() or ""
                elif uploaded_doc.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    doc = docx.Document(uploaded_doc)
                    for para in doc.paragraphs:
                        doc_text += para.text + "\n"
                elif uploaded_doc.type == "text/plain":
                    doc_text = str(uploaded_doc.read(), "utf-8")
                    
                st.success("✅ An karanta takardar!")

        with col2:
            st.markdown("##### 💬 Dandalin Hira")
            
            for msg in current_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if user_input := st.chat_input("Rubuta sakonka a nan..."):
                current_messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)

                if len(current_messages) == 1:
                    topic_title = user_input[:25] + "..." if len(user_input) > 25 else user_input
                    st.session_state.chats[current_id]["title"] = topic_title

                full_prompt = user_input
                if doc_text:
                    full_prompt = f"Bisa labarin/bayanin da ke cikin wannan takardar:\n\n{doc_text[:4000]}\n\nAmsa wannan tambayar: {user_input}"

                with st.chat_message("assistant"):
                    with st.spinner("ATOM Pro yana tunani..."):
                        try:
                            # Fixed model to gemini-3.6-flash to avoid 404 error
                            response = client.models.generate_content(
                                model='gemini-3.6-flash',
                                contents=full_prompt,
                                config=types.GenerateContentConfig(
                                    system_instruction=system_prompt,
                                ),
                            )
                            st.markdown(response.text)
                            current_messages.append({"role": "assistant", "content": response.text})
                            st.rerun()
                        except Exception as e:
                            # Fallback error handling with a visible warning box
                            st.warning(f"Kuskure ya faru: {e}. Da fatan duba idan API Key dinka mai aiki ne ko ka sake gwadawa.")

    # ---------------- TAB 2: IMAGE VISION ----------------
    with tab2:
        st.markdown("### 🖼️ Bincikar Hoto (Vision)")
        
        col_img1, col_img2 = st.columns([1, 1], gap="large")
        
        with col_img1:
            st.markdown("<div class='studio-card'>", unsafe_allow_html=True)
            uploaded_image = st.file_uploader("Loda hoto...", type=["jpg", "jpeg", "png"], key="vision_uploader")
            if uploaded_image:
                img = Image.open(uploaded_image)
                st.image(img, caption="Hoton da ka loda", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_img2:
            image_prompt = st.text_area("Tambayarka game da hoton:", "Yi mini bayani daki-daki game da wannan hoton da Hausa.")
            
            if uploaded_image and st.button("🔍 Fara Binciken Hoto"):
                with st.spinner("ATOM Pro yana nazarin hoton..."):
                    try:
                        # fixed model to gemini-3.6-flash
                        response = client.models.generate_content(
                            model='gemini-3.6-flash',
                            contents=[img, image_prompt],
                        )
                        st.markdown("### 🤖 Sakamakon ATOM Pro:")
                        st.info(response.text)
                    except Exception as e:
                        st.warning(f"Kuskure: {e}")

    # ---------------- TAB 3: MODERN IMAGE GENERATION STUDIO PRO ----------------
    with tab3:
        st.markdown("<h2 style='text-align: center; color: white; margin-bottom: 5px;'>🎨 ATOM Image Studio Pro</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94A3B8; margin-bottom: 30px;'>Zana hotuna masu inganci (HD) ta amfani da fasahar AI ta zamani.</p>", unsafe_allow_html=True)
        
        col_studio1, col_studio2 = st.columns([1, 2], gap="large")
        
        # Left Panel: Controls
        with col_studio1:
            st.markdown("<div class='studio-card'>", unsafe_allow_html=True)
            st.markdown("<h5 style='color: white; margin-top: 0;'>📝 1. Bayyana Hotonko</h5>", unsafe_allow_html=True)
            gen_prompt = st.text_area(
                "Prompt (Zaka iya rubutawa da Hausa):", 
                "Toyota Land Cruiser Prado 2024 driving through sand dunes in Sahara desert, sunset background, highly detailed, 8k resolution, photorealistic",
                height=150,
                placeholder="Rubuta abin da kake son gani..."
            )
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='studio-card'>", unsafe_allow_html=True)
            st.markdown("<h5 style='color: white; margin-top: 0;'>⚙️ 2. Saituna & Salo</h5>", unsafe_allow_html=True)
            
            style_option = st.selectbox(
                "🎨 Salo (Style):",
                ["Photorealistic (Kamar Na Gaske)", "Anime / Cartoon", "3D Digital Art", "Cinematic Movie", "Cyberpunk / Futuristic"]
            )
            
            aspect_ratio = st.radio(
                "📐 Girman Hoto (Aspect Ratio):",
                ["Square (1:1)", "Portrait (9:16)", "Landscape (16:9)"],
                horizontal=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

            # Generate Button
            generate_btn = st.button("✨ Zana Hoton (Generate HD)")

        # Right Panel: Display
        with col_studio2:
            st.markdown("<h5 style='color: white; margin-bottom: 10px;'>🖼️ Sakamakon Zane</h5>", unsafe_allow_html=True)
            image_placeholder = st.empty()
            
            # Default placeholder state with dark mode visible text
            with image_placeholder.container():
                st.markdown("""
                    <div class="image-container">
                        <div style="text-align: center;">
                            <div style="font-size: 4rem; margin-bottom: 20px;">🎨</div>
                            <span style="color: #94A3B8;">Hotonka zai fito a nan...<br>Cika bayani a gefen hagu sannan ka danna 'Zana Hoton'.</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Dimension Mapping
        dimensions = {"Square (1:1)": (1024, 1024), "Portrait (9:16)": (720, 1280), "Landscape (16:9)": (1280, 720)}
        width, height = dimensions[aspect_ratio]

        # Execution Logic
        if generate_btn:
            with st.spinner("🚀 ATOM Pro yana canza bayaninka zuwa zane..."):
                
                # Translation is needed for Pollinations to work perfectly
                try:
                    translation_res = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=f"Translate this Hausa prompt to English for image generation, focusing on visual details: '{gen_prompt}'. Only return the translated English text."
                    )
                    english_prompt = translation_res.text.strip()
                except Exception:
                    english_prompt = gen_prompt # Fallback
                
                # Dynamic Style Modifiers
                style_modifiers = {
                    "Photorealistic (Kamar Na Gaske)": "photorealistic, 8k resolution, ultra detailed, realistic lighting, sharp focus",
                    "Anime / Cartoon": "vibrant anime style, detailed digital illustration, aesthetic colors",
                    "3D Digital Art": "octane render, highly detailed 3d model, smooth lighting, trendy art",
                    "Cinematic Movie": "cinematic dramatic lighting, movie shot scene, masterpiece, highly texture",
                    "Cyberpunk / Futuristic": "cyberpunk style, neon lights, futuristic cityscape background, highly detailed"
                }
                
                # Auto-enhance prompt for Pollinations
                final_prompt = f"{english_prompt}, {style_modifiers[style_option]}"
                
                # Update placeholder to showing loading state
                image_placeholder.markdown("""
                    <div class="image-container">
                        <div style="text-align: center;">
                            <div style="font-size: 3rem; margin-bottom: 20px;">🚀</div>
                            <span style="color: #A5B4FC;">Injin AI yana hada hoton...<br>Da fatan a jira dakika kadan.</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Use direct rendering engine for reliability and clarity
                # Added random seed to ensure new images on generate button click
                random_seed = random.randint(1000, 999999)
                encoded_prompt = urllib.parse.quote(final_prompt)
                
                # Modern Flux Realism Model URL for Pollinations (High Quality)
                direct_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={random_seed}&model=flux-realism&nologo=true"
                
                try:
                    # Clear loading and show image inside a visible studio card
                    image_placeholder.empty()
                    with image_placeholder.container():
                        st.markdown("<div class='studio-card'>", unsafe_allow_html=True)
                        st.image(direct_url, caption=f"Sakamako: {gen_prompt}", use_container_width=True)
                        st.success("✅ An gama zana hoton cikin nasara!")
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                except Exception as e:
                    st.warning(f"Kuskure wajen nuna hoto: {e}")

else:
    # Error box with visible white text
    st.markdown("""
        <div style="background-color: #7C3AED; color: white; padding: 20px; border-radius: 12px; text-align: center; font-weight: bold; margin-bottom: 20px;">
            ⚠️ Da fatan za ka saka Gemini API Key ɗinka a gefen hagu (Sidebar) domin kunna ATOM AI Pro.
        </div>
    """, unsafe_allow_html=True)
