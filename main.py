import streamlit as st
from deep_translator import GoogleTranslator
import PyPDF2
from docx import Document
from io import BytesIO
import time
import json

# --- Page Config ---
st.set_page_config(page_title="AI Translator", layout="centered")

# --- Custom CSS (Layout & Font Adjustments) ---
st.markdown("""
    <style>
    /* Fixed Layout & Global Font Size */
    .main .block-container { max-width: 500px; padding-top: 1rem; font-size: 14px; }
    
    /* စာပေအမျိုးအစားရွေးရန် ကို တစ်တန်းတည်း ဖြစ်စေခြင်း */
    .genre-title {
        display: inline-block;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 0px;
        white-space: nowrap;
    }

    /* File Uploader အစိမ်းနုရောင် နောက်ခံ နှင့် စာသားများ */
    .stFileUploader section {
        background-color: #D1FFD7 !important; 
        border: 2px dashed #2E86C1 !important;
        border-radius: 10px;
        padding: 5px;
    }
    
    /* Browse files စာသားကို ဖျောက်ပြီး မြန်မာလို အစားထိုးခြင်း */
    .stFileUploader section button {
        font-size: 0 !important;
    }
    .stFileUploader section button::after {
        content: "ဖိုင်တင်ရန်";
        font-size: 14px !important;
        color: white;
    }
    
    /* Upload စာသားကို အပြာရောင် ပီပီသသ ပြခြင်း */
    .stFileUploader label {
        color: #1A5276 !important; 
        font-weight: bold;
        font-size: 15px !important;
        display: block;
        margin-bottom: 10px;
    }

    /* အဖြူရောင်နောက်ခံပေါ်တွင် စာသားများ မမြင်ရသည့် ပြဿနာအတွက် */
    p, span, label {
        color: #1E1E1E !important; /* အနက်ရောင် သို့မဟုတ် မီးခိုးရင့်ရောင် */
    }

    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 2.8em; }
    </style>
    """, unsafe_allow_html=True)

# --- Sound Function ---
def play_notification_sound():
    sound_url = "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"
    sound_html = f"<audio autoplay><source src='{sound_url}' type='audio/mp3'></audio>"
    st.components.v1.html(sound_html, height=0)

# --- Logic ---
GLOSSARY_FILES = {
    "ရိုးရိုးဝတ္ထု": "glossary_novel.json",
    "အက်ရှင်": "glossary_action.json",
    "အထွေထွေ": "glossary_general.json",
    "သင်္ချာ": "glossary_math.json",
"သိပ္ပံ": "glossary_science.json"
}

# --- UI Layout ---

# 1. Genre Selection (Title နှင့် Dropdown ကို တစ်တန်းတည်း နီးပါးဖြစ်အောင် ညှိထားသည်)
st.markdown("<p class='genre-title'>📖 စာပေအမျိုးအစားရွေးရန်</p>", unsafe_allow_html=True)
selected_genre = st.selectbox("", list(GLOSSARY_FILES.keys()), label_visibility="collapsed")

# 2. File Upload Area
uploaded_file = st.file_uploader("ဘာသာပြန်မည့် file တင်ပါ", type="pdf")

if uploaded_file:
    # ဖိုင်တင်ပြီးသွားလျှင် နာမည်ပြခြင်း (စာလုံးအရွယ်အစား လျှော့ထားသည်)
    st.markdown(f"<p style='color:#1E1E1E; font-weight:bold; font-size:13px;'>📄 ဖိုင်: {uploaded_file.name}</p>", unsafe_allow_html=True)
    
    st.write("---")
    
    if st.button("စတင်ဘာသာပြန်ပါ"):
        with st.status(f"ဘာသာပြန်နေသည်...", expanded=True) as status:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            doc = Document()
            
            # Glossary Load
            try:
                with open(GLOSSARY_FILES[selected_genre], 'r', encoding='utf-8') as f:
                    glossary = json.load(f)
            except: glossary = {}
            
            total_pages = len(pdf_reader.pages)
            progress_bar = st.progress(0)
            
            for i in range(total_pages):
                st.write(f"➡️ စာမျက်နှာ {i+1} ပြီးစီး...")
                page_text = pdf_reader.pages[i].extract_text()
                
                if page_text:
                    translated = GoogleTranslator(source='en', target='my').translate(page_text)
                    for eng, myan in glossary.items():
                        translated = translated.replace(eng, myan)
                    doc.add_heading(f"Page {i+1}", level=2)
                    doc.add_paragraph(translated)
                
                progress_bar.progress((i + 1) / total_pages)
                time.sleep(0.1)
            
            status.update(label="✅ ပြီးဆုံးပါပြီ!", state="complete")
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
