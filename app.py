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
    initial_sidebar_state="collapsed"
)

# 2. Optimized Mobile-Friendly CSS (Gyararren Buttons & Gaps)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0d1117;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #f0f6fc;
    }

    /* Clean Card & Spacing */
    .glass-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }

    /* FIX BUTTON SPACING & LAYOUT FOR MOBILE */
    .stButton {
        margin-top: 8px !important;
        margin-bottom: 8px !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 10px 16px !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        width: 100% !important;
        display: block !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
    }

    /* Chat Messages Visibility */
    [data-testid="stChatMessage"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        color: #f0f6fc !important;
        padding: 12px !important;
        margin-bottom: 12px !important;
    }

    [data-testid="stChatMessage"] p {
        color: #f0f6fc !important;
        font-size: 1rem !important;
    }

    /* Input Fields Fix */
    .stTextArea textarea, .stTextInput input, [data-testid="stChatInput"] textarea {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }

    /* Header styling */
    .main-header {
        text-align: center;
        padding: 15px 10px;
        margin-bottom: 20px;
        background: #161b22;
        border-radius: 12px;
        border: 1px solid #30363d;
    }

    .main-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #58a6ff;
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Session State Management
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

# Safe API Handler
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
                return None, "⏳ An samu cunkoso. Da fatan sake gwada bayan dakika kadan."
            return None, f"Kuskure: {err_msg}"

# Header UI
st.markdown("""
    <div class="main-header">
        <div class="main-title">⚡ ATOM Studio Ultra</div>
        <div style="color: #8b949e; font-size: 0.85rem;">AI Workspace - Fast & Mobile Optimized</div>
    </div>
""", unsafe_allow_html=True)

# Safe Secrets Retrieval
api_key = ""
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Control Center")
    if api_key:
        st.success("🟢 API Connected")
    else:
        api_key = st.text_input("🔑 Gemini API Key:", type="password")

    st.markdown("<div style='margin-top:10px; margin-bottom:10px;'>", unsafe_allow_html=True)
    if st.button("➕ Sabuwar Hira (New Chat)", use_container_width=True):
        start_new_chat()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 💬 Hirarrakin Baya")
    for cid in reversed(list(st.session_state.chats.keys())):
        chat_data = st.session_state.chats[cid]
        label = f"💬 {chat_data['title']}" if cid == st.session_state.current_chat_id else f"📁 {chat_data['title']}"
        st.markdown("<div style='margin-bottom:6px;'>", unsafe_allow_html=True)
        if st.button(label, key=f"sb_btn_{cid}", use_container_width=True):
            st.session_state.current_chat_id = cid
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Engine Logic
if api_key:
    client = genai.Client(api_key=api_key.strip())
    current_id = st.session_state.current_chat_id
    current_messages = st.session_state.chats[current_id]["messages"]

    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Chat & Docs", 
        "🔍 Vision AI", 
        "🎨 Draw Image", 
        "🖼️ Gallery"
    ])

    # ---------------- TAB 1: CHAT & DOCS ----------------
    with tab1:
        with st.expander("📄 Loda PDF ko DOCX (Zabi ne)", expanded=False):
            uploaded_doc = st.file_uploader("Zaɓi fayil:", type=["pdf", "docx", "txt"])
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
                    st.success("✅ An karanta takardarka!")
                except Exception as e:
                    st.error(f"Kuskure: {e}")

        # Display Existing Messages
        for msg in current_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Input Field
        user_input = st.chat_input("Rubuta tambayarku a nan...")
        
        if user_input:
            current_messages.append({"role": "user", "content": user_input})
            
            if len(current_messages) == 1:
                st.session_state.chats[current_id]["title"] = user_input[:15] + "..."

            full_prompt = user_input
            if doc_text:
                full_prompt = f"Context from Document:\n{doc_text[:3000]}\n\nUser Question: {user_input}"

            with st.spinner("ATOM yana rubuta amsa..."):
                response_text, error = safe_generate_content(client, full_prompt)
                if response_text:
                    current_messages.append({"role": "assistant", "content": response_text})
                else:
                    current_messages.append({"role": "assistant", "content": f"⚠️ {error}"})
            st.rerun()

    # ---------------- TAB 2: VISION AI ----------------
    with tab2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        uploaded_image = st.file_uploader("Loda Hoto:", type=["jpg", "jpeg", "png"])
        image_prompt = st.text_input("Bani tambaya a kan hoton:", "Mene ne a cikin hoton nan?")
        
        if uploaded_image:
            img = Image.open(uploaded_image)
            st.image(img, use_container_width=True)
            
            st.markdown("<div style='margin-top:12px;'>", unsafe_allow_html=True)
            if st.button("🔍 Bincika Hoton", use_container_width=True):
                with st.spinner("Intelligent Vision yana bincike..."):
                    res_text, err = safe_generate_content(client, [img, image_prompt])
                    if res_text:
                        st.info(res_text)
                    else:
                        st.error(err)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- TAB 3: DRAW IMAGE ----------------
    with tab3:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        gen_prompt = st.text_area("Bayanin hoton da kake so a zana:", value=st.session_state.preset_prompt, height=80)
        style = st.selectbox("Salon Hoto:", ["Photorealistic", "3D Render", "Anime Art", "Cyberpunk Neon"])
        
        st.markdown("<div style='margin-top:12px;'>", unsafe_allow_html=True)
        generate_btn = st.button("🚀 Zana Hoto Yanzu", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if generate_btn:
            with st.spinner("Zanawa a yanar gizo..."):
                trans_text, _ = safe_generate_content(client, f"Translate to detailed image prompt: '{gen_prompt}'")
                eng_prompt = trans_text.strip() if trans_text else gen_prompt
                
                seed = random.randint(1, 999999)
                encoded = urllib.parse.quote(f"{eng_prompt}, {style} style")
                image_url = f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=800&seed={seed}&nologo=true"

                st.session_state.gallery.insert(0, {"url": image_url, "prompt": gen_prompt})
                st.image(image_url, caption=f"Sakamako: {gen_prompt}", use_container_width=True)
                st.markdown(f"🔗 [Sauke Hoton direct HD]({image_url})")

    # ---------------- TAB 4: GALLERY ----------------
    with tab4:
        if not st.session_state.gallery:
            st.info("Babu hotuna a gallery.")
        else:
            for item in st.session_state.gallery:
                st.image(item["url"], use_container_width=True)
                st.caption(item["prompt"])
                st.markdown("---")
else:
    st.error("⚠️ Ba a samun API Key ba. Tabbatar ka saka GEMINI_API_KEY a Streamlit Secrets ko a Sidebar.")
