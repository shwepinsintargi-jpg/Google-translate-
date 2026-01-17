import streamlit as st
from deep_translator import GoogleTranslator
import PyPDF2
from docx import Document
from io import BytesIO
import re
import time
import json # JSON ဖိုင်ဖတ်ရန် ထပ်တိုးထားသည်

# ၁။ JSON ဖိုင်မှ Glossary ကို ဖတ်ယူခြင်း
def load_glossary():
    try:
        with open('glossary.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def apply_glossary(text, glossary):
    for wrong_word, correct_word in glossary.items():
        # စာလုံးအကြီးအသေးမရွေး ရှာပြီး အစားထိုးရန်
        pattern = re.compile(re.escape(wrong_word), re.IGNORECASE)
        text = pattern.sub(correct_word, text)
    return text

# --- ဘာသာပြန် Function ---
def smart_translate(text, glossary):
    try:
        sentences = re.split(r'(?<=[.!?]) +', text.replace('\n', ' '))
        translator = GoogleTranslator(source='en', target='my')
        
        translated_sentences = []
        for sentence in sentences:
            if sentence.strip():
                res = translator.translate(sentence.strip())
                # Glossary ဖြင့် စစ်ဆေးပြင်ဆင်ခြင်း
                res = apply_glossary(res, glossary)
                translated_sentences.append(res)
                time.sleep(0.3) 
        
        return " ".join(translated_sentences)
    except Exception as e:
        return f"Error: {str(e)}"

# --- UI ပိုင်း ---
st.title("Pro AI Translator (with JSON Glossary)")
glossary = load_glossary()

uploaded_file = st.file_uploader("📄 PDF တင်ပါ", type="pdf")
if uploaded_file and st.button("🚀 ဘာသာပြန်မည်"):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    doc = Document()
    bar = st.progress(0)
    
    for i in range(len(pdf_reader.pages)):
        text = pdf_reader.pages[i].extract_text()
        if text:
            result = smart_translate(text, glossary)
            doc.add_heading(f"Page {i+1}", level=2)
            doc.add_paragraph(result)
        bar.progress((i + 1) / len(pdf_reader.pages))
    
    bio = BytesIO()
    doc.save(bio)
    st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
    st.download_button("📥 Word ရယူရန်", bio.getvalue(), "Pro_Translated.docx")
