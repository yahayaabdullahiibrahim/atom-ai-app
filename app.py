import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import PyPDF2
import docx
import urllib.parse
import uuid
import random

# 1. Page Configuration
st.set_page_config(
    page_title="ATOM AI - NextGen Studio", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Ultra-Modern Glassmorphism & Neon CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background: #030712;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #F3F4F6;
    }
    
    /* Header Container */
    .hero-header {
        background: linear-gradient(180deg, rgba(17, 24, 39, 0.8) 0%, rgba(3, 7, 18, 0.9) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 35px 20px;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.6);
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366F1 0%, #EC4899 50%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
        letter-spacing: -1px;
    }
    
    /* Glass Cards */
    .glass-card {
        background: rgba(17, 24, 39, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.15);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(17, 24, 39, 0.7);
        padding: 8px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        color: #9CA3AF;
        font-weight: 600;
        padding: 10px 20px;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
    }

    /* Modern Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        color: white;
        border: none;
        padding: 14px 24px;
        font-weight: 700;
        border-radius: 14px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
    }

    /* Input Customization */
    .stTextArea textarea, .stTextInput input {
        background: rgba(3, 7, 18, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #F3F4F6 !important;
        border-radius: 12px !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.3) !important;
    }

    /* Sidebar Clean Look */
    section[data-testid="stSidebar"] {
        background: #030712;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. Session State Storage
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {"title": "Sabuwar Hira", "messages": []}
    st.session_state.current_chat_id = new_id

if "preset_prompt" not in st.session_state:
    st.session_state.preset_prompt = "Toyota Land Cruiser Prado 2024, futuristic dark background, neon headlights, 8k render"

# Gallery State Initialization
if "gallery" not in st.session_state:
    st.session_state.gallery = []

def start_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chats[new_id] = {"title": "Sabuwar Hira", "messages": []}
    st.session_state.current_chat_id = new_id

# 4. Header UI
st.markdown("""
    <div class="hero-header">
        <div style="color: #8B5CF6; font-size: 0.85rem; font-weight: 700; letter-spacing: 2px; margin-bottom: 5px;">NEXT-GEN CREATIVE SUITE</div>
        <div class="hero-title">⚡ ATOM Studio Pro</div>
        <div style="color: #9CA3AF; font-size: 1rem;">Madaidaicin dandalin hira, binciken hotuna, da zana hotunan AI na zamani.</div>
    </div>
""", unsafe_allow_html=True)

# 5. Sidebar
with st.sidebar:
    st.markdown("<h3 style='color: white;'>⚙️ Control Center</h3>", unsafe_allow_html=True)
    api_key = st.text_input("🔑 Gemini API Key:", type="password", help="Saka API key dinka a nan")
    st.markdown("---")
    
    if st.button("➕ New Session", use_container_width=True):
        start_new_chat()
        st.rerun()

    st.markdown("<h4 style='color: #6B7280;'>💬 Saved Workspaces</h4>", unsafe_allow_html=True)
    for cid in reversed(list(st.session_state.chats.keys())):
        chat_data = st.session_state.chats[cid]
        label = f"💬 {chat_data['title']}" if cid == st.session_state.current_chat_id else f"📁 {chat_data['title']}"
        if st.button(label, key=f"sidebar_btn_{cid}", use_container_width=True):
            st.session_state.current_chat_id = cid
            st.rerun()

# 6. Main Logic
if api_key:
    client = genai.Client(api_key=api_key.strip())
    current_id = st.session_state.current_chat_id
    current_messages = st.session_state.chats[current_id]["messages"]

    tab1, tab2, tab3, tab4 = st.tabs(["💬 Assistant", "🔍 Vision Lab", "🎨 Image Studio Ultra", "🖼️ Gallery"])

    # ---------------- TAB 1: CHAT ----------------
    with tab1:
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.markdown("<div class='glass-card'><h5>📄 Loda Fayil</h5>", unsafe_allow_html=True)
            uploaded_doc = st.file_uploader("PDF, DOCX, TXT", type=["pdf", "docx", "txt"])
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
                st.success("An karanta takarda!")

        with col2:
            for msg in current_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if user_input := st.chat_input("Yi tambaya ko ba da umarni..."):
                current_messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)

                if len(current_messages) == 1:
                    st.session_state.chats[current_id]["title"] = user_input[:20] + "..."

                full_prompt = user_input
                if doc_text:
                    full_prompt = f"Context:\n{doc_text[:4000]}\n\nQuestion: {user_input}"

                with st.chat_message("assistant"):
                    with st.spinner("ATOM yana tunani..."):
                        try:
                            res = client.models.generate_content(
                                model='gemini-3.6-flash',
                                contents=full_prompt
                            )
                            st.markdown(res.text)
                            current_messages.append({"role": "assistant", "content": res.text})
                            st.rerun()
                        except Exception as e:
                            st.error(f"Kuskure: {e}")

    # ---------------- TAB 2: VISION ----------------
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
            image_prompt = st.text_area("Tambayarka game da hoton:", "Nuna min cikakken bayani a kan wannan hoton.")
            if uploaded_image and st.button("🔍 Fara Bincike"):
                with st.spinner("Yana bincike..."):
                    try:
                        res = client.models.generate_content(
                            model='gemini-3.6-flash',
                            contents=[img, image_prompt]
                        )
                        st.info(res.text)
                    except Exception as e:
                        st.error(f"Kuskure: {e}")

    # ---------------- TAB 3: IMAGE STUDIO ULTRA ----------------
    with tab3:
        st.markdown("<h3 style='color: white; text-align: center; margin-bottom: 20px;'>🎨 Image Generation Engine</h3>", unsafe_allow_html=True)
        
        # Quick Preset Prompt Buttons
        st.markdown("<div style='margin-bottom: 10px; color: #9CA3AF; font-size: 0.85rem;'>💡 Danna misali don saurin gwadawa:</div>", unsafe_allow_html=True)
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
            if st.button("🏍️ Motorbike Concept"):
                st.session_state.preset_prompt = "Futuristic neon cyber motorbike, high speed blur, Tokyo night background, 8k render"
        with p_col2:
            if st.button("🚘 Land Cruiser Prado"):
                st.session_state.preset_prompt = "Toyota Land Cruiser Prado 2024, driving on Sahara desert dunes, golden hour sunset"
        with p_col3:
            if st.button("🦅 Cyberpunk Eagle"):
                st.session_state.preset_prompt = "Robotic mechanical eagle with glowing red eyes, metallic feathers, cinematic lighting"

        col_st1, col_st2 = st.columns([1, 1.2], gap="large")

        with col_st1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            gen_prompt = st.text_area("Bayanin Hoton (Prompt):", value=st.session_state.preset_prompt, height=130)
            
            style = st.selectbox("🎨 Zaɓi Salon Hoto (Art Style):", ["Photorealistic (Na Gaske)", "3D Render (Octane)", "Anime Art", "Cyberpunk Neon", "Cinematic Dark"])
            ratio = st.radio("📐 Aspect Ratio:", ["1:1 (Square)", "16:9 (Landscape)", "9:16 (Portrait)"], horizontal=True)
            
            generate_btn = st.button("🚀 Zana Hoton Yanzu")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_st2:
            st.markdown("<div class='glass-card' style='text-align: center;'>", unsafe_allow_html=True)
            image_placeholder = st.empty()
            image_placeholder.markdown("""
                <div style="padding: 80px 20px; color: #4B5563;">
                    <div style="font-size: 3rem; margin-bottom: 10px;">✨</div>
                    Sakamakon zane zai bayyana a nan.
                </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Execution
        if generate_btn:
            with st.spinner("⚡ Engine yana aiki..."):
                try:
                    # Translate prompt
                    trans = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=f"Translate this prompt to highly detailed English image prompt: '{gen_prompt}'"
                    )
                    eng_prompt = trans.text.strip()
                except Exception:
                    eng_prompt = gen_prompt

                # Dimensions
                dim_map = {"1:1 (Square)": (1024, 1024), "16:9 (Landscape)": (1280, 720), "9:16 (Portrait)": (720, 1280)}
                w, h = dim_map[ratio]

                style_modifiers = {
                    "Photorealistic (Na Gaske)": "photorealistic 8k, ultra-detailed, highly realistic lighting, masterpiece",
                    "3D Render (Octane)": "3d octane render, cinema 4d, smooth shading, vibrant colors",
                    "Anime Art": "vibrant anime style, clean lines, aesthetic colors, studio ghibli inspired",
                    "Cyberpunk Neon": "cyberpunk style, vibrant neon lights, futuristic cityscape, dramatic atmosphere",
                    "Cinematic Dark": "cinematic dramatic dark lighting, movie shot, highly detailed composition"
                }

                final_query = f"{eng_prompt}, {style_modifiers[style]}"
                seed = random.randint(1, 999999)
                encoded = urllib.parse.quote(final_query)
                image_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&seed={seed}&model=flux-realism&nologo=true"

                # Save to Gallery Session State
                st.session_state.gallery.insert(0, {
                    "url": image_url,
                    "prompt": gen_prompt,
                    "style": style
                })

                image_placeholder.empty()
                with image_placeholder.container():
                    st.image(image_url, caption=f"Sakamako: {gen_prompt}", use_container_width=True)
                    st.markdown(f"[⬇️ Sauke Hoton Direct (Download Link)]({image_url})")
                    st.success("✅ An kammala sannan an adana shi a Gallery!")

    # ---------------- TAB 4: GALLERY ----------------
    with tab4:
        st.markdown("<h3 style='color: white; text-align: center; margin-bottom: 20px;'>🖼️ Taskar Hotunan da Ka Zana (Gallery)</h3>", unsafe_allow_html=True)
        
        if len(st.session_state.gallery) == 0:
            st.info("Babu wani hoto a taskarka a yanzu. Je zuwa Tab 3 domin zana sabon hoto!")
        else:
            if st.button("🗑️ Goge Dukkan Hotuna (Clear Gallery)"):
                st.session_state.gallery = []
                st.rerun()

            # Display Gallery in Grid Format (3 Columns)
            g_cols = st.columns(3)
            for idx, item in enumerate(st.session_state.gallery):
                col_idx = idx % 3
                with g_cols[col_idx]:
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    st.image(item["url"], use_container_width=True)
                    st.caption(f"**Prompt:** {item['prompt']}")
                    st.caption(f"**Style:** {item['style']}")
                    st.markdown(f"[⬇️ Download HD]({item['url']})")
                    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.warning("⚠️ Saka Gemini API Key dinka a gefen hagu domin fara amfani.")
