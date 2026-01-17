import streamlit as st
import google.generativeai as genai
import PyPDF2
from docx import Document
from io import BytesIO

# UI အလှဆင်ခြင်း
st.set_page_config(page_title="AI PDF Translator", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .main-title { color: #00BFFF; font-size: 40px; font-weight: bold; text-align: center; }
    .vpn-warning { color: #ff4b4b; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">English PDF To Myanmar</p>', unsafe_allow_html=True)

# API Key Box
gemini_key = st.text_input("Google API Key ကို ထည့်ပါ", type="password")
st.markdown('<p class="vpn-warning">⚠️ မြန်မာနိုင်ငံမှ အသုံးပြုပါက USA သို့မဟုတ် Singapore VPN ဖွင့်ပေးပါရန်</p>', unsafe_allow_html=True)

def translate_with_gemini(text, key):
    try:
        genai.configure(api_key=key)
        # Model နာမည်ကို အမှန်ကန်ဆုံးဖြစ်သော gemini-1.5-flash ဟုသာ ရေးပါ
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(
            f"Translate this English text into natural, fluent Myanmar prose: {text}"
        )
        # အဖြေပြန်မလာပါက စစ်ဆေးရန်
        if response and response.text:
            return response.text
        else:
            return "ဘာသာပြန်၍ မရပါ (Empty Response)"
    except Exception as e:
        # 404 Error သို့မဟုတ် အခြား Error များအား ဖမ်းယူရန်
        return f"Error: {str(e)}"

if gemini_key:
    uploaded_file = st.file_uploader("PDF ဖိုင်ရွေးပါ", type="pdf")

    if uploaded_file and st.button("ဘာသာပြန်မည်"):
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            doc = Document()
            bar = st.progress(0)
            num_pages = len(pdf_reader.pages)
            
            st.info("AI ဘာသာပြန်နေပါသည်။ ခဏစောင့်ပေးပါ...")
            
            for i in range(num_pages):
                text = pdf_reader.pages[i].extract_text()
                if text:
                    result = translate_with_gemini(text, gemini_key)
                    # စာမျက်နှာအလိုက် Word ထဲထည့်ခြင်း
                    doc.add_heading(f"Page {i+1}", level=2)
                    doc.add_paragraph(result)
                bar.progress((i + 1) / num_pages)
            
            # Word File အဖြစ် သိမ်းဆည်းခြင်း
            bio = BytesIO()
            doc.save(bio)
            st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
            st.download_button(
                label="Word ဖိုင်ရယူရန်",
                data=bio.getvalue(),
                file_name="Translated_Myanmar.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.info("ဆက်လက်လုပ်ဆောင်ရန် Google API Key ကို ထည့်ပေးပါ")
