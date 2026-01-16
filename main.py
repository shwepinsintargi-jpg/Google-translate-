import streamlit as st
from googletrans import Translator
import PyPDF2
from docx import Document
from io import BytesIO

st.set_page_config(page_title="PDF Translator", layout="wide")
st.title("🇲🇲 PDF to Myanmar Translator")

uploaded_file = st.file_uploader("PDF ဖိုင်ရွေးပါ", type="pdf")

if uploaded_file:
    if st.button("ဘာသာပြန်မည်"):
        translator = Translator()
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        doc.add_heading('Translated Content', 0)
        
        bar = st.progress(0)
        num_pages = len(pdf_reader.pages)
        
        for i in range(num_pages):
            page = pdf_reader.pages[i]
            text = page.extract_text()
            if text:
                try:
                    res = translator.translate(text, src='en', dest='my')
                    doc.add_heading(f'Page {i+1}', level=1)
                    doc.add_paragraph(res.text)
                except:
                    doc.add_paragraph(f"--- Page {i+1} (Translation Error) ---")
            bar.progress((i + 1) / num_pages)
            
        # Word ဖိုင်ကို Download လုပ်ရန် ပြင်ဆင်ခြင်း
        bio = BytesIO()
        doc.save(bio)
        st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
        st.download_button(
            label="Word ဖိုင်ဖြင့် ရယူရန်",
            data=bio.getvalue(),
            file_name="translated.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
