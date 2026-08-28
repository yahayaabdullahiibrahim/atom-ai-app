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
    page_title="ATOM AI - Ultra Modern Suite", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Modern Glassmorphism & Cyberpunk CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background: #030712;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #F3F4F6;
    }

    /* Background Neon Glows */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: -100px;
        left: -100px;
        width: 450px;
        height: 450px;
        background: rgba(99, 102, 241, 0.15);
        filter: blur(140px);
        border-radius: 50%;
        z-index: 0;
    }
    
    [data-testid="stAppViewContainer"]::after {
        content: "";
        position: fixed;
        bottom: -100px;
        right: -100px;
        width: 450px;
        height: 450px;
        background: rgba(236, 72, 153, 0.12);
        filter: blur(140px);
        border-radius: 50%;
        z-index: 0;
    }
    
    /* Header Container */
    .hero-header {
        background: linear-gradient(180deg, rgba(17, 24, 39, 0.8) 0%, rgba(3, 7, 18, 0.9) 100%);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 30px 20px;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.6);
    }
    
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366F1 0%, #EC4899 50%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
        letter-spacing: -1px;
    }
    
    /* Glass Cards */
    .glass-card {
        background: rgba(17, 24, 39, 0.6);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 22px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.15);
    }

    /* Modernized Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(17, 24, 39, 0.8);
        padding: 8px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        gap: 12px;
        display: flex;
        justify-content: center;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 14px;
        color: #9CA3AF;
        font-weight: 700;
        padding: 12px 24px;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 0.95rem;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #FFFFFF;
        background: rgba(255, 255, 255, 0.05);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 6px 25px rgba(99, 102, 241, 0.45);
    }

    /* Buttons Override */
    .stButton>button {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        color: white;
        border: none;
        padding: 12px 22px;
        font-weight: 700;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.25);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.45);
    }

    /* Custom Inputs */
    .stTextArea textarea, .stTextInput input {
        background: rgba(3, 7, 18, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.3) !important;
    }

    section[data-testid="stSidebar"] {
        background: #030712;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
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

if "preset_prompt" not in st.session_state:
    st.session_state.preset_prompt = "Futuristic neon cyber motorbike, high speed blur, Tokyo night background, 8k render"

if "gallery" not in st.session_state:
    st.session_state.gallery = []

def start_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {"title": "Sabuwar Hira", "messages": []}
    st.session_state.current_chat_id = new_id

# Safe API Call Handler
def safe_generate_content(client, contents, model='gemini-3.6-flash', max_retries=3):
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
                    sleep_time = (attempt + 1) * 4
                    st.toast(f"⏳ Cunkoso a server. ATOM zai sake gwada bayan dakika {sleep_time}...", icon="⏳")
                    time.sleep(sleep_time)
                    continue
                return None, "⏳ Quota din asusunka ta cika (Rate Limit/Quota Exceeded). Da fatan sake gwada daga baya."
            elif any(code in err_msg for code in ["401", "UNAUTHENTICATED"]):
                return None, "🔑 Kuskuren API Key: Tabbatar an saka ingantaccen Gemini API Key."
            else:
                return None, f"Kuskure: {err_msg}"

# 4. Header UI
st.markdown("""
    <div class="hero-header">
        <div style="color: #8B5CF6; font-size: 0.8rem; font-weight: 700; letter-spacing: 2px; margin-bottom: 4px;">NEXT-GEN CREATIVE PLATFORM</div>
        <div class="hero-title">⚡ ATOM Studio Ultra</div>
        <div style="color: #9CA3AF; font-size: 0.95rem;">Dandalin Hira, Bincike, da Zana Hotuna na AI</div>
    </div>
""", unsafe_allow_html=True)

# API Key Retrieval Logic (Checks Secrets First, then Sidebar Fallback)
api_key = st.secrets.get("GEMINI_API_KEY", "")

# 5. Sidebar Navigation
with st.sidebar:
    st.markdown("<h3 style='color: white;'>⚙️ Control Center</h3>", unsafe_allow_html=True)
    
    if api_key:
        st.success("🟢 API System Connected")
    else:
        api_key = st.text_input("🔑 Gemini API Key:", type="password", help="Saka API key dinka a nan")
        
    st.markdown("---")
    
    if st.button("➕ New Workspace Session", use_container_width=True):
        start_new_chat()
        st.rerun()

    st.markdown("<h4 style='color: #9CA3AF; margin-top: 15px;'>💬 Saved Chats</h4>", unsafe_allow_html=True)
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

    # Sababbin Sunayen Tabs Na Zamani
    tab1, tab2, tab3, tab4 = st.tabs([
        "⚡ Smart AI & Docs", 
        "🔍 Intelligent Vision", 
        "🎨 Neural Canvas Ultra", 
        "🖼️ Master Gallery"
    ])

    # ---------------- TAB 1: SMART AI & DOCS ----------------
    with tab1:
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.markdown("<div class='glass-card'><h5>📄 Smart Document Reader</h5>", unsafe_allow_html=True)
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
                    st.success("✅ An sarrafa takardar!")
                except Exception as e:
                    st.error(f"Kuskure: {e}")

        with col2:
            for msg in current_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if user_input := st.chat_input("Rubuta sakonka..."):
                current_messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)

                if len(current_messages) == 1:
                    st.session_state.chats[current_id]["title"] = user_input[:20] + "..."

                full_prompt = user_input
                if doc_text:
                    full_prompt = f"Context from Document:\n{doc_text[:4000]}\n\nUser Question: {user_input}"

                with st.chat_message("assistant"):
                    with st.spinner("ATOM yana aiki..."):
                        response_text, error = safe_generate_content(client, full_prompt)
                        if response_text:
                            st.markdown(response_text)
                            current_messages.append({"role": "assistant", "content": response_text})
                            st.rerun()
                        else:
                            st.warning(error)

    # ---------------- TAB 2: INTELLIGENT VISION ----------------
    with tab2:
        col_v1, col_v2 = st.columns([1, 1], gap="large")
        with col_v1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            uploaded_image = st.file_uploader("Loda Hoto:", type=["jpg", "jpeg", "png"])
            if uploaded_image:
                img = Image.open(uploaded_image)
                st.image(img, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_v2:
            image_prompt = st.text_area("Tambayarku a kan hoton:", "Bani cikakken bayanin hoton nan.")
            if uploaded_image and st.button("🔍 Fara Binciken Hoto"):
                with st.spinner("Intelligent Vision yana bincike..."):
                    response_text, error = safe_generate_content(client, [img, image_prompt])
                    if response_text:
                        st.info(response_text)
                    else:
                        st.warning(error)

    # ---------------- TAB 3: NEURAL CANVAS ULTRA ----------------
    with tab3:
        st.markdown("<h3 style='color: white; text-align: center; margin-bottom: 15px;'>🎨 Neural Canvas Image Studio</h3>", unsafe_allow_html=True)
        
        col_st1, col_st2 = st.columns([1, 1.2], gap="large")

        with col_st1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            gen_prompt = st.text_area("Bayanin Hoto (Prompt):", value=st.session_state.preset_prompt, height=120)
            
            style = st.selectbox("🎨 Salon Hoto (Art Style):", ["Photorealistic (Na Gaske)", "3D Render (Octane)", "Anime Art", "Cyberpunk Neon", "Cinematic Dark"])
            ratio = st.radio("📐 Formats (Aspect Ratio):", ["1:1 (Square)", "16:9 (Landscape)", "9:16 (Portrait)"], horizontal=True)
            
            generate_btn = st.button("🚀 Zana Hoton Yanzu", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_st2:
            st.markdown("<div class='glass-card' style='text-align: center;'>", unsafe_allow_html=True)
            image_placeholder = st.empty()
            image_placeholder.markdown("""
                <div style="padding: 70px 20px; color: #4B5563;">
                    <div style="font-size: 3rem; margin-bottom: 8px;">✨</div>
                    Sakamakon zane zai bayyana a nan.
                </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if generate_btn:
            with st.spinner("⚡ Generation Engine yana aiki..."):
                trans_text, error = safe_generate_content(
                    client, 
                    f"Translate this prompt to precise English image generation prompt: '{gen_prompt}'"
                )
                
                eng_prompt = trans_text.strip() if trans_text else gen_prompt

                dim_map = {"1:1 (Square)": (1024, 1024), "16:9 (Landscape)": (1280, 720), "9:16 (Portrait)": (720, 1280)}
                w, h = dim_map[ratio]

                style_modifiers = {
                    "Photorealistic (Na Gaske)": "photorealistic 8k, ultra-detailed, highly realistic lighting",
                    "3D Render (Octane)": "3d octane render, cinema 4d, smooth shading",
                    "Anime Art": "vibrant anime style, clean lines, aesthetic colors",
                    "Cyberpunk Neon": "cyberpunk style, vibrant neon lights, futuristic cityscape",
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
                    st.markdown(f"🔗 [Download Direct Image HD]({image_url})")

    # ---------------- TAB 4: MASTER GALLERY ----------------
    with tab4:
        st.markdown("<h3 style='color: white; text-align: center; margin-bottom: 20px;'>🖼️ Master Gallery</h3>", unsafe_allow_html=True)
        
        if len(st.session_state.gallery) == 0:
            st.info("Babu hoton da aka adana a yanzu.")
        else:
            if st.button("🗑️ Clear All Gallery Images"):
                st.session_state.gallery = []
                st.rerun()

            g_cols = st.columns(3)
            for idx, item in enumerate(st.session_state.gallery):
                col_idx = idx % 3
                with g_cols[col_idx]:
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    st.image(item["url"], use_container_width=True)
                    st.caption(f"**Prompt:** {item['prompt']}")
                    st.markdown(f"⬇️ [Download HD]({item['url']})")
                    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.warning("⚠️ Sanya Gemini API Key dinka a Secrets ko a Control Center domin kunna dandalin.")
