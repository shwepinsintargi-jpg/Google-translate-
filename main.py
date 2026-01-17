import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from io import BytesIO
import time # အချိန်နားရန်အတွက်

# --- Page Config ---
st.set_page_config(page_title="Professional PDF Translator", layout="wide")

# --- UI Styling (Fixed One-Page Contrast Style) ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #F8F9FA !important; }
    .main-card {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        max-width: 900px;
        margin: auto;
        margin-top: 2vh;
        border-top: 8px solid #1A365D;
    }
    .preview-box {
        background-color: #1A365D; /* အပြာရင့်နောက်ခံ (သားနားစေရန်) */
        color: #FFFFFF !important; /* အဖြူရောင်စာသား (ပြတ်သားစေရန်) */
        border-radius: 12px;
        padding: 25px;
        height: 350px;
        overflow-y: auto;
        font-family: 'Pyidaungsu', sans-serif;
        line-height: 1.8;
        font-size: 1.1rem;
        margin-top: 20px;
        border: 2px solid #E2E8F0;
    }
    h1 { color: #1A365D !important; text-align: center; font-weight: 800; }
    .stProgress > div > div > div > div { background-color: #1A365D !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Groq Logic ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def ai_translate(text):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a senior Myanmar academic translator. Translate formal English into literary Myanmar with natural flow."},
                {"role": "user", "content": f"Translate this text: {text}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# --- Layout ---
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown("<h1>English PDF into Myanmar</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>အဆင့်မြင့် ဉာဏ်ရည်တုစနစ်ဖြင့် သပ်ရပ်စွာ ဘာသာပြန်ဆိုခြင်း</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("PDF ဖိုင်ကို ဤနေရာတွင် တင်ပါ", type="pdf")

if uploaded_file:
    if st.button("ဘာသာပြန်ခြင်း စတင်ပါ"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        full_translated_text = ""
        
        status_text = st.empty()
        progress_bar = st.progress(0)
        preview_container = st.empty() # Preview စာသားများ ထည့်ရန် နေရာလွတ်

        total_pages = len(pdf_reader.pages)

        for i in range(total_pages):
            page_text = pdf_reader.pages[i].extract_text()
            
            if page_text.strip():
                # ၁ စက္ကန့် နားသည့် စနစ် (Cool down for API)
                time.sleep(1)
                
                translated = ai_translate(page_text)
                
                # စုစည်းမှု
                doc.add_heading(f"Page {i+1}", level=2)
                doc.add_paragraph(translated)
                full_translated_text += f"--- Page {i+1} ---\n{translated}\n\n"
                
                # Preview ကို Live update လုပ်ခြင်း
                preview_container.markdown(f'<div class="preview-box">{full_translated_text}</div>', unsafe_allow_html=True)
                
            # Progress Update
            progress = (i + 1) / total_pages
            progress_bar.progress(progress)
            status_text.markdown(f"<p style='text-align:center; color:#1A365D;'><b>စာမျက်နှာ {i+1} ကို အောင်မြင်စွာ ဘာသာပြန်ပြီးပါပြီ ({int(progress*100)}%)</b></p>", unsafe_allow_html=True)

        st.success("✅ ဘာသာပြန်ခြင်း လုပ်ငန်းစဉ် ပြီးဆုံးပါပြီ!")
        
        # Download Button
        bio = BytesIO()
        doc.save(bio)
        st.download_button(
            label="📥 ဘာသာပြန်ထားသော Word ဖိုင်ကို ရယူရန်",
            data=bio.getvalue(),
            file_name="Professional_Translated.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

st.markdown('</div>', unsafe_allow_html=True)
