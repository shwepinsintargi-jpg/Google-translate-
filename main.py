import streamlit as st
from deep_translator import GoogleTranslator
import PyPDF2
from docx import Document
from io import BytesIO
import time
import json
import re

# --- Page Config ---
st.set_page_config(page_title="AI Translator Pro", layout="centered")

# --- Custom CSS (Pure White Background & Black Text) ---
st.markdown("""
    <style>
    /* တစ်ပြင်လုံးကို အဖြူရောင်ပြောင်းခြင်း */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    .main .block-container {
        max-width: 500px;
        padding-top: 1rem;
    }

    /* စာသားအားလုံးကို အနက်ရောင်ပြောင်းခြင်း */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #000000 !important;
        font-family: 'Pyidaungsu', sans-serif;
    }

    /* Dropdown Box (Selectbox) Styling */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #000000 !important;
    }
    
    /* File Uploader - အဖြူရောင်နောက်ခံနှင့် အနက်ရောင်အစင်းကြောင်း */
    .stFileUploader section {
        background-color: #FFFFFF !important;
        border: 1.5px dashed #000000 !important;
        border-radius: 0px !important; /* လေးထောင့်ကျကျ ပိုဆန်စေရန် */
    }

    /* File Uploader ခလုတ်ကို အနက်ရောင်ပြောင်းခြင်း */
    .stFileUploader section button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: none !important;
        font-size: 0 !important;
    }
    .stFileUploader section button::after {
        content: "ဖိုင်တင်ရန်";
        font-size: 14px !important;
        color: #FFFFFF !important;
    }

    /* စတင်ဘာသာပြန်ပါ ခလုတ် - အနက်ရောင် */
    .stButton>button {
        width: 100%;
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 0px !important;
        font-weight: bold;
        height: 3em;
        border: 1px solid #000000 !important;
    }
    
    /* Progress Bar ကို အနက်ရောင်ပြောင်းခြင်း */
    .stProgress > div > div > div > div {
        background-color: #000000 !important;
    }

    /* Divider ကို အနက်ရောင်ပါးပါးပြောင်းခြင်း */
    hr {
        border-top: 1px solid #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Formula & Chemical Protection Logic ---
def smart_process(text, glossary):
    if re.search(r'[=+*/\^<>]', text) or re.search(r'\b[A-Z][a-z]?\d+\b', text):
        return text
    try:
        translated = GoogleTranslator(source='en', target='my').translate(text)
        if glossary:
            sorted_keys = sorted(glossary.keys(), key=len, reverse=True)
            for eng in sorted_keys:
                pattern = re.compile(re.escape(eng), re.IGNORECASE)
                translated = pattern.sub(glossary[eng], translated)
        return translated
    except:
        return text

# --- Sound Function ---
def play_notification_sound():
    sound_url = "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"
    sound_html = f"<audio autoplay><source src='{sound_url}' type='audio/mp3'></audio>"
    st.components.v1.html(sound_html, height=0)

# --- UI Setup ---
GLOSSARY_FILES = {
    "ရိုးရိုးဝတ္ထု": "glossary_novel.json",
    "အက်ရှင်": "glossary_action.json",
    "အထွေထွေ": "glossary_general.json",
    "သင်္ချာ": "glossary_math.json",
    "သိပ္ပံ": "glossary_science.json"
}

# 1. Title
st.markdown("### 📖 စာပေအမျိုးအစားရွေးရန်")
selected_genre = st.selectbox("", list(GLOSSARY_FILES.keys()), label_visibility="collapsed")

# 2. File Upload
st.markdown("<br>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("ဘာသာပြန်မည့် file တင်ပါ", type="pdf")

if uploaded_file:
    # ဖိုင်တင်ပြီးသွားလျှင် အနက်ရောင်စာသားဖြင့်ပြခြင်း
    st.markdown(f"**📄 ဖိုင်အမည်:** {uploaded_file.name}")
    st.markdown("---")
    
    if st.button("စတင်ဘာသာပြန်ပါ"):
        with st.status("ဘာသာပြန်နေပါသည်...", expanded=True) as status:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            doc = Document()
            
            try:
                with open(GLOSSARY_FILES[selected_genre], 'r', encoding='utf-8') as f:
                    glossary = json.load(f)
            except: glossary = {}

            total_pages = len(pdf_reader.pages)
            progress_bar = st.progress(0)

            for i in range(total_pages):
                st.write(f"➡️ စာမျက်နှာ {i+1} ကို လုပ်ဆောင်နေသည်...")
                page_text = pdf_reader.pages[i].extract_text()
                if page_text:
                    lines = page_text.split('\n')
                    doc.add_heading(f"Page {i+1}", level=2)
                    for line in lines:
                        if line.strip():
                            processed_line = smart_process(line.strip(), glossary)
                            doc.add_paragraph(processed_line)
                
                progress_bar.progress((i + 1) / total_pages)
                time.sleep(0.05)

            status.update(label="✅ ဘာသာပြန်ခြင်း ပြီးဆုံးပါပြီ!", state="complete")
            play_notification_sound()
            
            bio = BytesIO()
            doc.save(bio)
            st.download_button(
                label="📥 Word file ဒေါင်းရန်",
                data=bio.getvalue(),
                file_name=f"Translated_{selected_genre}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
else:
    # ဖိုင်မတင်ရသေးခင် အနက်ရောင် Progress Bar အလွတ်ပြထားမည်
    st.progress(0)
