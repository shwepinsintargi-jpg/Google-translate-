import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(page_title="Academic PDF Translator", layout="wide")

# --- Luxury & Clean UI Styling ---
st.markdown("""
    <style>
    /* Main Background & Font */
    .stApp { background-color: #F8F9FA !important; }
    h1, h2, h3 { font-family: 'Pyidaungsu', sans-serif; color: #1A365D !important; }
    
    /* Custom Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }

    /* Professional Card for Content */
    .content-card {
        background-color: #FFFFFF;
        padding: 2.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
    }

    /* Button Styling (Deep Blue) */
    .stButton>button {
        width: 100%;
        background-color: #1A365D !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2A4365 !important;
        box-shadow: 0 4px 12px rgba(26, 54, 93, 0.2);
    }

    /* File Uploader Box Styling */
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF;
        border: 2px dashed #CBD5E0 !important;
        border-radius: 12px;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Logic: Groq Configuration ---
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=API_KEY)
except Exception:
    st.error("⚠️ GROQ_API_KEY is missing in Streamlit Secrets.")
    st.stop()

# --- Professional Translation Function ---
def ai_translate(text):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a senior Myanmar academic translator. Translate English into professional literary Myanmar. Maintain subject-object-verb structure. Use formal terms (e.g., 'ဉာဏ်ရည်တု' for AI, 'နိဂုံး' for Conclusion)."},
                {"role": "user", "content": f"Translate this text formally: {text}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Translation Error: {str(e)}"

# --- Layout Construction ---

# Sidebar for Status and Settings
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2800/2800015.png", width=80)
    st.title("Settings")
    st.info("Quality: High (Llama 3.3 70B)")
    st.write("---")
    st.caption("Developed for Academic Use")

# Main Page Content
st.markdown('<div class="content-card">', unsafe_allow_html=True)
st.markdown("# English PDF into Myanmar Text")
st.markdown("##### အဆင့်မြင့် ဉာဏ်ရည်တုစနစ်ဖြင့် မြန်မာဘာသာသို့ တိကျစွာ ဘာသာပြန်ဆိုခြင်း")
st.write("")

# File Upload Section
uploaded_file = st.file_uploader("ဘာသာပြန်မည့် PDF ဖိုင်ကို ရွေးချယ်ပါ", type="pdf")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("ဘာသာပြန်ခြင်း စတင်မည်"):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            doc = Document()
            total_pages = len(pdf_reader.pages)
            
            progress_container = st.empty()
            progress_bar = st.progress(0)
            
            for i in range(total_pages):
                page_text = pdf_reader.pages[i].extract_text()
                if page_text.strip():
                    translated_page = ai_translate(page_text)
                    doc.add_heading(f"Page {i+1}", level=2)
                    doc.add_paragraph(translated_page)
                
                # Dynamic Update
                progress = (i + 1) / total_pages
                progress_bar.progress(progress)
                progress_container.markdown(f"**တိုးတက်မှုအခြေအနေ: {int(progress * 100)}%**")

            st.success("ဘာသာပြန်ခြင်း ပြီးမြောက်ပါပြီ။")
            
            # Save and Download
            bio = BytesIO()
            doc.save(bio)
            st.download_button(
                label="📥 ရရှိလာသောစာသားကို Word ဖိုင်အဖြစ် ရယူရန်",
                data=bio.getvalue(),
                file_name="Translated_Document.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
