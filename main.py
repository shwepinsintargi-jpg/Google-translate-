import streamlit as st
import google.generativeai as genai
import PyPDF2
from docx import Document
from io import BytesIO

# ၁။ UI ပိုင်း ပြင်ဆင်ခြင်း
st.set_page_config(page_title="AI PDF Translator", layout="wide")

# CSS ဖြင့် အလှဆင်ခြင်း (အမှားပြင်ဆင်ပြီး)
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .main-title {
        color: #00BFFF;
        font-size: 40px;
        font-weight: bold;
        text-align: center;
    }
    .vpn-warning {
        color: #ff4b4b;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">English PDF To Myanmar</p>', unsafe_allow_html=True)

# ၂။ API Key ထည့်ရန် Box
gemini_key = st.text_input("Google API Key ကို ထည့်ပါ", type="password")
st.markdown('<p class="vpn-warning">⚠️ မြန်မာနိုင်ငံမှ အသုံးပြုပါက USA သို့မဟုတ် Singapore VPN ဖွင့်ပေးပါရန်</p>', unsafe_allow_html=True)

def translate_with_gemini(text, key):
    try:
        genai.configure(api_key=key)
        # Model နာမည်ကို models/ ထည့်၍ ပြင်ဆင်ခြင်း
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        prompt = (
            f"You are a professional English-to-Myanmar translator. "
            f"Translate the following text into natural, smooth, and elegant Myanmar prose. "
            f"Avoid literal translation. Text: {text}"
        )
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

if gemini_key:
    uploaded_file = st.file_uploader("PDF ဖိုင်ရွေးပါ", type="pdf")

    if uploaded_file and st.button("ဘာသာပြန်မည်"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        bar = st.progress(0)
        num_pages = len(pdf_reader.pages)
        
        st.info("AI ဘာသာပြန်နေပါသည်။ ခဏစောင့်ပေးပါ...")
        
        for i in range(num_pages):
            text = pdf_reader.pages[i].extract_text()
            if text:
                result = translate_with_gemini(text, gemini_key)
                
                # Word ထဲသို့ စာမျက်နှာခေါင်းစဉ်နှင့် အဖြေထည့်ခြင်း
                p = doc.add_paragraph()
                run = p.add_run(f"--- Page {i+1} ---")
                run.bold = True
                doc.add_paragraph(result)
            
            bar.progress((i + 1) / num_pages)
        
        # Word File ထုတ်ပေးခြင်း
        bio = BytesIO()
        doc.save(bio)
        st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
        st.download_button("Word ဖိုင်ရယူရန်", bio.getvalue(), "Translated_Myanmar.docx")
else:
    st.info("ဆက်လက်လုပ်ဆောင်ရန် Google API Key ကို အပေါ်က Box မှာ ထည့်ပေးပါ")
