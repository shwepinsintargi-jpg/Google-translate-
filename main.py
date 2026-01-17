import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from io import BytesIO

# --- Groq Configuration ---
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=API_KEY)
except Exception as e:
    st.error("⚠️ GROQ_API_KEY ကို Secrets မှာ အရင်ထည့်ပေးပါ။")
    st.stop()

# --- Page Config ---
st.set_page_config(page_title="Groq AI Translator", layout="centered")

# --- UI Styling ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h3, p, span, label { color: #000000 !important; font-family: 'Pyidaungsu', sans-serif; }
    .stButton>button { width: 100%; background-color: #000000 !important; color: #FFFFFF !important; border-radius: 8px !important; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- Translation Function (Advanced Prompting) ---
def ai_translate(text):
    try:
        # ဤနေရာတွင် System Prompt ကို အဆင့်မြှင့်ထားပါသည်
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert English-to-Myanmar translator. Your task is to provide a natural, professional, and context-aware translation. Avoid robotic or direct word-for-word translation. Keep technical terms in English where necessary."
                },
                {
                    "role": "user",
                    "content": f"Translate this text to Myanmar: \n\n {text}"
                }
            ],
            model="llama-3.1-70b-versatile", # Gemini Pro နဲ့ တန်းတူရည်တူရှိသော model ဖြစ်သည်
            temperature=0.3, # တိကျမှုရှိစေရန်
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# --- UI ---
st.markdown("### ⚡ Groq AI Fast Translator")
uploaded_file = st.file_uploader("PDF တင်ပါ", type="pdf")

if uploaded_file:
    if st.button("ဘာသာပြန်ပါ"):
        with st.status("Groq AI က အလွန်လျှင်မြန်စွာ ဘာသာပြန်နေပါသည်...") as status:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            doc = Document()
            total_pages = len(pdf_reader.pages)
            progress_bar = st.progress(0)

            for i in range(total_pages):
                page_text = pdf_reader.pages[i].extract_text()
                if page_text.strip():
                    translated_text = ai_translate(page_text)
                    doc.add_heading(f"Page {i+1}", level=2)
                    doc.add_paragraph(translated_text)
                progress_bar.progress((i + 1) / total_pages)
            
            status.update(label="✅ ပြီးပါပြီ!", state="complete")
            
            bio = BytesIO()
            doc.save(bio)
            st.download_button(label="📥 Word ဖိုင်ရယူရန်", data=bio.getvalue(), file_name="Groq_Translated.docx")
