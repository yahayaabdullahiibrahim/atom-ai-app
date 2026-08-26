import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
import docx

st.set_page_config(page_title="Atom AI - Pro", page_icon="🤖", layout="wide")

st.title("🤖 Atom AI Assistant")
st.caption("Cikakken AI mai gano hoto, karanta takardu (PDF/Docx), da amsa tambayoyi.")

# Sidebar Settings
st.sidebar.header("⚙️ Saitunan Atom AI")
api_key = st.sidebar.text_input("🔑 Saka Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    system_prompt = """
    Sunanka ATOM. Kai gwanin AI ne mai matukar basira da iyawa.
    Koyaushe ka sanar da mai amfani da kai cewa sunanka ATOM idan aka tambaye ka.
    Za ka iya taimakawa wajen bincikar takardu, fassara, gano hoto, da amsa kowace irin tambaya cikin harshen Hausa ko Turanci.
    """
    
    # An gyara sunan model zuwa gemini-1.5-flash
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)

    # Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Tab 1: Chat & Documents | Tab 2: Vision & Images
    tab1, tab2 = st.tabs(["💬 Hira & Bincikar Takardu (PDF/Docx)", "🖼️ Bincikar Hotuna"])

    with tab1:
        # File Uploading for PDF/Docx
        uploaded_doc = st.file_uploader("📄 Loda Fayil (PDF ko Word Docx) don Atom ya bincika:", type=["pdf", "docx", "txt"])
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
                
            st.success("✅ An loda takarda cikin nasara! Atom yana shirye don amsa tambayoyi a kanta.")

        # Display Chat History
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat Input
        if user_input := st.chat_input("Yi wa Atom tambaya a nan..."):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Combine Document text if available
            full_prompt = user_input
            if doc_text:
                full_prompt = f"Bisa labarin/bayanin da ke cikin wannan takardar:\n\n{doc_text[:4000]}\n\nAmsa wannan tambayar: {user_input}"

            with st.chat_message("assistant"):
                with st.spinner("Atom yana tunani..."):
                    chat = model.start_chat(history=[])
                    response = chat.send_message(full_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})

    with tab2:
        st.subheader("🖼️ Loda Hoto don Atom ya bincika")
        uploaded_image = st.file_uploader("Zaɓi hoto...", type=["jpg", "jpeg", "png"], key="vision_uploader")
        image_prompt = st.text_input("Me kake son Atom ya gano ko ya bayyana a hoton?:", "Yi mini bayani daki-daki game da wannan hoton da Hausa.")

        if uploaded_image:
            img = Image.open(uploaded_image)
            st.image(img, caption="Hoton da ka loda", width=400)
            
            if st.button("🔍 Binciki Hoton Yanzu"):
                with st.spinner("Atom yana bincikar hoton..."):
                    response = model.generate_content([image_prompt, img])
                    st.write("### 🤖 Sakamakon Atom:")
                    st.write(response.text)

else:
    st.warning("⚠️ Da fatan za ka saka Gemini API Key ɗinka a gefen hagu domin fara amfani da dukkan fasahohin Atom AI.")
