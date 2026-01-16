import streamlit as st
import requests
import PyPDF2
from docx import Document
from io import BytesIO
import time

# UI ပိုင်း ပြင်ဆင်ခြင်း
st.set_page_config(page_title="Professional AI Translator", layout="wide")
st.title("🇲🇲 Professional AI PDF Translator")
st.write("Mistral-7B Model ကို အသုံးပြုထားသဖြင့် မြန်မာစာအရေးအသား ပိုမိုတည်ငြိမ်ပါသည်")

# API Key (Token) ကို Box ထဲတွင် ထည့်ခိုင်းခြင်း
hf_token = st.text_input("Hugging Face Token (hf_...) ကို ထည့်ပါ", type="password")

def translate_with_ai(text, token):
    # ပိုမိုတည်ငြိမ်သော Mistral API Endpoint ကို အသုံးပြုခြင်း
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
    headers = {"Authorization": f"Bearer {token}"}
    
    # မြန်မာစာ ပြေပြစ်စေရန် Prompt ကို အဆင့်မြှင့်တင်ခြင်း
    prompt = f"<s>[INST] Translate the following English text to natural and fluent Myanmar (Burmese) language. Do not explain, just give the translation.\n\nText: {text} [/INST]"
    
    payload = {
        "inputs": prompt, 
        "parameters": {"max_new_tokens": 1200, "temperature": 0.7}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            full_text = response.json()[0]['generated_text']
            # AI ၏ အဖြေထဲမှ ဘာသာပြန်ကိုသာ ဆွဲထုတ်ခြင်း
            return full_text.split("[/INST]")[-1].strip()
        elif response.status_code == 503:
            # Model load လုပ်နေလျှင် စောင့်ရန်
            st.warning("AI စက်စတင်နေပါသဖြင့် ခေတ္တစောင့်ပေးပါ...")
            time.sleep(15)
            return translate_with_ai(text, token)
        else:
            return f"Error: {response.status_code}. Model ချိတ်ဆက်မှု အဆင်မပြေပါ။"
    except:
        return "ဘာသာပြန်ရာတွင် အခက်အခဲရှိနေပါသည်။"

if hf_token:
    uploaded_file = st.file_uploader("PDF ဖိုင်ရွေးပါ", type="pdf")

    if uploaded_file and st.button("AI ဖြင့် ဘာသာပြန်မည်"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        bar = st.progress(0)
        num_pages = len(pdf_reader.pages)
        
        st.info("AI ဘာသာပြန်နေပါသည်။ စာမျက်နှာအလိုက် စောင့်ပေးပါ...")
        
        for i in range(num_pages):
            text = pdf_reader.pages[i].extract_text()
            if text:
                # စာပိုဒ်လိုက် ဘာသာပြန်ခြင်း
                result = translate_with_ai(text, hf_token)
                
                # Word ထဲသို့ ထည့်သွင်းခြင်း
                p = doc.add_paragraph()
                run = p.add_run(f"--- Page {i+1} ---")
                run.bold = True
                doc.add_paragraph(result)
            
            bar.progress((i + 1) / num_pages)
        
        # Download ပြုလုပ်ရန် Word File ဖန်တီးခြင်း
        bio = BytesIO()
        doc.save(bio)
        st.success("ဘာသာပြန်ခြင်း အောင်မြင်စွာ ပြီးဆုံးပါပြီ!")
        st.download_button(
            label="ဘာသာပြန်ထားသော Word ဖိုင်ရယူရန်",
            data=bio.getvalue(),
            file_name="AI_Myanmar_Translation.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
else:
    st.info("ဆက်လက်လုပ်ဆောင်ရန် Hugging Face Token ကို အပေါ်က Box တွင် ထည့်ပေးပါ")
