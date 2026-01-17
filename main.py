import streamlit as st
from googletrans import Translator
import PyPDF2
from docx import Document
from io import BytesIO

# UI အလှဆင်ခြင်း
st.set_page_config(page_title="AI PDF Translator", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .main-title { color: #00BFFF; font-size: 40px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">English PDF To Myanmar (Google Translate)</p>', unsafe_allow_html=True)

translator = Translator()

def translate_text(text):
    try:
        # စာသားအရမ်းရှည်ရင် Google Translate က လက်မခံတတ်လို့ စာကြောင်းခွဲပြီး ပြန်ပေးပါမယ်
        translated = translator.translate(text, src='en', dest='my')
        return translated.text
    except Exception as e:
        return f"Error: {str(e)}"

uploaded_file = st.file_uploader("PDF ဖိုင်ရွေးပါ", type="pdf")

if uploaded_file and st.button("ဘာသာပြန်မည်"):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        bar = st.progress(0)
        num_pages = len(pdf_reader.pages)
        
        st.info("ဘာသာပြန်နေပါသည်။ ခဏစောင့်ပေးပါ...")
        
        for i in range(num_pages):
            text = pdf_reader.pages[i].extract_text()
            if text:
                # Google Translate ဖြင့် ဘာသာပြန်ခြင်း
                result = translate_text(text)
                
                doc.add_heading(f"Page {i+1}", level=2)
                doc.add_paragraph(result)
            
            bar.progress((i + 1) / num_pages)
        
        # Word File အဖြစ် ထုတ်ပေးခြင်း
        bio = BytesIO()
        doc.save(bio)
        st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
        st.download_button(
            label="Word ဖိုင်ရယူရန်",
            data=bio.getvalue(),
            file_name="Translated_Google.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        st.error(f"Error: {e}")
