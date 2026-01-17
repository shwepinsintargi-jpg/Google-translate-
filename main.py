import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from io import BytesIO
import time
import json
import os

# --- Page Config ---
st.set_page_config(page_title="Elite PDF Translator", layout="wide")

# --- UI Styling ---
st.markdown("""
    <style>
    .top-header { position: fixed; top: 0; left: 0; width: 100%; background: white; border-bottom: 1px solid #E2E8F0; padding: 10px; text-align: center; color: #1A365D; font-weight: bold; z-index: 1000; }
    .main-container { max-width: 600px; margin: auto; padding-top: 80px; }
    .stProgress > div > div > div > div { background-color: #1A365D !important; }
    .file-pill { background-color: #F1F5F9; border-left: 5px solid #1A365D; padding: 15px; border-radius: 8px; color: #1A365D; margin-bottom: 20px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- Logic: Groq & Teaching Context ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def get_teaching_context():
    if os.path.exists("teaching_data.json"):
        with open("teaching_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            context = "Focus on this style:\n"
            for ex in data.get("examples", [])[:5]: # ပထမ ၅ ခုပဲယူပါမယ် (Token သက်သာရန်)
                context += f"EN: {ex['english']} -> MM: {ex['myanmar']}\n"
            return context
    return "Translate English to Myanmar professionally."

def ai_translate_with_retry(text, retries=3):
    teaching_context = get_teaching_context()
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are a professional translator. {teaching_context}"},
                    {"role": "user", "content": text}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.2,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(5) # ၅ စက္ကန့်နားပြီး ပြန်ကြိုးစားမည်
                continue
            else:
                return f"Error: {str(e)}"

# --- UI Execution ---
st.markdown('<div class="top-header">(English PDF မှ မြန်မာဘာသာသို့ - Stable Version)</div>', unsafe_allow_html=True)
st.markdown('<div class="main-container">', unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")

if uploaded_file:
    st.markdown(f'<div class="file-pill">📄 {uploaded_file.name}</div>', unsafe_allow_html=True)
    
    if "doc" not in st.session_state:
        st.session_state.doc = Document()
        st.session_state.processed_pages = 0

    if st.button("ဘာသာပြန်ခြင်း စတင်မည်"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        total_pages = len(pdf_reader.pages)
        
        prog_bar = st.progress(0)
        prog_text = st.empty()
        
        for i in range(st.session_state.processed_pages, total_pages):
            page_text = pdf_reader.pages[i].extract_text()
            
            if page_text.strip():
                # စာမျက်နှာအလိုက် Delay ပေးခြင်း (Rate Limit ကာကွယ်ရန်)
                time.sleep(1.2)
                
                translated = ai_translate_with_retry(page_text)
                st.session_state.doc.add_heading(f"Page {i+1}", level=2)
                st.session_state.doc.add_paragraph(translated)
            
            st.session_state.processed_pages = i + 1
            percent = int((st.session_state.processed_pages / total_pages) * 100)
            prog_bar.progress(st.session_state.processed_pages / total_pages)
            prog_text.markdown(f"<p style='text-align:center;'>အခြေအနေ: စာမျက်နှာ {st.session_state.processed_pages} / {total_pages} ({percent}%)</p>", unsafe_allow_html=True)

        st.success("ဘာသာပြန်ခြင်း အောင်မြင်စွာ ပြီးဆုံးပါပြီ!")

    # Download Button (အမြဲတမ်း ပေါ်နေမည် - ရသလောက် သိမ်းနိုင်ရန်)
    if st.session_state.processed_pages > 0:
        bio = BytesIO()
        st.session_state.doc.save(bio)
        st.download_button(
            label=f"📥 Word ဖိုင်ရယူရန် (စာမျက်နှာ {st.session_state.processed_pages} အထိ)",
            data=bio.getvalue(),
            file_name=f"Translated_{uploaded_file.name.replace('.pdf', '')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

st.markdown('</div>', unsafe_allow_html=True)
