import streamlit as st
from deep_translator import GoogleTranslator
import PyPDF2
from docx import Document
from io import BytesIO
import time
import json
import base64

# --- Page Config ---
st.set_page_config(page_title="AI Translator", layout="centered")

# --- Custom CSS (Fixed Layout & Styles) ---
st.markdown("""
    <style>
    .main .block-container { max-width: 500px; padding-top: 1rem; }
    
    .stFileUploader section {
        background-color: #D1FFD7 !important; 
        border: 2px dashed #2E86C1 !important;
        border-radius: 10px;
        padding: 10px;
    }
    .stFileUploader label {
        color: #1A5276 !important; 
        font-weight: bold;
        font-size: 16px;
    }
    .stProgress > div > div > div > div { background-color: #3498DB; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- Sound Function (အသံမြည်အောင်လုပ်ခြင်း) ---
def play_notification_sound():
    # အွန်လိုင်းမှ Notification အသံတိုလေးတစ်ခုကို သုံးထားပါတယ်
    sound_url = "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"
    sound_html = f"""
        <audio autoplay>
            <source src="{sound_url}" type="audio/mp3">
        </audio>
    """
    st.components.v1.html(sound_html, height=0)

# --- Logic ---
GLOSSARY_FILES = {
    "ရိုးရိုးဝတ္ထု": "glossary_novel.json",
    "အက်ရှင်": "glossary_action.json",
    "အထွေထွေ": "glossary_general.json",
    "သင်္ချာ": "glossary_math.json"
}

def load_glossary(category):
    try:
        with open(GLOSSARY_FILES[category], 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return {}

# --- UI Layout ---

# 1. Genre Selection
st.markdown("### 📖 စာပေအမျိုးအစားရွေးရန်")
selected_genre = st.selectbox("", list(GLOSSARY_FILES.keys()), label_visibility="collapsed")
st.write(f"ရွေးချယ်ထားသော အမျိုးအစား - **{selected_genre}**")

# 2. File Upload Area
uploaded_file = st.file_uploader("ဘာသာပြန်မည့် file တင်ပါ", type="pdf")

if uploaded_file:
    # ဖိုင်တင်ပြီးသွားလျှင် နာမည်ပြခြင်း
    st.markdown(f"<p style='color:black; font-weight:bold; margin-top:10px;'>📄 ဖိုင်နာမည်: {uploaded_file.name}</p>", unsafe_allow_html=True)
    
    # 3. Translate Button & Process
    st.write("---")
    st.info("✨ ဘာသာပြန်ရန် အဆင်သင့်ဖြစ်ပါပြီ")
    
    if st.button("စတင်ဘာသာပြန်ပါ"):
        with st.status(f"စာမျက်နှာများကို ဘာသာပြန်နေသည်...", expanded=True) as status:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            doc = Document()
            glossary = load_glossary(selected_genre)
            
            total_pages = len(pdf_reader.pages)
            progress_bar = st.progress(0)
            
            for i in range(total_pages):
                st.write(f"➡️ စာမျက်နှာ {i+1} ကို အချောသတ်နေသည်...")
                page_text = pdf_reader.pages[i].extract_text()
                
                if page_text:
                    translated = GoogleTranslator(source='en', target='my').translate(page_text)
                    # Glossary အစားထိုးခြင်း
                    for eng, myan in glossary.items():
                        translated = translated.replace(eng, myan)
                    
                    doc.add_heading(f"Page {i+1}", level=2)
                    doc.add_paragraph(translated)
                
                progress_bar.progress((i + 1) / total_pages)
                time.sleep(0.1)
            
            status.update(label="✅ ဘာသာပြန်ခြင်း ပြီးဆုံးပါပြီ!", state="complete")
            
            # --- ဘာသာပြန်ပြီးတာနဲ့ အသံမြည်စေခြင်း ---
            play_notification_sound()
            
            # Download Section
            bio = BytesIO()
            doc.save(bio)
            st.download_button(
                label="📥 Word file ဒေါင်းရန်",
                data=bio.getvalue(),
                file_name=f"Translated_{selected_genre}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
else:
    # ဖိုင်မတင်ရသေးခင် အပြာရောင် Progress Bar အလွတ်ပြထားခြင်း
    st.progress(0)
