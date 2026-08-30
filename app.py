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
    page_title="ATOM AI - UK/MAN Suite", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Injecting Bootstrap 5 CSS CDN
st.markdown("""
    <!-- Bootstrap 5 CSS CDN -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <style>
    /* Minimal Streamlit Overrides to support Bootstrap */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa !important;
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    /* Streamlit Native Buttons Overridden with Bootstrap Look */
    .stButton>button {
        background-color: #0d6efd !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0.375rem !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075) !important;
    }

    .stButton>button:hover {
        background-color: #0b5ed7 !important;
    }

    /* Native Chat Message Styling */
    [data-testid="stChatMessage"] {
        background-color: #ffffff !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 0.5rem !important;
        color: #212529 !important;
        padding: 1rem !important;
        margin-bottom: 0.75rem !important;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.05) !important;
    }

    /* Hide Default Headers */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Session State
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

# Header Using Pure Bootstrap Classes
st.markdown("""
    <div class="container my-3 p-4 bg-white rounded-3 border shadow-sm text-center">
        <h1 class="display-6 fw-bold text-primary mb-1">⚡ ATOM Studio Ultra</h1>
        <p class="text-muted mb-0">Clean AI Workspace Powered by Bootstrap</p>
    </div>
""", unsafe_allow_html=True)

# API Key Retrieval
api_key = ""
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

# Sidebar
with st.sidebar:
    st.markdown("<h4 class='text-dark fw-bold'>⚙️ Control Center</h4>", unsafe_allow_html=True)
    if api_key:
        st.markdown("<div class='alert alert-success py-2 mb-3' role='alert'>🟢 API Connected</div>", unsafe_allow_html=True)
    else:
        api_key = st.text_input("🔑 Gemini API Key:", type="password")

    if st.button("➕ Sabuwar Hira", use_container_width=True):
        start_new_chat()
        st.rerun()

    st.markdown("---")
    st.markdown("<h6 class='text-secondary fw-bold'>💬 Hirarrakin Baya</h6>", unsafe_allow_html=True)
    for cid in reversed(list(st.session_state.chats.keys())):
        chat_data = st.session_state.chats[cid]
        label = f"💬 {chat_data['title']}" if cid == st.session_state.current_chat_id else f"📁 {chat_data['title']}"
        if st.button(label, key=f"sb_btn_{cid}", use_container_width=True):
            st.session_state.current_chat_id = cid
            st.rerun()

# Main Logic
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

        # Input
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
        st.markdown("<div class='card p-3 shadow-sm mb-3'>", unsafe_allow_html=True)
        uploaded_image = st.file_uploader("Loda Hoto:", type=["jpg", "jpeg", "png"])
        image_prompt = st.text_input("Bani tambaya a kan hoton:", "Mene ne a cikin hoton nan?")
        
        if uploaded_image:
            img = Image.open(uploaded_image)
            st.image(img, use_container_width=True)
            if st.button("🔍 Bincika Hoton", use_container_width=True):
                with st.spinner("Intelligent Vision yana bincike..."):
                    res_text, err = safe_generate_content(client, [img, image_prompt])
                    if res_text:
                        st.info(res_text)
                    else:
                        st.error(err)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- TAB 3: DRAW IMAGE ----------------
    with tab3:
        st.markdown("<div class='card p-3 shadow-sm mb-3'>", unsafe_allow_html=True)
        gen_prompt = st.text_area("Bayanin hoton da kake so a zana:", value=st.session_state.preset_prompt, height=80)
        style = st.selectbox("Salon Hoto:", ["Photorealistic", "3D Render", "Anime Art", "Cyberpunk Neon"])
        generate_btn = st.button("🚀 Zana Hoto Yanzu", use_container_width=True)
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
