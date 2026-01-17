import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from io import BytesIO
import base64

# --- Groq API Configuration ---
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=API_KEY)
except Exception as e:
    st.error("⚠️ GROQ_API_KEY ကို Secrets မှာ အရင်ထည့်ပေးပါ။")
    st.stop()

# --- Page Config & Style ---
st.set_page_config(page_title="PDF to Myanmar Translator", layout="centered")

# Custom CSS for UI Style
st.markdown("""
    <style>
    /* White Background */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Dark Blue Text for Titles */
    h1, h2, h3 { color: #003366 !important; font-family: 'Pyidaungsu', sans-serif; }
    p, span, label { color: #333333 !important; }

    /* Button Styling */
    .stButton>button {
        width: 100%;
        background-color: #003366 !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        height: 3em;
        border: none !important;
        font-weight: bold;
    }
    
    /* Progress Bar Color */
    .stProgress > div > div > div > div { background-color: #003366 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Alarm Sound Function ---
def play_alarm():
    # ရိုးရှင်းသော Notification အသံ (Base64)
    audio_html = """
        <audio autoplay>
            <source src="https:// quality-notifications.s3.amazonaws.com/success.mp3" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# --- High-Level Translation Function ---
def ai_translate(text):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are an elite English-to-Myanmar translator specialized in academic and professional documents. 
                    - Provide a natural, fluent Myanmar translation (Subject-Object-Verb).
                    - Use formal 'Literary' Myanmar style (e.g., uses 'ပါသည်', 'ပြုလုပ်သည်').
                    - Avoid word-for-word robotic translation.
                    - Keep technical terms or proper nouns in English inside parentheses if necessary."""
                },
                {
                    "role": "user",
                    "content": f"Translate this into professional Myanmar: \n\n {text}"
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# --- UI Layout ---

# ၁။ ပထမဆုံး စာသား
st.markdown("# English PDF into Myanmar Text")
st.write("---")

# ၂။ ဒုတိယ File တင်ရန် (Label)
st.markdown("### ဘာသာပြန်လိုသော PDF ဖိုင်ကို ရွေးချယ်ပါ")

# ၃။ တတိယ File Uploaded နေရာ
uploaded_file = st.file_uploader("", type="pdf")

if uploaded_file:
    if st.button("ဘာသာပြန်ခြင်း စတင်ပါ"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        total_pages = len(pdf_reader.pages)
        
        # ၄။ စတုတ္ထ ဘာသာပြန် loading % ပြတဲ့ နေရာ
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        full_text_translated = ""

        for i in range(total_pages):
            # Page အလိုက် process လုပ်ခြင်း
            page_text = pdf_reader.pages[i].extract_text()
            if page_text.strip():
                translated_page = ai_translate(page_text)
                doc.add_heading(f"Page {i+1}", level=2)
                doc.add_paragraph(translated_page)
                full_text_translated += translated_page + "\n\n"
            
            # Update Progress
            percent_complete = int(((i + 1) / total_pages) * 100)
            progress_bar.progress((i + 1) / total_pages)
            progress_text.markdown(f"**ဘာသာပြန်နေမှု: {percent_complete}%**")

        # ဘာသာပြန်ပြီးလျှင် Alarm မြည်ခြင်း
        play_alarm()
        st.success("✅ ဘာသာပြန်ခြင်း အောင်မြင်စွာ ပြီးဆုံးပါပြီ!")

        # ၅။ နောက်ဆုံး Text download ရန် နေရာ
        bio = BytesIO()
        doc.save(bio)
        
        st.download_button(
            label="📥 ဘာသာပြန်ထားသော Word ဖိုင်ကို ရယူရန်",
            data=bio.getvalue(),
            file_name="Translated_Myanmar.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
