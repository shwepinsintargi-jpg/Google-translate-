import streamlit as st
import requests
import PyPDF2
from docx import Document
from io import BytesIO
import time

st.set_page_config(page_title="AI Myanmar Translator", layout="wide")
st.title("🇲🇲 AI PDF Myanmar Translator")

# App ဖွင့်မှ Key ထည့်ရန် Box ပြုလုပ်ခြင်း
hf_token = st.text_input("Hugging Face Token (hf_...) ကို ထည့်ပါ", type="password")

def translate_with_ai(text, token):
    API_URL = "https://api-inference.huggingface.co/models/google/gemma-2-9b-it"
    headers = {"Authorization": f"Bearer {token}"}
    
    prompt = f"<bos><start_of_turn>user\nTranslate this to natural Myanmar prose: {text}<end_of_turn>\n<start_of_turn>model\n"
    
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 1000, "temperature": 0.7}}
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            full_text = response.json()[0]['generated_text']
            return full_text.split("model\n")[-1].strip()
        elif response.status_code == 503:
            st.warning("AI Model စတင်နေပါသဖြင့် ၁၀ စက္ကန့်ခန့် စောင့်ပေးပါ...")
            time.sleep(10)
            return translate_with_ai(text, token)
        else:
            return f"Error: {response.status_code}. Token မှန်မမှန် ပြန်စစ်ပေးပါ။"
    except:
        return "ဘာသာပြန်ရာတွင် အခက်အခဲရှိနေပါသည်။"

if hf_token:
    uploaded_file = st.file_uploader("PDF ဖိုင်ရွေးပါ", type="pdf")

    if uploaded_file and st.button("AI ဖြင့် ဘာသာပြန်မည်"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        bar = st.progress(0)
        
        for i in range(len(pdf_reader.pages)):
            text = pdf_reader.pages[i].extract_text()
            if text:
                result = translate_with_ai(text, hf_token)
                doc.add_heading(f'Page {i+1}', level=1)
                doc.add_paragraph(result)
            bar.progress((i + 1) / len(pdf_reader.pages))
        
        bio = BytesIO()
        doc.save(bio)
        st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
        st.download_button("Word ဖိုင်ရယူရန်", bio.getvalue(), "AI_Translated.docx")
else:
    st.info("ဆက်လက်လုပ်ဆောင်ရန် Hugging Face Token ကို အပေါ်က Box မှာ ထည့်ပေးပါခင်ဗျာ။")
