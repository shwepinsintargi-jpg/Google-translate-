import streamlit as st
from deep_translator import GoogleTranslator
import PyPDF2
from docx import Document
from io import BytesIO
import re
import time
import json

# --- Page Config ---
st.set_page_config(page_title="AI Pro Translator", page_icon="📚", layout="centered")

# --- Custom Styling ---
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .main-title { color: #2E4053; text-align: center; font-size: 40px; font-weight: bold; margin-bottom: 10px; }
    .step-box { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #ddd; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 25px; height: 3.5em; background-image: linear-gradient(to right, #FF4B2B, #FF416C); color: white; border: none; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# --- Logic Functions ---
GLOSSARY_FILES = {
    "ရိုးရိုးဝတ္ထု (Drama/Novel)": "glossary_novel.json",
    "အက်ရှင်/စွန့်စားခန်း (Action/Adventure)": "glossary_action.json",
    "အထွေထွေဗဟုသုတ (General/Science)": "glossary_general.json",
    "စိုက်ပျိုးရေး (Agriculture)": "glossary_agri.json",
    "သင်္ချာ (Mathematics)": "glossary_math.json"
}

def load_glossary(category):
    filename = GLOSSARY_FILES.get(category)
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def improve_myanmar_text(myan_text, glossary):
    if not glossary:
        return myan_text
    
    # စကားလုံးအရှည်ဆုံး Phrases များကို အရင် အစားထိုးရန် (Longest Match First)
    sorted_keys = sorted(glossary.keys(), key=len, reverse=True)
    
    for eng_word in sorted_keys:
        myan_word = glossary[eng_word]
        # Google ရဲ့ မြန်မာပြန်ထဲမှာ ပါနေတဲ့ အင်္ဂလိပ်စာလုံး သို့မဟုတ် မှားနေတဲ့ မြန်မာစာလုံးကို လိုက်ပြင်ခြင်း
        # အင်္ဂလိပ်စာလုံးကျန်ခဲ့ရင်လည်း ပြင်မယ်၊ မြန်မာစာလုံးဆိုလည်း ပြန်ပြင်မယ်
        pattern = re.compile(re.escape(eng_word), re.IGNORECASE)
        myan_text = pattern.sub(myan_word, myan_text)
    
    return myan_text

def smart_translate(text, glossary):
    try:
        sentences = re.split(r'(?<=[.!?]) +', text.replace('\n', ' '))
        translator = GoogleTranslator(source='en', target='my')
        
        final_results = []
        for sentence in sentences:
            if sentence.strip():
                # ၁။ အရင်ဆုံး Google နဲ့ ပြန်တယ်
                translated = translator.translate(sentence.strip())
                # ၂။ ပြီးမှ Glossary နဲ့ တိုက်စစ်ပြီး အမှားပြင်တယ်
                final_fixed = improve_myanmar_text(translated, glossary)
                final_results.append(final_fixed)
                time.sleep(0.2)
        
        return " ".join(final_results)
    except Exception as e:
        return f"Error: {str(e)}"

# --- UI Interface ---
st.markdown("<h1 class='main-title'>📚 AI Book Translator Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #5D6D7E;'>နယ်ပယ်အလိုက် အကောင်းဆုံး မြန်မာဘာသာပြန်စနစ်</p>", unsafe_allow_html=True)

# Step 1: Genre Selection
st.markdown("<div class='step-box'>", unsafe_allow_html=True)
st.subheader("၁။ စာအုပ်အမျိုးအစား ရွေးချယ်ပါ")
selected_genre = st.selectbox("", list(GLOSSARY_FILES.keys()))
current_glossary = load_glossary(selected_genre)
st.write(f"✅ လက်ရှိ: **{selected_genre}** (စကားလုံးပေါင်း {len(current_glossary)} လုံးဖြင့် အလုပ်လုပ်မည်)")
st.markdown("</div>", unsafe_allow_html=True)

# Step 2: File Upload
st.markdown("<div class='step-box'>", unsafe_allow_html=True)
st.subheader("၂။ PDF ဖိုင် တင်သွင်းပါ")
uploaded_file = st.file_uploader("", type="pdf")
st.markdown("</div>", unsafe_allow_html=True)

# Process Button
if uploaded_file:
    if st.button("🚀 ဘာသာပြန်ခြင်း စတင်မည်"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        
        progress_bar = st.progress(0)
        status = st.empty()
        
        total_pages = len(pdf_reader.pages)
        full_translated_text = ""

        for i in range(total_pages):
            status.info(f"စာမျက်နှာ {i+1} ကို ဘာသာပြန်နေသည်...")
            raw_text = pdf_reader.pages[i].extract_text()
            
            if raw_text:
                translated = smart_translate(raw_text, current_glossary)
                doc.add_heading(f"Page {i+1}", level=2)
                doc.add_paragraph(translated)
            
            progress_bar.progress((i + 1) / total_pages)
        
        # Save & Download
        bio = BytesIO()
        doc.save(bio)
        status.success("🎉 ဘာသာပြန်ခြင်း အောင်မြင်စွာ ပြီးဆုံးပါပြီ!")
        st.balloons()
        
        st.download_button(
            label="📥 Word ဖိုင်ကို ဒေါင်းလုဒ်ဆွဲရန်",
            data=bio.getvalue(),
            file_name="Translated_Novel_Pro.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
