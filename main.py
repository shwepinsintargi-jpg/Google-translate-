import streamlit as st
import google.generativeai as genai
import PyPDF2
from docx import Document
from io import BytesIO
import json

# --- Gemini Configuration (Secure Method) ---
try:
    # Streamlit Cloud Settings > Secrets ထဲမှ GEMINI_API_KEY ကို ဖတ်ခြင်း
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ API Key ကို Streamlit Secrets မှာ မတွေ့ရသေးပါ။ ကျေးဇူးပြု၍ Settings တွင် အရင်ထည့်ပေးပါ။")
    st.stop()

# --- Page Config ---
st.set_page_config(page_title="AI Pro Translator", layout="centered")

# --- Custom CSS (Pure White & Black Theme) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    .main .block-container { max-width: 550px; padding-top: 2rem; }
    h3, p, span, label, .stMarkdown { color: #000000 !important; font-family: 'Pyidaungsu', sans-serif; }
    
    .stSelectbox div[data-baseweb="select"] { border: 1.5px solid #000000 !important; border-radius: 5px; }
    .stFileUploader section { background-color: #FFFFFF !important; border: 1.5px dashed #000000 !important; border-radius: 8px; }
    
    .stButton>button {
        width: 100%; background-color: #000000 !important; color: #FFFFFF !important;
        border-radius: 8px !important; font-weight: bold !important; height: 3.5em; border: none !important;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #333333 !important; }
    .stButton>button p { color: #FFFFFF !important; margin: 0 !important; font-size: 16px; }
    .stProgress > div > div > div > div { background-color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- AI Translation Function ---
def ai_translate(text, glossary_data, genre):
    glossary_str = json.dumps(glossary_data, ensure_ascii=False)
    
    prompt = f"""
    You are a professional Myanmar translator specializing in {genre}. 
    Translate the following English text to Myanmar.

    GUIDELINES:
    1. STRICTLY use these terms if they appear in the text: {glossary_str}
    2. Keep chemical formulas (e.g., H2O, CO2), mathematical symbols, and numbers in English.
    3. Ensure the Myanmar translation flows naturally and is contextually correct for {genre}.
    4. Provide ONLY the translated Myanmar text.

    Text:
    {text}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "ဘာသာပြန်ရာတွင် အမှားအယွင်းရှိနေပါသည်။"

# --- UI Setup ---
GLOSSARY_FILES = {
    "ရိုးရိုးဝတ္ထု": "glossary_novel.json",
    "အက်ရှင်": "glossary_action.json",
    "အထွေထွေ": "glossary_general.json",
    "သင်္ချာ": "glossary_math.json",
    "သိပ္ပံ": "glossary_science.json"
}

# စာပေအမျိုးအစားရွေးရန် (တစ်တန်းတည်းထားခြင်း)
col1, col2 = st.columns([1.2, 1])
with col1:
    st.markdown("<p style='margin-top:10px; font-weight:bold;'>📖 စာပေအမျိုးအစားရွေးချယ်ရန်</p>", unsafe_allow_html=True)
with col2:
    selected_genre = st.selectbox("", list(GLOSSARY_FILES.keys()), label_visibility="collapsed")

uploaded_file = st.file_uploader("ဘာသာပြန်မည့် PDF file တင်ပါ", type="pdf")

if uploaded_file:
    st.markdown(f"**📄 ဖိုင်အမည်:** {uploaded_file.name}")
    st.write("---")
    
    if st.button("စတင်ဘာသာပြန်ပါ"):
        with st.status("Gemini AI ဖြင့် အဆင့်မြင့်ဘာသာပြန်နေပါသည်...", expanded=True) as status:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            doc = Document()
            
            # Glossary ဖတ်ခြင်း
            try:
                with open(GLOSSARY_FILES[selected_genre], 'r', encoding='utf-8') as f:
                    glossary = json.load(f)
            except:
                glossary = {}

            total_pages = len(pdf_reader.pages)
            progress_bar = st.progress(0)

            for i in range(total_pages):
                st.write(f"➡️ စာမျက်နှာ {i+1} ကို လုပ်ဆောင်နေသည်...")
                page_text = pdf_reader.pages[i].extract_text()
                
                if page_text:
                    # Gemini ကို စာမျက်နှာအလိုက် ပို့ခြင်း
                    translated_page = ai_translate(page_text, glossary, selected_genre)
                    doc.add_heading(f"Page {i+1}", level=2)
                    doc.add_paragraph(translated_page)
                
                progress_bar.progress((i + 1) / total_pages)

            status.update(label="✅ ဘာသာပြန်ခြင်း ပြီးဆုံးပါပြီ!", state="complete")
            
            bio = BytesIO()
            doc.save(bio)
            st.download_button(
                label="📥 Word file ဒေါင်းရန်",
                data=bio.getvalue(),
                file_name=f"AI_Translated_{selected_genre}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
else:
    st.progress(0)
