import streamlit as st
from supabase import create_client, Client
import hashlib
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

# 2. Injecting Bootstrap 5 CSS
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa !important;
        font-family: system-ui, -apple-system, sans-serif;
    }
    .stButton>button {
        background-color: #0d6efd !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0.375rem !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
    }
    [data-testid="stChatMessage"] {
        background-color: #ffffff !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 0.5rem !important;
        padding: 1rem !important;
        margin-bottom: 0.75rem !important;
    }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Supabase Connection Setup
raw_supabase_url = st.secrets.get("SUPABASE_URL", "").strip()
supabase_key = st.secrets.get("SUPABASE_KEY", "").strip()

cleaned_url = raw_supabase_url.split("/rest/v1")[0].rstrip("/")

@st.cache_resource
def init_supabase():
    if cleaned_url and supabase_key:
        return create_client(cleaned_url, supabase_key)
    return None

supabase: Client = init_supabase()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_user(username, password):
    data = {"username": username.strip(), "password": make_hashes(password)}
    res = supabase.table("users").insert(data).execute()
    return res

def login_user(username, password):
    hashed_pass = make_hashes(password)
    res = supabase.table("users").select("*").eq("username", username.strip()).eq("password", hashed_pass).execute()
    return len(res.data) > 0

# 4. Session State Setup
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
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

# 5. Function don kiran Gemini tare da System Instruction ta ATOM
def safe_generate_content(client, contents, model='gemini-3.6-flash', max_retries=2):
    system_instruction = (
        "You are ATOM, an advanced AI assistant created to help users with information, "
        "code, analysis, and creative tasks. Never identify yourself as Gemini or a language "
        "model built by Google. When asked who you are or what your name is, explicitly state "
        "that you are ATOM."
    )
    
    for attempt in range(max_retries + 1):
        try:
            clean_model = model.replace("models/", "")
            res = client.models.generate_content(
                model=clean_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
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

# 6. Authentication UI
if not st.session_state.logged_in:
    st.markdown("""
        <div class="container my-4 p-4 bg-white rounded-3 border shadow-sm text-center" style="max-width: 500px;">
            <h2 class="fw-bold text-primary mb-1">⚡ ATOM AI</h2>
            <p class="text-muted">Da fatan ka shiga ko ka yi rijista (Permanent DB)</p>
        </div>
    """, unsafe_allow_html=True)

    if not supabase:
        st.error("⚠️ An kasa haɗawa da Supabase. Tabbatar ka saka SUPABASE_URL da SUPABASE_KEY a Secrets.")
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            tab_login, tab_signup = st.tabs(["🔑 Sign In", "📝 Sign Up"])
            
            with tab_login:
                u_login = st.text_input("Username", key="l_user")
                p_login = st.text_input("Password", type="password", key="l_pass")
                if st.button("Shiga (Sign In)", key="btn_login"):
                    try:
                        if login_user(u_login, p_login):
                            st.session_state.logged_in = True
                            st.session_state.username = u_login
                            st.success(f"Barka da zuwa {u_login}!")
                            st.rerun()
                        else:
                            st.error("Username ko Password ba daidai ba ne!")
                    except Exception as e:
                        st.error(f"Kuskuren haɗawa: {e}")

            with tab_signup:
                u_signup = st.text_input("Zaɓi Username", key="s_user")
                p_signup = st.text_input("Zaɓi Password", type="password", key="s_pass")
                p_confirm = st.text_input("Maimaita Password", type="password", key="s_conf")
                if st.button("Yi Rijista (Sign Up)", key="btn_signup"):
                    if p_signup != p_confirm:
                        st.warning("Password ba su yi daidai ba!")
                    elif not u_signup or not p_signup:
                        st.warning("Da fatan ka cike dukkan guraren!")
                    else:
                        try:
                            add_user(u_signup, p_signup)
                            st.success("An yi rijista a Supabase cikin nasara! Yanzu za ka iya komawa Sign In.")
                        except Exception as e:
                            st.error(f"Kuskure daga Supabase: {e}")

# 7. Main App Interface
else:
    api_key = st.secrets.get("GEMINI_API_KEY", "")

    st.markdown(f"""
        <div class="container my-3 p-3 bg-white rounded-3 border shadow-sm d-flex justify-content-between align-items-center">
            <h3 class="fw-bold text-primary m-0">⚡ ATOM Studio Ultra</h3>
            <span class="badge bg-light text-dark border">👤 {st.session_state.username}</span>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"<h5 class='fw-bold'>👤 {st.session_state.username}</h5>", unsafe_allow_html=True)
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
            
        st.markdown("---")
        if api_key:
            st.markdown("<div class='alert alert-success py-1 mb-2'>🟢 API Connected</div>", unsafe_allow_html=True)
        else:
            api_key = st.text_input("🔑 Gemini API Key:", type="password")

        if st.button("➕ Sabuwar Hira", use_container_width=True):
            start_new_chat()
            st.rerun()

        st.markdown("<h6 class='text-secondary fw-bold mt-3'>💬 Hirarrakin Baya</h6>", unsafe_allow_html=True)
        for cid in reversed(list(st.session_state.chats.keys())):
            chat_data = st.session_state.chats[cid]
            label = f"💬 {chat_data['title']}" if cid == st.session_state.current_chat_id else f"📁 {chat_data['title']}"
            if st.button(label, key=f"sb_btn_{cid}", use_container_width=True):
                st.session_state.current_chat_id = cid
                st.rerun()

    if api_key:
        client = genai.Client(api_key=api_key.strip())
        current_id = st.session_state.current_chat_id
        current_messages = st.session_state.chats[current_id]["messages"]

        tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat & Docs", "🔍 Vision AI", "🎨 Draw Image", "🖼️ Gallery"])

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

            for msg in current_messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

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
