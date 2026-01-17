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

# --- Custom CSS (Fixed Layout & Professional UI) ---
st.markdown("""
    <style>
    /* Fixed Layout & Global Font Size */
    .main .block-container { max-width: 500px; padding-top: 1rem; font-size: 14px; }
    
    /* Genre Title Style */
    .genre-title {
        display: inline-block;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 0px;
        white-space: nowrap;
        color: #1E1E1E !important;
    }

    /* File Uploader အစိမ်းနုရောင် နောက်ခံ နှင့် စာသားများ */
    .stFileUploader section {
        background-color: #D1FFD7 !important; 
        border: 2px dashed #2E86C1 !important;
        border-radius: 10px;
        padding: 5px;
    }
    
    /* Browse files စာသားကို မြန်မာလို အစားထိုးခြင်း */
    .stFileUploader section button {
        font-size: 0 !important;
    }
    .stFileUploader section button::after {
        content: "ဖိုင်တင်ရန်";
        font-size: 14px !important;
        color: white;
    }
    
    /* Upload Label Color */
    .stFileUploader label {
        color: #1A5276 !important; 
        font-weight: bold;
        font-size: 15px !important;
        display: block;
        margin-bottom: 10px;
    }

    /* စာသားများ အနက်ရောင်ပြောင်းခြင်း (အဖြူပေါ်တွင် မြင်သာစေရန်) */
    p, span, label, .stMarkdown {
        color: #1E1E1E !important;
    }

    /* Button Style */
    .stButton>button { 
        width: 100%; 
        border-radius: 10px; 
        font-weight: bold; 
        height: 2.8em; 
        background-color: #2E86C1; 
        color: white; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- Formula & Chemical Symbol Protection Logic ---
def smart_process(text, glossary):
    # ၁။ သင်္ချာဖော်မြူလာများ သို့မဟုတ် ဓာတုဗေဒသင်္ကေတများ (ဥပမာ- CO2, H2O, O2) ကို ရှာဖွေခြင်း
    # သင်္ကေတများ (+, -, =, *, /, ^, <, >) သို့မဟုတ် ဂဏန်းပါသော ဓာတုသင်္ကေတများပါလျှင် မူရင်းအတိုင်းထားမည်
    if re.search(r'[=+*/\^<>]', text) or re.search(r'\b[A-Z][a-z]?\d+\b', text):
        return text

    try:
        # ၂။ Google Translate ဖြင့် ဘာသာပြန်ခြင်း
        translated = GoogleTranslator(source='en', target='my').translate(text)
        
        # ၃။ Glossary ဖြင့် အချောသတ်ခြင်း
        if glossary:
            # စကားလုံးအရှည်ဆုံးများကို အရင်အစားထိုးရန်
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
uploaded_file = st.file_uploader("ဘာသာပြန်မည့် file တင်ပါ", type="pdf")

if uploaded_file:
    # ဖိုင်တင်ပြီးသွားလျှင် နာမည်ကို အနက်ရောင်ဖြင့်ပြခြင်း
    st.markdown(f"<p style='color:#1E1E1E; font-weight:bold; font-size:13px;'>📄 ဖိုင်: {uploaded_file.name}</p>", unsafe_allow_html=True)
    
    st.write("---")
    
    if st.button("စတင်ဘာသာပြန်ပါ"):
        with st.status("Professional Processing...", expanded=True) as status:
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
                st.write(f"➡️ စာမျက်နှာ {i+1} ကို အချောသတ်နေသည်...")
                page_text = pdf_reader.pages[i].extract_text()

                if page_text:
                    # စာကြောင်းများကို ဇယားပုံစံမပျက်စေရန် တစ်ကြောင်းချင်းစီ စစ်ဆေးသည်
                    lines = page_text.split('\n')
                    doc.add_heading(f"Page {i+1}", level=2)
                    
                    for line in lines:
                        if line.strip():
                            # Formula & Chemical Protection ပါဝင်သော Logic ကို သုံးသည်
                            processed_line = smart_process(line.strip(), glossary)
                            doc.add_paragraph(processed_line)
                
                progress_bar.progress((i + 1) / total_pages)
                time.sleep(0.05)

            status.update(label="✅ ဘာသာပြန်ခြင်း ပြီးဆုံးပါပြီ!", state="complete")
            play_notification_sound()
            
            # Download Button
            bio = BytesIO()
            doc.save(bio)
            st.download_button(
                label="📥 Word file ဒေါင်းရန်",
                data=bio.getvalue(),
                file_name=f"Final_Translated_{selected_genre}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
else:
    # ဖိုင်မတင်ရသေးလျှင် Progress Bar အလွတ်ပြထားမည်
    st.progress(0)
