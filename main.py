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

# --- Custom CSS (Pure White & Black with Fixed Layout) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    .main .block-container { max-width: 500px; padding-top: 1rem; }

    /* စာပေအမျိုးအစားရွေးရန် နှင့် Dropdown ကို တစ်တန်းတည်းထားခြင်း */
    .flex-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 15px;
    }
    .genre-label {
        font-size: 16px;
        font-weight: bold;
        color: #000000 !important;
        white-space: nowrap;
    }

    /* စာသားအရောင်များ */
    h3, p, span, label, .stMarkdown { color: #000000 !important; }

    /* File Uploader Style */
    .stFileUploader section {
        background-color: #FFFFFF !important;
        border: 1.5px dashed #000000 !important;
        border-radius: 5px;
    }

    /* File Uploader Button */
    .stFileUploader section button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-size: 0 !important;
    }
    .stFileUploader section button::after {
        content: "ဖိုင်တင်ရန်";
        font-size: 14px !important;
        color: #FFFFFF !important;
    }

    /* --- ဘာသာပြန်ရန်ခလုတ် ပြင်ဆင်ချက် --- */
    .stButton>button {
        width: 100%;
        background-color: #000000 !important; /* နောက်ခံအနက် */
        color: #FFFFFF !important;           /* စာသားအဖြူ (သေချာပေါက်ပေါ်စေရန်) */
        border-radius: 5px !important;
        font-weight: bold !important;
        height: 3.2em;
        border: none !important;
        font-size: 16px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    /* ခလုတ်ပေါ်က စာသားကို Force လုပ်ပြီး အဖြူရောင်ပြောင်းခြင်း */
    .stButton>button p {
        color: #FFFFFF !important;
        margin: 0 !important;
    }

    .stProgress > div > div > div > div { background-color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Process Logic ---
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
    except: return text

def play_notification_sound():
    sound_url = "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"
    sound_html = f"<audio autoplay><source src='{sound_url}' type='audio/mp3'></audio>"
    st.components.v1.html(sound_html, height=0)

GLOSSARY_FILES = {
    "ရိုးရိုးဝတ္ထု": "glossary_novel.json",
    "အက်ရှင်": "glossary_action.json",
    "အထွေထွေ": "glossary_general.json",
    "သင်္ချာ": "glossary_math.json",
    "သိပ္ပံ": "glossary_science.json"
}

# --- UI Setup ---

# ၁။ စာပေအမျိုးအစားကို တစ်တန်းတည်းထားခြင်း
col1, col2 = st.columns([1.2, 1])
with col1:
    st.markdown("<p style='margin-top:10px; font-weight:bold;'>📖 စာပေအမျိုးအစားရွေးချယ်ရန်</p>", unsafe_allow_html=True)
with col2:
    selected_genre = st.selectbox("", list(GLOSSARY_FILES.keys()), label_visibility="collapsed")

# ၂။ File Upload
uploaded_file = st.file_uploader("ဘာသာပြန်မည့် file တင်ပါ", type="pdf")

if uploaded_file:
    st.markdown(f"**📄 ဖိုင်အမည်:** {uploaded_file.name}")
    st.write("---")
    
    # ၃။ ဘာသာပြန်ခလုတ် (စာသားသေချာပေါ်အောင် လုပ်ထားသည်)
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
