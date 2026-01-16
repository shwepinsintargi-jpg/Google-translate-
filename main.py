import streamlit as st
from googletrans import Translator
import PyPDF2
from docx import Document
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="PDF Translator", layout="wide")
st.title("🇲🇲 PDF to Myanmar (Word/PDF)")

uploaded_file = st.file_uploader("PDF ဖိုင်ရွေးပါ", type="pdf")

if uploaded_file:
    if st.button("ဘာသာပြန်မည်"):
        translator = Translator()
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        
        # စာရွက်စာတမ်းများ ပြင်ဆင်ခြင်း
        doc = Document()
        pdf_out = FPDF()
        pdf_out.add_page()
        pdf_out.set_font("Helvetica", size=12) # Standard Font သုံးခြင်း
        
        bar = st.progress(0)
        num_pages = len(pdf_reader.pages)
        
        full_text = ""
        for i in range(num_pages):
            page = pdf_reader.pages[i]
            text = page.extract_text()
            if text:
                try:
                    res = translator.translate(text, src='en', dest='my')
                    result = res.text
                except:
                    result = text
                
                # Word ထဲထည့်ခြင်း
                doc.add_heading(f'Page {i+1}', level=1)
                doc.add_paragraph(result)
                
                # PDF ထဲထည့်ရန် စာသားစုဆောင်းခြင်း
                full_text += f"\n--- Page {i+1} ---\n{result}\n"
            
            bar.progress((i + 1) / num_pages)
        
        st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
        
        col1, col2 = st.columns(2)
        
        # --- Word Download ---
        bio_word = BytesIO()
        doc.save(bio_word)
        with col1:
            st.download_button("Word ဖိုင်ဖြင့် ရယူရန်", bio_word.getvalue(), "translated.docx")
            
        # --- PDF Download (Error ပြင်ဆင်ပြီး) ---
        try:
            pdf_out.multi_cell(0, 10, txt=full_text.encode('latin-1', 'replace').decode('latin-1'))
            pdf_bytes = pdf_out.output() # fpdf2 version အသစ်အတွက် ပြင်ထားသည်
            with col2:
                st.download_button("PDF ဖိုင်ဖြင့် ရယူရန်", bytes(pdf_bytes), "translated.pdf", "application/pdf")
        except:
            with col2:
                st.info("PDF ထုတ်ရန် အခက်အခဲရှိပါက Word ကို အရင်ယူပါ")
