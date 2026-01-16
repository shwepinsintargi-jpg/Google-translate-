import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from io import BytesIO

st.set_page_config(page_title="Groq AI Translator", layout="wide")
st.title("🚀 Groq AI PDF Myanmar Translator")

# Groq API Key ထည့်ရန်
api_key = st.text_input("Groq API Key ထည့်ပါ (VPN မလိုပါ)", type="password")

if api_key:
    client = Groq(api_key=api_key)
    uploaded_file = st.file_uploader("PDF ဖိုင်ရွေးပါ", type="pdf")

    if uploaded_file and st.button("AI ဖြင့် ဘာသာပြန်မည်"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        
        bar = st.progress(0)
        num_pages = len(pdf_reader.pages)
        
        for i in range(num_pages):
            text = pdf_reader.pages[i].extract_text()
            if text:
                try:
                    # Groq AI ကို ဘာသာပြန်ခိုင်းခြင်း
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are a professional translator. Translate English to Myanmar language naturally and fluently."},
                            {"role": "user", "content": f"Translate this: {text}"}
                        ],
                    )
                    result = completion.choices[0].message.content
                    
                    doc.add_heading(f'Page {i+1}', level=1)
                    doc.add_paragraph(result)
                except Exception as e:
                    st.error(f"Error: {e}")
            
            bar.progress((i + 1) / num_pages)
        
        bio = BytesIO()
        doc.save(bio)
        st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
        st.download_button("Word ဖိုင်ရယူရန်", bio.getvalue(), "groq_translated.docx")
else:
    st.info("ဆက်လက်လုပ်ဆောင်ရန် Groq API Key ကို ထည့်ပေးပါ")
