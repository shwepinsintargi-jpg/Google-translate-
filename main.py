import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from io import BytesIO
import time
import json
import os

# --- Page Config ---
st.set_page_config(page_title="Professional PDF Translator", layout="wide")

# --- UI Styling (Fixed & High Contrast) ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
        overflow: hidden; 
        height: 100vh;
    }
    .top-header {
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #FFFFFF;
        border-bottom: 1px solid #E2E8F0;
        padding: 8px 0;
        text-align: center;
        color: #1A365D;
        font-size: 16px;
        font-weight: 500;
        z-index: 1000;
    }
    .main-container {
        max-width: 500px;
        margin: auto;
        padding-top: 60px;
    }
    .stButton>button {
        width: 100%;
        background-color: #1A365D !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600;
    }
    .file-pill {
        background-color: #F8F9FA;
        border-left: 5px solid #1A365D;
        padding: 10px;
        border-radius: 4px;
        color: #1A365D;
        margin: 15px 0;
        font-size: 14px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- JSON မှ သင်ကြားမှုဒေတာများ ဖတ်ခြင်း ---
def get_teaching_context():
    if os.path.exists("teaching_data.json"):
        with open("teaching_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            context = "Learn from these professional examples:\n"
            for ex in data.get("examples", []):
                context += f"English: {ex['english']} -> Myanmar: {ex['myanmar']}\n"
            context += f"\nRule: {data.get('style_instructions', '')}"
            return context
    return "Translate English to Myanmar formally and naturally."

# --- Groq Logic ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ai_translate(text):
    teaching_context = get_teaching_context()
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"You are an elite Myanmar translator. {teaching_context}"},
                {"role": "user", "content": f"Translate this PDF content: {text}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# --- UI Execution ---
st.markdown('<div class="top-header">(English PDF မှ မြန်မာဘာသာသို့)</div>', unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")

if uploaded_file:
    st.markdown(f'<div class="file-pill">📄 {uploaded_file.name}</div>', unsafe_allow_html=True)
    
    if st.button("ဘာသာပြန်ခြင်း စတင်မည်"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        total_pages = len(pdf_reader.pages)
        
        prog_text = st.empty()
        prog_bar = st.progress(0)
        
        for i in range(total_pages):
            text = pdf_reader.pages[i].extract_text()
            if text.strip():
                time.sleep(1) # API Stability
                translated = ai_translate(text)
                doc.add_heading(f"Page {i+1}", level=2)
                doc.add_paragraph(translated)
            
            percent = int(((i + 1) / total_pages) * 100)
            prog_bar.progress((i + 1) / total_pages)
            prog_text.markdown(f"<p style='text-align:center;'>တိုးတက်မှုအခြေအနေ: {percent}%</p>", unsafe_allow_html=True)

        st.success("ဘာသာပြန်ခြင်း ပြီးမြောက်ပါပြီ!")
        
        bio = BytesIO()
        doc.save(bio)
        st.download_button(
            label="📥 Word ဖိုင်ကို ရယူရန်",
            data=bio.getvalue(),
            file_name=f"Translated_{uploaded_file.name.replace('.pdf', '')}.docx"
        )

st.markdown('</div>', unsafe_allow_html=True)
