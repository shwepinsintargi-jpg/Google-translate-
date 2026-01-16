import streamlit as st
from googletrans import Translator
import PyPDF2
from docx import Document
from io import BytesIO

st.set_page_config(page_title="PDF Myanmar Translator", layout="wide")
st.title("🇲🇲 PDF to Myanmar (Easy Version)")

uploaded_file = st.file_uploader("PDF ဖိုင်ရွေးပါ", type="pdf")

if uploaded_file:
    if st.button("ဘာသာပြန်မည်"):
        translator = Translator()
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        
        bar = st.progress(0)
        num_pages = len(pdf_reader.pages)
        
        for i in range(num_pages):
            page = pdf_reader.pages[i]
            text = page.extract_text()
            
            if text:
                try:
                    # စာသားတွေကို သန့်ရှင်းအောင်လုပ်ပြီး စာပိုဒ်လိုက်ပြန်ခိုင်းခြင်း
                    clean_text = text.replace('\n', ' ') 
                    res = translator.translate(clean_text, src='en', dest='my')
                    result = res.text
                except:
                    result = text
                
                # စာမျက်နှာ ခေါင်းစဉ်တပ်ခြင်း
                p = doc.add_paragraph()
                run = p.add_run(f"--- Page {i+1} ---")
                run.bold = True
                doc.add_paragraph(result)
            
            bar.progress((i + 1) / num_pages)
        
        bio = BytesIO()
        doc.save(bio)
        st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
        st.download_button("Word ဖိုင်ကို ရယူရန်", bio.getvalue(), "translated_myanmar.docx")
