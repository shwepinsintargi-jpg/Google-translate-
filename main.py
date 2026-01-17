import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from io import BytesIO

# UI အလှဆင်ခြင်း
st.set_page_config(page_title="No-VPN AI Translator", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-title { color: #1E90FF; font-size: 40px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">AI PDF Translator (No VPN)</p>', unsafe_allow_html=True)

# ၁။ API Key Box (Groq Key ကို ဒီမှာ ထည့်ရပါမယ်)
groq_key = st.text_input("🔑 Groq API Key ကို ထည့်ပါ", type="password", help="console.groq.com တွင် Key ယူပါ")

def translate_with_groq(text, key):
    try:
        client = Groq(api_key=key)
        # Llama 3.1 70B ဆိုတဲ့ အဆင့်မြင့်ဆုံး model ကို သုံးပေးထားပါတယ်
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional English-to-Myanmar translator. Translate text naturally, fluently, and avoid literal translation. Use appropriate Myanmar vocabulary."
                },
                {
                    "role": "user",
                    "content": f"Translate the following text into Myanmar: \n\n{text}",
                }
            ],
            model="llama-3.1-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

if groq_key:
    uploaded_file = st.file_uploader("📄 PDF ဖိုင်တင်ပါ", type="pdf")

    if uploaded_file and st.button("🚀 ဘာသာပြန်မည်"):
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            doc = Document()
            num_pages = len(pdf_reader.pages)
            bar = st.progress(0)
            
            st.info("AI ဘာသာပြန်နေပါသည်။ ခဏစောင့်ပေးပါ (VPN မလိုပါ)...")
            
            for i in range(num_pages):
                page_text = pdf_reader.pages[i].extract_text()
                if page_text.strip():
                    # AI ဖြင့် ဘာသာပြန်ခြင်း
                    result = translate_with_groq(page_text, groq_key)
                    doc.add_heading(f"Page {i+1}", level=2)
                    doc.add_paragraph(result)
                bar.progress((i + 1) / num_pages)
            
            # Word ဖိုင်အဖြစ် ပြောင်းလဲခြင်း
            bio = BytesIO()
            doc.save(bio)
            st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
            st.download_button("📥 Word ဖိုင်ရယူရန်", bio.getvalue(), "Translated_AI.docx")
        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.warning("💡 ဆက်လက်လုပ်ဆောင်ရန် Groq API Key ကို အပေါ်ရှိ Box တွင် အရင်ထည့်ပေးပါ")
