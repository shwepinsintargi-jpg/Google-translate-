import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from io import BytesIO

# Secret ထဲကနေ Key ကို ဆွဲယူခြင်း
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("API Key မရှိသေးပါ။ Streamlit Settings (Secrets) တွင် အရင်ထည့်ပေးပါ")
    st.stop()

st.set_page_config(page_title="AI PDF Translator", layout="centered")
st.title("AI PDF Translator (Llama 3.3)")

def translate_with_groq(text):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        # အသစ်ထွက်လာသော llama-3.3-70b-versatile ကို အသုံးပြုထားပါသည်
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional English-to-Myanmar translator. Translate fluently and naturally."
                },
                {
                    "role": "user", 
                    "content": f"Translate the following text into natural Myanmar: \n\n{text}"
                }
            ],
            model="llama-3.3-70b-specdec", # လက်ရှိ အသစ်ဆုံးနှင့် အမြန်ဆုံး Model ဖြစ်သည်
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

uploaded_file = st.file_uploader("📄 PDF ဖိုင်တင်ပါ", type="pdf")

if uploaded_file and st.button("🚀 ဘာသာပြန်မည်"):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        num_pages = len(pdf_reader.pages)
        bar = st.progress(0)
        
        st.info("AI ဘာသာပြန်နေပါသည်။ ခဏစောင့်ပေးပါ (VPN မလိုပါ)...")
        
        for i in range(num_pages):
            page_text = pdf_reader.pages[i].extract_text()
            if page_text.strip():
                result = translate_with_groq(page_text)
                doc.add_heading(f"Page {i+1}", level=2)
                doc.add_paragraph(result)
            bar.progress((i + 1) / num_pages)
        
        bio = BytesIO()
        doc.save(bio)
        st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
        st.download_button("📥 Word ဖိုင်ရယူရန်", bio.getvalue(), "Translated_Final.docx")
    except Exception as e:
        st.error(f"Error: {e}")
