import streamlit as st
from deep_translator import GoogleTranslator
import PyPDF2
from docx import Document
from io import BytesIO
import time
import json
import re

# --- Page Config ---
st.set_page_config(page_title="Pro AI Translator", layout="centered")

# --- Custom CSS (Minimalist Black & White Theme) ---
st.markdown("""
    <style>
    /* Global Background & Font Settings */
    .main { background-color: #FFFFFF !important; }
    .block-container { max-width: 500px; padding-top: 2rem; font-size: 14px; }
    
    /* Genre Title Style */
    .genre-title {
        display: inline-block;
        font-size: 18px;
        font-weight: bold;
        color: #000000 !important;
        margin-bottom: 5px;
    }

    /* Minimalist File Uploader (Light Gray Background) */
    .stFileUploader section {
        background-color: #F8F9FA !important; 
        border: 1px solid #DEE2E6 !important;
        border-radius: 8px;
        padding: 10px;
    }
    
    /* Change Browse Files Button Text to Myanmar */
    .stFileUploader section button {
        font-size: 0 !important;
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 5px;
    }
    .stFileUploader section button::after {
        content: "ဖိုင်တင်ရန်";
        font-size: 14px !important;
        color: #FFFFFF !important;
    }
    
    /* Labels & Text Color Consistency */
    label, p, span, .stMarkdown {
        color: #000000 !important;
        font-weight: 500;
    }

    /* Main Action Button (Solid Black) */
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        font-weight: bold; 
        height: 3em; 
        background-color: #000000 !important; 
        color: #FFFFFF !important;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #333333 !important;
    }

    /* Progress Bar Color (Dark Gray) */
    .stProgress > div > div > div > div {
        background-color: #000000 !important;
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

# 1. Genre Selection
st.markdown("<p class='genre-title'>📖 စာပေအမျိုးအစားရွေးရန်</p>", unsafe_allow_html=True)
selected_genre = st.selectbox("", list(GLOSSARY_FILES.keys()), label_visibility="collapsed")

# 2. File Upload Area
st.markdown("<br>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("ဘာသာပြန်မည့် file တင်ပါ", type="pdf")

if uploaded_file:
    st.markdown(f"<p style='color:#333333; font-weight:bold; font-size:13px;'>📄 ဖိုင်အမည်: {uploaded_file.name}</p>", unsafe_allow_html=True)
    st.divider()
    
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
    st.progress(0)
