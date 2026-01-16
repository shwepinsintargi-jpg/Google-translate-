import streamlit as st
from googletrans import Translator
import PyPDF2
from docx import Document
from io import BytesIO

st.set_page_config(page_title="PDF to Word Myanmar", layout="wide")
st.title("🇲🇲 PDF to Myanmar Word Translator")

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
                    res = translator.translate(text, src='en', dest='my')
                    result = res.text
                except:
                    result = text
                
                # စာမျက်နှာအလိုက် ခေါင်းစဉ်တပ်ခြင်း
                p = doc.add_paragraph()
                p.add_run(f"--- Page {i+1} ---").bold = True
                # ဘာသာပြန်စာသား ထည့်ခြင်း
                doc.add_paragraph(result)
            
            bar.progress((i + 1) / num_pages)
        
        # Word File ပြင်ဆင်ခြင်း
        bio = BytesIO()
        doc.save(bio)
        
        st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
        st.download_button(
            label="Word ဖိုင်ကို ရယူရန် (Download)",
            data=bio.getvalue(),
            file_name="translated_myanmar.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
