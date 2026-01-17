import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from io import BytesIO
import time

# --- Page Config ---
st.set_page_config(page_title="Elite PDF Translator", layout="wide")

# --- Luxury Styling (Refined Contrast) ---
st.markdown("""
    <style>
    /* Fixed Page Layout */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #FAFAFA !important;
        overflow: hidden;
        height: 100vh;
    }

    /* အပေါ်ဆုံးကပ်နေသော ခေါင်းစဉ် (Fixed Header) */
    .header-bar {
        position: fixed;
        top: 0; left: 0; width: 100%;
        background-color: #FFFFFF;
        border-bottom: 1px solid #EAEAEA;
        padding: 10px 0;
        text-align: center;
        z-index: 1000;
        color: #1A365D;
        font-size: 16px;
        font-weight: 500;
        letter-spacing: 1px;
    }

    /* Main UI Box */
    .container-box {
        max-width: 550px;
        margin: auto;
        margin-top: 80px; /* Header အောက် ရောက်စေရန် */
        background: white;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }

    /* File Name Box - သားနားသော ဒီဇိုင်း */
    .file-pill {
        background-color: #F1F5F9;
        border-left: 4px solid #1A365D;
        padding: 12px;
        border-radius: 4px;
        color: #1A365D;
        font-size: 14px;
        margin: 15px 0;
        animation: fadeIn 0.5s ease-in;
    }

    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

    /* Custom Button */
    .stButton>button {
        background-color: #1A365D !important;
        color: white !important;
        border: none !important;
        padding: 12px !important;
        font-size: 15px !important;
        border-radius: 6px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Logic: Groq & Model Fix ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ai_translate(text):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Professional Myanmar Academic Translator. High-end literary tone."},
                {"role": "user", "content": f"Translate: {text}"}
            ],
            model="llama-3.3-70b-versatile", # Model Error Fix
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# --- Layout Implementation ---

# ၁။ ခေါင်းစဉ် (Page အပေါ်ဆုံးတွင် ကပ်လျက်)
st.markdown('<div class="header-bar">(ENGLISH PDF မှ မြန်မာဘာသာသို့)</div>', unsafe_allow_html=True)

st.markdown('<div class="container-box">', unsafe_allow_html=True)

# ၂။ File Uploader
uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")

if uploaded_file:
    # ၃။ File Name ပြခြင်း (သားနားသော Pill box ဖြင့်)
    st.markdown(f'<div class="file-pill">📄 {uploaded_file.name}</div>', unsafe_allow_html=True)
    
    # ၄။ ဘာသာပြန်ရန် Button
    if st.button("ဘာသာပြန်ခြင်း စတင်မည်"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        total_pages = len(pdf_reader.pages)
        
        progress_info = st.empty()
        p_bar = st.progress(0)
        
        for i in range(total_pages):
            text = pdf_reader.pages[i].extract_text()
            if text.strip():
                time.sleep(1) # API Stability
                translated = ai_translate(text)
                doc.add_heading(f"Page {i+1}", level=2)
                doc.add_paragraph(translated)
            
            # Update Progress
            percent = int(((i + 1) / total_pages) * 100)
            p_bar.progress((i + 1) / total_pages)
            progress_info.markdown(f"<p style='text-align:center; font-size:13px;'>ဘာသာပြန်နေမှု: {percent}%</p>", unsafe_allow_html=True)

        st.success("ဘာသာပြန်ခြင်း ပြီးမြောက်ပါပြီ။")
        
        # ၅။ Download Button
        bio = BytesIO()
        doc.save(bio)
        st.download_button(
            label="📥 Word ဖိုင်ကို ရယူရန်",
            data=bio.getvalue(),
            file_name=f"Translated_{uploaded_file.name.replace('.pdf', '')}.docx"
        )

st.markdown('</div>', unsafe_allow_html=True)
