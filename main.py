import streamlit as st
from googletrans import Translator
import PyPDF2
from docx import Document
from io import BytesIO

st.title("🌐 Google PDF Translator")

# Translator Setup
translator = Translator()

uploaded_file = st.file_uploader("PDF ဖိုင် တင်ပါ", type="pdf")

if uploaded_file:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    translated_doc = Document()
    
    if st.button("ဘာသာပြန်မည်"):
        progress_bar = st.progress(0)
        num_pages = len(pdf_reader.pages)
        
        for i in range(num_pages):
            page_text = pdf_reader.pages[i].extract_text()
            if page_text:
                # English to Myanmar ပြန်ခြင်း
                result = translator.translate(page_text, src='en', dest='my')
                translated_doc.add_paragraph(result.text)
            
            progress_bar.progress((i + 1) / num_pages)
            st.write(f"✅ Page {i+1} ပြီးပါပြီ")

        # Download Button
        bio = BytesIO()
        translated_doc.save(bio)
        st.download_button("📥 Word ဖိုင်ရယူရန်", data=bio.getvalue(), file_name="translated.docx")
