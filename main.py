import streamlit as st
import groq
from googletrans import Translator
import PyPDF2
from docx import Document
from io import BytesIO
import time
import json
import os

# --- Page Setup ---
st.set_page_config(page_title="Professional Hybrid Translator", layout="wide")

# --- UI Styling ---
st.markdown("""
    <style>
    .main-box { max-width: 600px; margin: auto; padding-top: 50px; }
    .stButton>button { width: 100%; background-color: #1A365D; color: white; border-radius: 8px; }
    .status-box { padding: 10px; border-radius: 5px; margin-bottom: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- Logic Setup ---
client = groq.Groq(api_key=st.secrets["GROQ_API_KEY"])
google_translator = Translator()

def translate_engine(text, direction):
    # ဘာသာပြန်ဦးတည်ချက် သတ်မှတ်ခြင်း
    if direction == "English to Myanmar":
        src_lang, dest_lang, system_role = "en", "my", "professional Myanmar translator"
    else:
        src_lang, dest_lang, system_role = "my", "en", "professional English translator"

    try:
        # ၁။ Groq AI ဖြင့် ကြိုးစားခြင်း
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"You are a {system_role}. Maintain academic and formal tone."},
                {"role": "user", "content": text}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )
        return response.choices[0].message.content.strip(), "Groq AI"
    
    except Exception as e:
        # ၂။ Error တက်ပါက Google Translate သို့ Fallback လုပ်ခြင်း
        if "429" in str(e) or "rate_limit" in str(e):
            try:
                result = google_translator.translate(text, src=src_lang, dest=dest_lang)
                return result.text, "Google Translate (Backup)"
            except:
                return "Translation Failed", "Error"
        return f"Error: {str(e)}", "Error"

# --- UI ---
st.markdown('<div class="main-box">', unsafe_allow_html=True)
st.title("🌐 Hybrid PDF Translator")

# ဘာသာပြန် ဦးတည်ချက် ရွေးရန်
direction = st.radio("ဘာသာပြန်ဆိုမည့် ပုံစံကို ရွေးချယ်ပါ:", ("English to Myanmar", "Myanmar to English"))

uploaded_file = st.file_uploader("PDF ဖိုင် တင်ပါ", type="pdf")

if uploaded_file:
    if "final_doc" not in st.session_state:
        st.session_state.final_doc = Document()
        st.session_state.p_count = 0

    if st.button("ဘာသာပြန်ခြင်း စတင်မည်"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        total_pages = len(pdf_reader.pages)
        prog_bar = st.progress(0)
        
        for i in range(st.session_state.p_count, total_pages):
            page_text = pdf_reader.pages[i].extract_text()
            if page_text.strip():
                time.sleep(1) # API Stability
                translated, engine = translate_engine(page_text, direction)
                st.session_state.final_doc.add_heading(f"Page {i+1}", level=2)
                st.session_state.final_doc.add_paragraph(translated)
                st.write(f"✅ Page {i+1} translated using {engine}")

            st.session_state.p_count = i + 1
            prog_bar.progress(st.session_state.p_count / total_pages)

    if st.session_state.p_count > 0:
        bio = BytesIO()
        st.session_state.final_doc.save(bio)
        st.download_button("📥 Word ဖိုင်ရယူရန်", data=bio.getvalue(), file_name="Translated_Doc.docx")

st.markdown('</div>', unsafe_allow_html=True)
