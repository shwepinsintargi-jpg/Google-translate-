import streamlit as st
from googletrans import Translator
import PyPDF2

st.set_page_config(page_title="PDF Translator", layout="wide")
st.title("🇲🇲 PDF to Myanmar Translator")

uploaded_file = st.file_uploader("PDF ဖိုင်ရွေးပါ", type="pdf")

if uploaded_file:
    if st.button("ဘာသာပြန်မည်"):
        translator = Translator()
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        full_text = ""
        bar = st.progress(0)
        num_pages = len(pdf_reader.pages)
        
        for i in range(num_pages):
            page = pdf_reader.pages[i]
            text = page.extract_text()
            if text:
                try:
                    res = translator.translate(text, src='en', dest='my')
                    full_text += f"--- Page {i+1} ---\n{res.text}\n\n"
                except:
                    full_text += f"--- Page {i+1} ---\n{text}\n\n"
            bar.progress((i + 1) / num_pages)
            
        st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
        st.download_button("ရလဒ်ရယူရန်", full_text, "translated.txt")

