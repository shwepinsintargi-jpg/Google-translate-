import streamlit as st
from deep_translator import GoogleTranslator
import PyPDF2
from docx import Document
from io import BytesIO
import re
import time

st.set_page_config(page_title="Stable PDF Translator", layout="centered")
st.title("English to Myanmar (Slow & Stable)")

def smart_translate(text):
    try:
        # စာကြောင်းအလိုက် ခွဲထုတ်ခြင်း
        sentences = re.split(r'(?<=[.!?]) +', text.replace('\n', ' '))
        translator = GoogleTranslator(source='en', target='my')
        
        translated_sentences = []
        for sentence in sentences:
            if sentence.strip():
                # တစ်ကြောင်းချင်းစီ ဘာသာပြန်ခြင်း
                res = translator.translate(sentence.strip())
                translated_sentences.append(res)
                # စာကြောင်းတစ်ကြောင်းပြန်ပြီးတိုင်း 0.5 စက္ကန့် ခဏနားခြင်း (Slow Translation)
                time.sleep(0.5) 
        
        return " ".join(translated_sentences)
    except Exception as e:
        return f"Error: {str(e)}"

uploaded_file = st.file_uploader("📄 PDF တင်ပါ", type="pdf")

if uploaded_file and st.button("🚀 ဘာသာပြန်မည်"):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        num_pages = len(pdf_reader.pages)
        bar = st.progress(0)
        status = st.empty()
        
        for i in range(num_pages):
            status.text(f"⏳ စာမျက်နှာ {i+1} ကို အသေးစိတ် ဘာသာပြန်နေပါသည်...")
            page_text = pdf_reader.pages[i].extract_text()
            if page_text and page_text.strip():
                result = smart_translate(page_text)
                doc.add_heading(f"Page {i+1}", level=2)
                doc.add_paragraph(result)
            bar.progress((i + 1) / num_pages)
            # စာမျက်နှာတစ်ခုပြီးတိုင်း ၁ စက္ကန့် ထပ်နားခြင်း
            time.sleep(1)

        bio = BytesIO()
        doc.save(bio)
        status.success("✅ အောင်မြင်စွာ ဘာသာပြန်ဆိုပြီးပါပြီ!")
        st.download_button("📥 Word ဖိုင်ရယူရန်", bio.getvalue(), "Stable_Translated.docx")
    except Exception as e:
        st.error(f"Error: {e}")
