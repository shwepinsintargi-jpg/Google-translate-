import streamlit as st
from deep_translator import GoogleTranslator
import PyPDF2
from docx import Document
from io import BytesIO
import re
import time
import json

# ၁။ Glossary JSON ဖိုင်နာမည်များကို ချိတ်ဆက်ခြင်း
GLOSSARY_FILES = {
    "General (အထွေထွေ)": "glossary_general.json",
    "Novel Style (ရိုးရိုးဝတ္ထု)": "glossary_novel.json",
    "Action/Fantasy (အက်ရှင်)": "glossary_action.json",
    "Agriculture (စိုက်ပျိုးရေး)": "glossary_agri.json"
}

def load_glossary(category):
    filename = GLOSSARY_FILES.get(category)
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # ဖိုင်မရှိသေးလျှင် Error မတက်ဘဲ အလွတ်ပြရန်
        return {}

def apply_glossary(text, glossary):
    if not glossary:
        return text
    # စကားလုံးအရှည်ကို အရင်စစ်၍ အစားထိုးခြင်း
    sorted_keys = sorted(glossary.keys(), key=len, reverse=True)
    for eng_word in sorted_keys:
        myan_word = glossary[eng_word]
        # Regex သုံး၍ စာလုံးအကြီးအသေးမရွေး ရှာဖွေအစားထိုးခြင်း
        pattern = re.compile(re.escape(eng_word), re.IGNORECASE)
        text = pattern.sub(myan_word, text)
    return text

def smart_translate(text, glossary):
    try:
        sentences = re.split(r'(?<=[.!?]) +', text.replace('\n', ' '))
        translator = GoogleTranslator(source='en', target='my')
        
        translated_sentences = []
        for sentence in sentences:
            if sentence.strip():
                res = translator.translate(sentence.strip())
                # ရွေးချယ်ထားသော JSON glossary ဖြင့် အမှားပြင်ခြင်း
                res = apply_glossary(res, glossary)
                translated_sentences.append(res)
                time.sleep(0.3) 
        
        return " ".join(translated_sentences)
    except Exception as e:
        return f"Error: {str(e)}"

# --- UI Setup ---
st.set_page_config(page_title="Professional Translator", layout="centered")
st.title("📚 AI Translator (Multi-Genre)")

# Sidebar တွင် JSON ဖိုင်များကို ရွေးချယ်ခိုင်းခြင်း
with st.sidebar:
    st.header("Glossary Settings")
    selected_category = st.selectbox("နယ်ပယ်ရွေးချယ်ပါ", list(GLOSSARY_FILES.keys()))
    
    # ရွေးထားသော ဖိုင်ကို Load လုပ်ခြင်း
    current_glossary = load_glossary(selected_category)
    
    st.success(f"လက်ရှိ: {selected_category}")
    st.write(f"စကားလုံးပေါင်း: {len(current_glossary)}")

# Main Interface
uploaded_file = st.file_uploader("📄 ဘာသာပြန်မည့် PDF တင်ပါ", type="pdf")

if uploaded_file and st.button("🚀 ဘာသာပြန်မည်"):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    doc = Document()
    progress_bar = st.progress(0)
    
    for i in range(len(pdf_reader.pages)):
        text = pdf_reader.pages[i].extract_text()
        if text:
            result = smart_translate(text, current_glossary)
            doc.add_heading(f"Page {i+1}", level=2)
            doc.add_paragraph(result)
        progress_bar.progress((i + 1) / len(pdf_reader.pages))
    
    bio = BytesIO()
    doc.save(bio)
    st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
    st.download_button("📥 Word ရယူရန်", bio.getvalue(), "Translated_Novel.docx")
