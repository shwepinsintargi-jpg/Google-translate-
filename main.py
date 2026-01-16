import streamlit as st
import requests
import PyPDF2
from docx import Document
from io import BytesIO
import time

# UI ပိုင်း ပြင်ဆင်ခြင်း
st.set_page_config(page_title="AI Myanmar Translator", layout="wide")
st.title("🇲🇲 Google Gemma-2 AI PDF Translator")
st.subheader("Google ရဲ့ AI နည်းပညာဖြင့် အပြေပြစ်ဆုံး ဘာသာပြန်ပေးပါသည်")

# --- အောက်က "hf_..." နေရာမှာ သင်ရလာတဲ့ Token ကို အစားထိုးပါ ---
HF_TOKEN = "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"

def translate_with_ai(text):
    API_URL = "https://api-inference.huggingface.co/models/google/gemma-2-9b-it"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # AI ကို မြန်မာစာ ပြေပြစ်အောင် ပြန်ခိုင်းသော Prompt
    prompt = (
        f"<bos><start_of_turn>user\n"
        f"Translate the following English text into very natural and smooth Myanmar (Burmese) prose. "
        f"Avoid literal word-for-word translation. Make it sound like a well-written book.\n\n"
        f"Text: {text}<end_of_turn>\n"
        f"<start_of_turn>model\n"
    )
    
    payload = {
        "inputs": prompt, 
        "parameters": {"max_new_tokens": 1500, "temperature": 0.7}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            full_text = response.json()[0]['generated_text']
            # AI ရဲ့ အဖြေထဲက မြန်မာစာကိုပဲ ဆွဲထုတ်ခြင်း
            return full_text.split("model\n")[-1].strip()
        elif response.status_code == 503:
            time.sleep(5) # Model load လုပ်နေရင် ၅ စက္ကန့် စောင့်ခြင်း
            return translate_with_ai(text)
        else:
            return f"Error: {response.status_code}"
    except:
        return "ဘာသာပြန်ရာတွင် အခက်အခဲရှိနေပါသည်။"

uploaded_file = st.file_uploader("PDF ဖိုင်ရွေးပါ", type="pdf")

if uploaded_file and st.button("AI ဖြင့် ဘာသာပြန်မည်"):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    doc = Document()
    bar = st.progress(0)
    num_pages = len(pdf_reader.pages)
    
    st.info("AI ဘာသာပြန်နေပါသည်။ ခဏစောင့်ပေးပါ...")
    
    for i in range(num_pages):
        text = pdf_reader.pages[i].extract_text()
        if text:
            # AI ဖြင့် ဘာသာပြန်ခြင်း
            result = translate_with_ai(text)
            
            # Word ဖိုင်ထဲ ထည့်ခြင်း
            p = doc.add_paragraph()
            run = p.add_run(f"--- Page {i+1} ---")
            run.bold = True
            doc.add_paragraph(result)
            
        bar.progress((i + 1) / num_pages)
    
    # Word File အဖြစ် သိမ်းဆည်းခြင်း
    bio = BytesIO()
    doc.save(bio)
    st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
    st.download_button(
        label="ဘာသာပြန်ထားသော Word ဖိုင်ရယူရန်",
        data=bio.getvalue(),
        file_name="AI_Myanmar_Translation.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )