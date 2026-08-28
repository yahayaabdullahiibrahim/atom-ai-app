import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import PyPDF2
import docx
import urllib.parse
import uuid
import random
import time

# 1. Page Configuration
st.set_page_config(
    page_title="Gemini Ultra - ATOM Studio", 
    page_icon="✨", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Modern Gemini-Style Dark Theme CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0E131F;
        font-family: 'Google Sans', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #E3E3E3;
    }

    /* Ambient Gemini Glow Effect */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: -150px;
        left: 30%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(66,133,244,0.15) 0%, rgba(155,114,203,0.1) 40%, rgba(0,0,0,0) 70%);
        filter: blur(80px);
        z-index: 0;
        pointer-events: none;
    }

    /* Gemini Header Banner */
    .gemini-header {
        text-align: center;
        padding: 20px 0 30px 0;
    }

    .gemini-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4285F4 0%, #9B72CB 50%, #D96570 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }

    .gemini-subtitle {
        color: #C4C7C5;
        font-size: 1.1rem;
        font-weight: 400;
    }

    /* Gemini Card Containers */
    .gemini-card {
        background: #1E1F20;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    /* Tabs Styling - Gemini Style */
    .stTabs [data-baseweb="tab-list"] {
        background: #131722;
        padding: 6px;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        gap: 8px;
        display: flex;
        justify-content: center;
        max-width: 800px;
        margin: 0 auto 25px auto;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 20px;
        color: #C4C7C5;
        font-weight: 500;
        padding: 10px 24px;
        border: none;
        transition: all 0.2s ease;
        font-size: 0.95rem;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #FFFFFF;
        background: rgba(255, 255, 255, 0.05);
    }

    .stTabs [aria-selected="true"] {
        background: #282A2C !important;
        color: #A8C7FA !important;
        border: 1px solid rgba(168, 199, 250, 0.2) !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }

    /* Custom Input Controls */
    .stTextArea textarea, .stTextInput input, .stSelectbox select {
        background-color: #1E1F20 !important;
        border: 1px solid #444746 !important;
        color: #E3E3E3 !important;
        border-radius: 12px !important;
    }

    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #A8C7FA !important;
        box-shadow: 0 0 0 1px #A8C7FA !important;
    }

    /* Pill Action Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #0B57D0 0%, #1B6EF3 100%);
        color: #FFFFFF;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        border-radius: 24px;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(11, 87, 208, 0.3);
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #1B6EF3 0%, #0B57D0 100%);
        box-shadow: 0 4px 12px rgba(11, 87, 208, 0.5);
        transform: translateY(-1px);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #131722;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. State Management
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {"title": "Sabuwar Hira", "messages": []}
    st.session_state.current_chat_id = new_id

if "gallery" not in st.session_state:
    st.session_state.gallery = []

def start_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {"title": "Sabuwar Hira", "messages": []}
    st.session_state.current_chat_id = new_id

# Safe API Engine Error Handler
def safe_generate_content(client, contents, model='gemini-3.6-flash', max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            res = client.models.generate_content(
                model=model,
                contents=contents
            )
            return res.text, None
        except Exception as e:
            err_msg = str(e)
            if any(code in err_msg for code in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED"]):
                if attempt < max_retries:
                    time.sleep(3)
                    continue
                return None, "⚠️ Google Server yana da cunkoso ko kuma iyakokin amfaninka na rana sun cika. Da fatan sake gwadawa daga baya."
            elif any(code in err_msg for code in ["401", "UNAUTHENTICATED"]):
                return None, "🔑 API Key dinka ba ya aiki. Da fatan sake shigar da ingantaccen Gemini API Key."
            else:
                return None, f"Kuskure: {err_msg}"

# 4. Gemini Top Header
st.markdown("""
    <div class="gemini-header">
        <div class="gemini-title">✨ Gemini Ultra</div>
        <div class="gemini-subtitle">ATOM AI Suite • Hira, Nazarin Hotuna, da Ƙirƙirar Hotuna</div>
    </div>
""", unsafe_allow_html=True)

# 5. Sidebar Navigation
with st.sidebar:
    st.markdown("<h3 style='color: #E3E3E3;'>⚙️ Control Panel</h3>", unsafe_allow_html=True)
    api_key = st.text_input("🔑 Google Gemini API Key:", type="password", help="Saka API key dinka daga Google AI Studio")
    st.markdown("---")
    
    if st.button("➕ Sabuwar Hira (New Chat)", use_container_width=True):
        start_new_chat()
        st.rerun()

    st.markdown("<h4 style='color: #C4C7C5; margin-top: 15px;'>💬 Tsoffin Hirarraki</h4>", unsafe_allow_html=True)
    for cid in reversed(list(st.session_state.chats.keys())):
        chat_data = st.session_state.chats[cid]
        label = f"💬 {chat_data['title']}" if cid == st.session_state.current_chat_id else f"📁 {chat_data['title']}"
        if st.button(label, key=f"sidebar_btn_{cid}", use_container_width=True):
            st.session_state.current_chat_id = cid
            st.rerun()

# 6. Main Core Engine
if api_key:
    clean_api_key = api_key.strip()
    client = genai.Client(api_key=clean_api_key)
    current_id = st.session_state.current_chat_id
    current_messages = st.session_state.chats[current_id]["messages"]

    # Gemini Style Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Chat & Context", 
        "👁️ Gemini Vision", 
        "🎨 Imagen Studio", 
        "🖼️ Gallery"
    ])

    # ---------------- TAB 1: CHAT & CONTEXT ----------------
    with tab1:
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.markdown("<div class='gemini-card'><h5>📄 Loda Takarda (Document Context)</h5>", unsafe_allow_html=True)
            uploaded_doc = st.file_uploader("Sanya PDF, DOCX, ko TXT", type=["pdf", "docx", "txt"])
            st.markdown("</div>", unsafe_allow_html=True)
            doc_text = ""
            if uploaded_doc:
                try:
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
                    st.success("✅ An karanta takardarku cikin nasara!")
                except Exception as e:
                    st.error(f"Kuskure: {e}")

        with col2:
            for msg in current_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if user_input := st.chat_input("Yaya zan iya taimaka muku a yau?"):
                current_messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)

                if len(current_messages) == 1:
                    st.session_state.chats[current_id]["title"] = user_input[:22] + "..."

                full_prompt = user_input
                if doc_text:
                    full_prompt = f"Bisa labarin/bayanin da ke cikin wannan takardar:\n{doc_text[:4000]}\n\nAmsa wannan tambayar: {user_input}"

                with st.chat_message("assistant"):
                    with st.spinner("Gemini yana tunani..."):
                        response_text, error = safe_generate_content(client, full_prompt)
                        if response_text:
                            st.markdown(response_text)
                            current_messages.append({"role": "assistant", "content": response_text})
                            st.rerun()
                        else:
                            st.warning(error)

    # ---------------- TAB 2: GEMINI VISION ----------------
    with tab2:
        col_v1, col_v2 = st.columns([1, 1], gap="large")
        with col_v1:
            st.markdown("<div class='gemini-card'>", unsafe_allow_html=True)
            uploaded_image = st.file_uploader("Loda hoto domin bincike:", type=["jpg", "jpeg", "png"])
            if uploaded_image:
                img = Image.open(uploaded_image)
                st.image(img, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_v2:
            image_prompt = st.text_area("Tambayarku akan hoton:", "Yi mini cikakken bayani akan abubuwan da ke cikin wannan hoton.")
            if uploaded_image and st.button("🔍 Binciki Hoton"):
                with st.spinner("Gemini Vision yana bincike..."):
                    response_text, error = safe_generate_content(client, [img, image_prompt])
                    if response_text:
                        st.info(response_text)
                    else:
                        st.warning(error)

    # ---------------- TAB 3: IMAGEN STUDIO ----------------
    with tab3:
        st.markdown("<h3 style='color: #E3E3E3; text-align: center; margin-bottom: 20px;'>🎨 Imagen AI Generator</h3>", unsafe_allow_html=True)
        
        col_st1, col_st2 = st.columns([1, 1.2], gap="large")

        with col_st1:
            st.markdown("<div class='gemini-card'>", unsafe_allow_html=True)
            gen_prompt = st.text_area("Bayanin Hoto (Prompt):", "Toyota Land Cruiser Prado 2024 in Sahara desert, cinematic lighting, 8k render, hyperrealistic", height=120)
            
            style = st.selectbox("🎨 Salo (Art Style):", ["Photorealistic (Na Gaske)", "3D Render", "Anime / Art", "Cyberpunk", "Cinematic Dark"])
            ratio = st.radio("📐 Formats (Aspect Ratio):", ["1:1 (Square)", "16:9 (Landscape)", "9:16 (Portrait)"], horizontal=True)
            
            generate_btn = st.button("✨ Zana Hoto", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_st2:
            st.markdown("<div class='gemini-card' style='text-align: center;'>", unsafe_allow_html=True)
            image_placeholder = st.empty()
            image_placeholder.markdown("""
                <div style="padding: 70px 20px; color: #8E918F;">
                    <div style="font-size: 3rem; margin-bottom: 10px;">✨</div>
                    Sakamakon hoton zai bayyana a nan.
                </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if generate_btn:
            with st.spinner("⚡ Imagen Engine yana sarrafa hotonka..."):
                trans_text, error = safe_generate_content(
                    client, 
                    f"Translate this prompt to precise English image prompt: '{gen_prompt}'"
                )
                
                eng_prompt = trans_text.strip() if trans_text else gen_prompt

                dim_map = {"1:1 (Square)": (1024, 1024), "16:9 (Landscape)": (1280, 720), "9:16 (Portrait)": (720, 1280)}
                w, h = dim_map[ratio]

                style_modifiers = {
                    "Photorealistic (Na Gaske)": "photorealistic 8k, ultra-detailed, highly realistic lighting",
                    "3D Render": "3d octane render, cinema 4d, smooth shading",
                    "Anime / Art": "vibrant anime style, clean lines, aesthetic colors",
                    "Cyberpunk": "cyberpunk style, vibrant neon lights, futuristic cityscape",
                    "Cinematic Dark": "cinematic dramatic dark lighting, movie shot"
                }

                final_query = f"{eng_prompt}, {style_modifiers[style]}"
                seed = random.randint(1, 999999)
                encoded = urllib.parse.quote(final_query)
                image_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&seed={seed}&model=flux-realism&nologo=true"

                st.session_state.gallery.insert(0, {
                    "url": image_url,
                    "prompt": gen_prompt,
                    "style": style
                })

                image_placeholder.empty()
                with image_placeholder.container():
                    st.image(image_url, caption=f"Sakamako: {gen_prompt}", use_container_width=True)
                    st.markdown(f"🔗 [Download HD]({image_url})")

    # ---------------- TAB 4: GALLERY ----------------
    with tab4:
        st.markdown("<h3 style='color: #E3E3E3; text-align: center; margin-bottom: 20px;'>🖼️ Taskar Hotuna (Gallery)</h3>", unsafe_allow_html=True)
        
        if len(st.session_state.gallery) == 0:
            st.info("Babu hoton da aka adana a yanzu.")
        else:
            if st.button("🗑️ Coge Duka Hotuna"):
                st.session_state.gallery = []
                st.rerun()

            g_cols = st.columns(3)
            for idx, item in enumerate(st.session_state.gallery):
                col_idx = idx % 3
                with g_cols[col_idx]:
                    st.markdown("<div class='gemini-card'>", unsafe_allow_html=True)
                    st.image(item["url"], use_container_width=True)
                    st.caption(f"**Prompt:** {item['prompt']}")
                    st.markdown(f"⬇️ [Download Direct HD]({item['url']})")
                    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.warning("⚠️ Da fatan ka saka Google Gemini API Key dinka a Control Panel (gefen hagu) domin kunna manhajar.")
