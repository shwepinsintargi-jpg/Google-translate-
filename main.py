import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from io import BytesIO

# Secret ထဲကနေ Key ကို ဆွဲယူခြင်း
# (Box ထဲမှာ Key ထည့်စရာ မလိုတော့ပါ)
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("API Key မရှိသေးပါ။ Streamlit Settings တွင် အရင်ထည့်ပေးပါ")
    st.stop()

st.set_page_config(page_title="Auto AI Translator", layout="centered")
st.title("AI PDF Translator (Pro)")

def translate_with_groq(text):
    try:
        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional English-to-Myanmar translator."},
                {"role": "user", "content": f"Translate this: {text}"}
            ],
            model="llama-3.1-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

uploaded_file = st.file_uploader("📄 PDF ဖိုင်တင်ပါ", type="pdf")

if uploaded_file and st.button("🚀 ဘာသာပြန်မည်"):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    doc = Document()
    bar = st.progress(0)
    for i in range(len(pdf_reader.pages)):
        text = pdf_reader.pages[i].extract_text()
        if text:
            result = translate_with_groq(text)
            doc.add_heading(f"Page {i+1}", level=2)
            doc.add_paragraph(result)
        bar.progress((i + 1) / len(pdf_reader.pages))
    
    bio = BytesIO()
    doc.save(bio)
    st.success("ပြီးပါပြီ!")
    st.download_button("📥 Word ဖိုင်ရယူရန်", bio.getvalue(), "Translated.docx")
