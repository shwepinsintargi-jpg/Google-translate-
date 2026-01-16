import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from io import BytesIO

st.set_page_config(page_title="AI Myanmar Translator", layout="wide")
st.title("🇲🇲 Professional AI PDF Translator")

# --- API KEY ကို ဒီနေရာမှာ တစ်ခါတည်း ထည့်ထားပါ ---
# သင်ရလာတဲ့ Groq Key စာသားအရှည်ကြီးကို အောက်က "" ထဲမှာ အစားထိုးထည့်ပါ
GROQ_API_KEY = "သင်၏_Groq_API_Key_ကို_ဒီမှာထည့်ပါ"

if GROQ_API_KEY != "သင်၏_Groq_API_Key_ကို_ဒီမှာထည့်ပါ":
    client = Groq(api_key=GROQ_API_KEY)
    uploaded_file = st.file_uploader("PDF ဖိုင်ရွေးပါ", type="pdf")

    if uploaded_file and st.button("AI ဖြင့် ဘာသာပြန်မည်"):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        doc = Document()
        
        bar = st.progress(0)
        num_pages = len(pdf_reader.pages)
        
        for i in range(num_pages):
            text = pdf_reader.pages[i].extract_text()
            if text:
                try:
                    # ပိုမိုပြေပြစ်သော Prompt (ခိုင်းစာ)
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "You are a master English-to-Myanmar literary translator. "
                                    "Your goal is to translate the text into natural, elegant, and modern Myanmar prose. "
                                    "Use vocabulary that a real Myanmar person would use. "
                                    "For example, use 'လူကြီးမင်း' or 'လူတစ်ယောက်' instead of 'အရှင်', "
                                    "and 'ဆင်ပေါက်လေး' instead of 'အရုဏ်ကလေး'. "
                                    "Ensure the story flows beautifully like a professional novel."
                                )
                            },
                            {"role": "user", "content": f"Please translate this text into smooth Myanmar language:\n\n{text}"}
                        ],
                        temperature=0.7, # စာသားအသွားအလာ ပိုသဘာဝကျအောင် လုပ်ပေးခြင်း
                    )
                    result = completion.choices[0].message.content
                    
                    # စာမျက်နှာအလိုက် ခေါင်းစဉ်တပ်ခြင်း
                    p = doc.add_paragraph()
                    run = p.add_run(f"--- Page {i+1} ---")
                    run.bold = True
                    doc.add_paragraph(result)
                except Exception as e:
                    st.error(f"Error on Page {i+1}: {e}")
            
            bar.progress((i + 1) / num_pages)
        
        # Word File ထုတ်ပေးခြင်း
        bio = BytesIO()
        doc.save(bio)
        st.success("ဘာသာပြန်ခြင်း ပြီးပါပြီ!")
        st.download_button("Word ဖိုင်ရယူရန်", bio.getvalue(), "AI_Translated_Myanmar.docx")
else:
    st.error("API Key မထည့်ရသေးပါ။ ကျေးဇူးပြု၍ ကုဒ်ထဲရှိ GROQ_API_KEY နေရာတွင် သင်၏ Key ကို အစားထိုးပါ။")
