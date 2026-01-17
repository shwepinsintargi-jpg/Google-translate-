import streamlit as st
from deep_translator import GoogleTranslator
import PyPDF2
from docx import Document
from io import BytesIO
import re

# UI အလှဆင်ခြင်း
st.set_page_config(page_title="PDF Translator (Stable)", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-title { color: #00BFFF; font-size: 40px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">English PDF To Myanmar (Optimized)</p>', unsafe_allow_html=True)

def smart_translate(text):
    try:
        # စာသားကို စာကြောင်းအလိုက် ခွဲထုတ်ခြင်း (ပိုမိုတိကျသော ဘာသာပြန်မှုရရန်)
        sentences = re.split(r'(?<=[.!?]) +', text)
        translated_sentences = []
        
        translator = GoogleTranslator(source='en', target='my')
        
        for sentence in sentences:
            if sentence.strip():
                # တစ်ကြောင်းချင်းစီ ဘာသာပြန်ခြင်း
                res = translator.translate(sentence)
                translated_sentences.append(res)
        
        return " ".join(translated_sentences)
    except Exception as e:
        return f"Translation Error: {str(e)}"

uploaded_file = st.file_uploader("📄 ဘာသာပြန်လိုသော PDF ကို တင်ပါ", type="pdf")

if uploaded_file and st.button("🚀 ဘာသာပြန်မည်"):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        num_pages = len(pdf_reader.pages)
        
        progress_text = st.empty()
        bar = st.progress(0)
        
        st.info("Google Translate ဖြင့် အဆင့်မြှင့်တင် ဘာသာပြန်နေပါသည်။ ခဏစောင့်ပေးပါ...")
        
        for i in range(num_pages):
            progress_text.text(f"⏳ စာမျက်နှာ {i+1} ကို လုပ်ဆောင်နေပါသည်...")
            page_text = pdf_reader.pages[i].extract_text()
            
            if page_text.strip():
                # Smart Translation ခေါ်ယူခြင်း
                result = smart_translate(page_text)
                
                doc.add_heading(f"Page {i+1}", level=2)
                doc.add_paragraph(result)
            
            bar.progress((i + 1) / num_pages)
        
        bio = BytesIO()
        doc.save(bio)
        st.success("✅ ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
        st.download_button(
            label="📥 Word ဖိုင်ရယူရန်",
            data=bio.getvalue(),
            file_name="Optimized_Translated.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        st.error(f"Error: {e}")
