import streamlit as st
import google.generativeai as genai
import PyPDF2
from docx import Document
from io import BytesIO

# --- Gemini Configuration ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ API Key ကို Streamlit Secrets မှာ မတွေ့ရသေးပါ။")
    st.stop()

# --- Page Config ---
st.set_page_config(page_title="Gemini AI Translator", layout="centered")

# --- Custom CSS (Minimalist Style) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h3, p, span, label { color: #000000 !important; font-family: 'Pyidaungsu', sans-serif; }
    .stButton>button {
        width: 100%; background-color: #000000 !important; color: #FFFFFF !important;
        border-radius: 8px !important; height: 3.5em; border: none !important;
    }
    .stFileUploader section { border: 1.5px dashed #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Translation Function ---
def ai_translate(text):
    prompt = f"""
    You are a professional translator. 
    Translate the following English text to natural-sounding Myanmar language.
    
    RULES:
    1. Keep technical terms, formulas, and numbers in English if appropriate.
    2. Ensure the tone is formal and professional.
    3. Return ONLY the translated text.

    Text:
    {text}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# --- UI ---
st.markdown("### 🤖 Gemini AI Pro Translator")
uploaded_file = st.file_uploader("ဘာသာပြန်မည့် PDF တင်ပါ", type="pdf")

if uploaded_file:
    if st.button("ဘာသာပြန်ရန်"):
        with st.status("Gemini AI က ဘာသာပြန်နေပါသည်...") as status:
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
            
            status.update(label="✅ ပြီးဆုံးပါပြီ!", state="complete")
            
            bio = BytesIO()
            doc.save(bio)
            st.download_button(
                label="📥 Word ဖိုင်ရယူရန်",
                data=bio.getvalue(),
                file_name="Gemini_Translated.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
