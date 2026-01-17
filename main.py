import streamlit as st
from groq import Groq
from googletrans import Translator # အရန် ဘာသာပြန်စနစ်
import PyPDF2
from docx import Document
from io import BytesIO
import time
import json
import os

# --- Page Config ---
st.set_page_config(page_title="Stable PDF Translator", layout="wide")

# --- UI Styling (Fixed Minimalist) ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #FFFFFF !important; overflow: hidden; height: 100vh; }
    .top-header { position: fixed; top: 0; left: 0; width: 100%; background: white; border-bottom: 1px solid #E2E8F0; padding: 10px; text-align: center; color: #1A365D; font-weight: bold; z-index: 1000; font-size: 14px; }
    .main-box { max-width: 500px; margin: auto; padding-top: 70px; }
    .stButton>button { width: 100%; background-color: #1A365D !important; color: white !important; border-radius: 8px !important; font-weight: 600; }
    .file-pill { background-color: #F8F9FA; border-left: 5px solid #1A365D; padding: 10px; border-radius: 4px; color: #1A365D; margin: 15px 0; font-size: 13px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- Logic Initialization ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
google_translator = Translator()

def get_teaching_context():
    if os.path.exists("teaching_data.json"):
        with open("teaching_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            context = "Professional style examples:\n"
            for ex in data.get("examples", [])[:3]:
                context += f"EN: {ex['english']} -> MM: {ex['myanmar']}\n"
            return context
    return ""

def hybrid_translate(text):
    teaching_context = get_teaching_context()
    try:
        # ၁။ Groq (AI) ဖြင့် အရင်ကြိုးစားမည်
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"You are an elite Myanmar translator. {teaching_context}"},
                {"role": "user", "content": text}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )
        return response.choices[0].message.content.strip(), "Groq AI"
    
    except Exception as e:
        # ၂။ Token Limit ပြည့်လျှင် သို့မဟုတ် Error တက်လျှင် Google Translate သို့ ပြောင်းမည်
        if "rate_limit" in str(e).lower() or "429" in str(e):
            try:
                result = google_translator.translate(text, src='en', dest='my')
                return result.text, "Google Translate (Backup)"
            except:
                return "ဘာသာပြန်ဆို၍ မရပါ (System Busy)", "Error"
        return f"Error: {str(e)}", "Error"

# --- UI Execution ---
st.markdown('<div class="top-header">(English PDF မှ မြန်မာဘာသာသို့ - Hybrid System)</div>', unsafe_allow_html=True)
st.markdown('<div class="main-box">', unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")

if uploaded_file:
    st.markdown(f'<div class="file-pill">📄 {uploaded_file.name}</div>', unsafe_allow_html=True)
    
    if "doc" not in st.session_state:
        st.session_state.doc = Document()
        st.session_state.processed_count = 0

    if st.button("ဘာသာပြန်ခြင်း စတင်မည်"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        total_pages = len(pdf_reader.pages)
        
        prog_bar = st.progress(0)
        status_info = st.empty()
        
        for i in range(st.session_state.processed_count, total_pages):
            page_text = pdf_reader.pages[i].extract_text()
            if page_text.strip():
                time.sleep(1) # API Stability
                translated_text, engine = hybrid_translate(page_text)
                
                st.session_state.doc.add_heading(f"Page {i+1}", level=2)
                st.session_state.doc.add_paragraph(translated_text)
                
                # အသုံးပြုနေသည့် Engine ကို ပြသရန်
                status_info.markdown(f"<p style='text-align:center; font-size:12px;'>Using: <b>{engine}</b> for Page {i+1}</p>", unsafe_allow_html=True)

            st.session_state.processed_count = i + 1
            prog_bar.progress(st.session_state.processed_count / total_pages)

        st.success("အားလုံး ပြီးဆုံးပါပြီ။")

    if st.session_state.processed_count > 0:
        bio = BytesIO()
        st.session_state.doc.save(bio)
        st.download_button(
            label=f"📥 Word ဖိုင်ရယူရန် ({st.session_state.processed_count} မျက်နှာစာ)",
            data=bio.getvalue(),
            file_name=f"Translated_{uploaded_file.name.replace('.pdf', '')}.docx"
        )

st.markdown('</div>', unsafe_allow_html=True)
