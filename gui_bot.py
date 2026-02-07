import streamlit as st
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import pandas as pd

# --- 1. MODERN NOIR UI ---
st.set_page_config(page_title="Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    section[data-testid="stSidebar"] { 
        background-color: #050505 !important; 
        border-right: 1px solid #1A1A1A; 
    }
    .stChatInputContainer { border-top: 1px solid #1A1A1A !important; }
    h1, h2, h3, p, span, label { font-family: 'Inter', sans-serif !important; color: #FFFFFF !important; }
    .stTable { background-color: #000000; border: 1px solid #333333; }
    .stButton>button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 0px;
        width: 100%;
        font-weight: 900;
        border: none;
    }
    /* Spacious Chat Layout */
    .stChatMessage { margin-bottom: 2rem; border-bottom: 1px solid #111; padding-bottom: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CORE LOGIC (404 STABILIZER) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    if os.path.exists("data.txt"):
        with open("data.txt", "r") as f:
            kb_content = f.read()
    else:
        kb_content = "Knowledge base missing. User is unprepared."

    # Using the most stable model identifier to prevent v1beta 404s
    model = genai.GenerativeModel(
        model_name='models/gemini-1.5-flash',
        system_instruction=(
            f"DATA: {kb_content}\n"
            "SYSTEM: You are a professional, high-IQ roaster. "
            "First: Answer facts from the DATA accurately. "
            "Second: Deliver a witty, adult-humor roast. "
            "Strictly Black & White persona. No emojis. No cringe."
        )
    )
except Exception as e:
    st.error(f"FATAL_INIT: {e}")
    st.stop()

def get_sheet():
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    return gspread.authorize(creds).open("Chat logs").sheet1

# --- 3. SIDEBAR (RANKING & TOKENS) ---
st.sidebar.title("SYSTEM_LOGS")

if "tokens" not in st.session_state:
    st.session_state.tokens = 0
st.sidebar.write(f"TOKENS_BURNED: {st.session_state.tokens}")
st.sidebar.progress(min(st.session_state.tokens / 50000, 1.0))

st.sidebar.subheader("VICTIM_RANKING")
try:
    data = get_sheet().get_all_records()
    if data:
        df = pd.DataFrame(data)
        counts = df['Name'].value_counts().reset_index()
        counts.columns = ['Victim', 'Roasts']
        st.sidebar.table(counts.head(5))
except:
    st.sidebar.write("Logs connection pending.")

# --- 4. LOGIN ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("AUTHENTICATION")
    with st.form("login"):
        n = st.text_input("IDENTIFIER")
        e = st.text_input("CREDENTIAL")
        if st.form_submit_button("ENTER"):
            if "@" in e and n:
                st.session_state.user_name = n
                st.session_state.user_email = e
                st.session_state.signed_in = True
                st.rerun()
    st.stop()

# --- 5. TERMINAL ---
st.title("COMMAND_LINE")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Enter query..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Bypassing safety for hilarity
        safety = [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                  {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}]
        
        response = model.generate_content(prompt, safety_settings=safety)
        answer = response.text
        
        st.session_state.tokens += (len(prompt) + len(answer)) // 4
        
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        get_sheet().append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.user_name, st.session_state.user_email, prompt, answer])
    except Exception as e:
        # If it 404s again, this error message will tell us the EXACT path that failed
        st.error(f"TERMINAL_FAILURE: {e}")
