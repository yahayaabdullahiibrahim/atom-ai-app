import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import PyPDF2
import docx
import io
import urllib.parse
import uuid

# 1. Page Configuration
st.set_page_config(
    page_title="ATOM AI - Professional Workspace", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Modern Custom CSS Styling
st.markdown("""
    <style>
    /* Global Styles */
    .main {
        background-color: #0E1117;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #1E1E2E 0%, #2A2D3E 100%);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #3A3D52;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .main-title {
        color: #FFFFFF;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .main-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-top: 6px;
    }

    /* Modern Badge */
    .badge {
        background: linear-gradient(90deg, #6366F1 0%, #8B5CF6 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 10px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #161922;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #262936;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre;
        background-color: transparent;
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        border: none;
        padding: 0px 20px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }

    /* Sidebar Custom Styling */
    section[data-testid="stSidebar"] {
        background-color: #12151C;
        border-right: 1px solid #262936;
    }

    /* Buttons Styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
        <div class="badge">NEXT-GEN AI WORKSPACE</div>
        <div class="main-title">🤖 ATOM AI Assistant</div>
        <div class="main-subtitle">Ingantaccen tsarin AI na zamani domin hira, bincikar takardu, gano hoto, da zana zane-zane.</div>
    </div>
""", unsafe_allow_html=True)

# 5. Sidebar Configuration & Chat History
with st.sidebar:
    st.markdown("### ⚙️ Saitunan Tsari")
    api_key = st.text_input("🔑 Saka Gemini API Key:", type="password", help="Sami API key daga Google AI Studio")
    st.markdown("---")
    
    if st.button("➕ Sabuwar Hira (New Chat)", use_container_width=True):
        start_new_chat()
        st.rerun()

    st.markdown("### 💬 Tarihin Hirarraki (Saved Topics)")
    
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
    client = genai.Client(api_key=api_key.strip())
    
    system_prompt = """
    Sunanka ATOM. Kai gwanin AI ne mai matukar basira da iyawa.
    Koyaushe ka sanar da mai amfani da kai cewa sunanka ATOM idan aka tambaye ka.
    Za ka iya taimakawa wajen bincikar takardu, fassara, gano hoto, da amsa kowace irin tambaya cikin harshen Hausa ko Turanci.
    Amsoshinka su kasance a tsara, masu kyawun fasali da girmamawa.
    """

    current_id = st.session_state.current_chat_id
    current_messages = st.session_state.chats[current_id]["messages"]

    tab1, tab2, tab3 = st.tabs(["💬 Hira & Takardu", "🖼️ Bincikar Hoto", "🎨 Zana Hoto (Generate Image)"])

    # ---------------- TAB 1: CHAT & DOCUMENTS ----------------
    with tab1:
        col1, col2 = st.columns([1, 2], gap="large")
        
        with col1:
            st.markdown("##### 📄 Loda Takarda")
            uploaded_doc = st.file_uploader("Saka Fayil (PDF, DOCX, TXT):", type=["pdf", "docx", "txt"])
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
                    
                st.success("✅ An karanta takardar cikin nasara!")

        with col2:
            st.markdown("##### 💬 Dandalin Hira")
            
            for msg in current_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if user_input := st.chat_input("Rubuta sakonka ko tambayarka a nan..."):
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
                    with st.spinner("ATOM yana tunani..."):
                        try:
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
                            st.error(f"Kuskure ya faru: {e}")

    # ---------------- TAB 2: IMAGE VISION ----------------
    with tab2:
        st.markdown("### 🖼️ Binciken Halayen Hoto (Vision)")
        st.caption("Loda hoto domin ATOM ya fayyace muku abinda ke ciki Daki-daki.")
        
        col_img1, col_img2 = st.columns([1, 1], gap="large")
        
        with col_img1:
            uploaded_image = st.file_uploader("Zabi hoto daga na'urarka...", type=["jpg", "jpeg", "png"], key="vision_uploader")
            if uploaded_image:
                img = Image.open(uploaded_image)
                st.image(img, caption="Hoton da ka loda", use_container_width=True)

        with col_img2:
            image_prompt = st.text_area("Bayanin abinda kake son sani game da hoton:", "Yi mini bayani daki-daki game da wannan hoton da Hausa.")
            
            if uploaded_image and st.button("🔍 Binciki Hoton Yanzu"):
                with st.spinner("ATOM yana nazarin hoton..."):
                    try:
                        response = client.models.generate_content(
                            model='gemini-3.6-flash',
                            contents=[img, image_prompt],
                        )
                        st.markdown("### 🤖 Sakamakon ATOM:")
                        st.info(response.text)
                    except Exception as e:
                        st.error(f"Kuskure ya faru: {e}")

    # ---------------- TAB 3: HIGH-QUALITY IMAGE GENERATION ----------------
    with tab3:
        st.markdown("### 🎨 Zana Hoto Mai Matukar Kyau (HD/4K)")
        st.caption("Bayyana irin hoton da kake bukata ta amfani da kalmomi daki-daki.")
        
        gen_prompt = st.text_area(
            "Rubuta bayanin hoton (Prompt):", 
            "A realistic portrait of a young person in golden hour lighting, sharp focus, highly detailed skin texture, 8k resolution, photorealistic",
            height=100
        )
        
        if st.button("✨ Zana Hoton Yanzu"):
            with st.spinner("ATOM yana tsara hotonku cikin inganci..."):
                success = False
                
                # Gwaji na 1: Google Imagen 3
                try:
                    result = client.models.generate_images(
                        model='imagen-3.0-generate-002',
                        prompt=gen_prompt,
                        config=types.GenerateImagesConfig(
                            number_of_images=1,
                            output_mime_type="image/jpeg",
                            aspect_ratio="1:1"
                        )
                    )
                    
                    for generated_image in result.generated_images:
                        image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                        st.image(image, caption=f"Sakamako (Google Imagen Ultra): {gen_prompt}", use_container_width=True)
                        st.success("✅ An zana hoton mai inganci ta Google Imagen!")
                        success = True
                except Exception:
                    st.info("ℹ️ Google Imagen na samun cunkoso, muna fito da hoton ta amfani da High-Resolution Render Engine...")

                # Gwaji na 2: High-Quality Flux Render Engine
                if not success:
                    try:
                        # Auto-enhance prompt for HD clarity
                        enhanced_prompt = f"{gen_prompt}, 8k resolution, highly detailed, photorealistic, cinematic lighting, sharp focus"
                        encoded_prompt = urllib.parse.quote(enhanced_prompt)
                        
                        # High Definition Model URL Stream (Flux Model)
                        hd_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&model=flux&nologo=true&enhance=true"
                        
                        st.image(hd_url, caption=f"Sakamako (HD Flux Engine): {gen_prompt}", use_container_width=True)
                        st.success("✅ An zana hoton HD mai matukar inganci da kyau!")
                    except Exception as fallback_error:
                        st.error(f"Kuskure: {fallback_error}")

else:
    st.warning("⚠️ Da fatan za ka saka Gemini API Key ɗinka a gefen hagu (Sidebar) domin Fara amfani da ATOM AI.")
