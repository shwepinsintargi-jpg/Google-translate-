import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from io import BytesIO
import time

# --- Page Config ---
st.set_page_config(page_title="PDF Translator", layout="wide")

# --- UI Styling (Fixed & High Contrast) ---
st.markdown("""
    <style>
    /* Page ကို မလှုပ်အောင် Fix လုပ်ခြင်း */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
        overflow: hidden; 
        height: 100vh;
    }
    
    /* Title - Page ရဲ့ အပေါ်ဆုံးမှာ တကြောင်းတည်း */
    .title-text {
        color: #1A365D;
        font-size: 24px;
        font-weight: 800;
        text-align: center;
        padding-top: 20px;
        margin-bottom: 30px;
        border-bottom: 2px solid #F0F2F5;
    }

    /* အလယ်က Main Container */
    .main-box {
        max-width: 600px;
        margin: auto;
        padding: 20px;
    }

    /* Button Styling */
    .stButton>button {
        width: 100%;
        background-color: #1A365D !important;
        color: white !important;
        border-radius: 8px !important;
        height: 3.5em;
        font-weight: bold;
        border: none;
    }

    /* Progress Bar Color */
    .stProgress > div > div > div > div { background-color: #1A365D !important; }
    
    /* File Name Display */
    .file-info {
        background-color: #F8F9FA;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        color: #1A365D;
        font-weight: 500;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Logic: Groq Configuration ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ai_translate(text):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Professional Myanmar Academic Translator. Formal literary tone."},
                {"role": "user", "content": f"Translate: {text}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# --- Layout ---

# ၁။ ခေါင်းစဉ် (Page ရဲ့ အပေါ်ဆုံးမှာ တကြောင်းတည်း)
st.markdown('<div class="title-text">(English PDF မှ မြန်မာဘာသာသို့)</div>', unsafe_allow_html=True)

st.markdown('<div class="main-box">', unsafe_allow_html=True)

# ၂။ File တင်မယ့် Button
uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")

# ၃။ File တင်ပြီးပါက File Name ပြခြင်း
if uploaded_file is not None:
    st.markdown(f'<div class="file-info">📄 {uploaded_file.name}</div>', unsafe_allow_html=True)
    st.write("")
    
    # ၄။ ဘာသာပြန်ရန် Button
    if st.button("ဘာသာပြန်ရန်"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        total_pages = len(pdf_reader.pages)
        
        # ၅။ % ပြတဲ့ Progress Bar
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        for i in range(total_pages):
            page_text = pdf_reader.pages[i].extract_text()
            if page_text.strip():
                time.sleep(1) # ၁ စက္ကန့်နားစနစ်
                translated = ai_translate(page_text)
                doc.add_heading(f"Page {i+1}", level=2)
                doc.add_paragraph(translated)
            
            # Update %
            percent = int(((i + 1) / total_pages) * 100)
            progress_bar.progress((i + 1) / total_pages)
            progress_text.markdown(f"<p style='text-align:center;'>ဘာသာပြန်ပြီးစီးမှု: {percent}%</p>", unsafe_allow_html=True)

        # ၆။ Download Button
        bio = BytesIO()
        doc.save(bio)
        st.write("")
        st.download_button(
            label="📥 Download Word File",
            data=bio.getvalue(),
            file_name=f"Translated_{uploaded_file.name.replace('.pdf', '')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

st.markdown('</div>', unsafe_allow_html=True)
