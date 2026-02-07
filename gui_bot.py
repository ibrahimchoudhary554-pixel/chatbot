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
    /* Spacious Layout */
    .stChatMessage { margin-bottom: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE ENGINE SWAP (GEMINI 1.5 PRO) ---
try:
    # Force stable v1 configuration to stop the 404 v1beta cycle
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    kb_content = ""
    if os.path.exists("data.txt"):
        with open("data.txt", "r") as f:
            kb_content = f.read()

    # SWAPPED TO PRO MODEL: More stable, less likely to 404 on newer API calls
    model = genai.GenerativeModel(
        model_name='gemini-1.5-pro',
        system_instruction=(
            f"KNOWLEDGE: {kb_content}\n"
            "ROLE: You are an elite, savage terminal. "
            "1. Answer queries accurately using the KNOWLEDGE. "
            "2. Follow with a brutal, witty, adult-humor roast. "
            "3. Strictly Noir (Black/White). No emojis. No fluff."
        )
    )
except Exception as e:
    st.error(f"ENGINE_FAILURE: {e}")
    st.stop()

def get_sheet():
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    return gspread.authorize(creds).open("Chat logs").sheet1

# --- 3. SIDEBAR (SCOREBOARD & BURN) ---
st.sidebar.title("SYSTEM_LOGS")

if "tokens" not in st.session_state:
    st.session_state.tokens = 0
st.sidebar.write(f"BURNED_TOKENS: {st.session_state.tokens}")
st.sidebar.progress(min(st.session_state.tokens / 100000, 1.0))

st.sidebar.subheader("VICTIM_RANKING")
try:
    df = pd.DataFrame(get_sheet().get_all_records())
    if not df.empty:
        counts = df['Name'].value_counts().reset_index()
        counts.columns = ['Victim', 'Roasts']
        st.sidebar.table(counts.head(5))
except:
    st.sidebar.write("Syncing logs...")

# --- 4. AUTH ---
if "signed_in" not in st.session_state:
    st.session_state.signed_in = False

if not st.session_state.signed_in:
    st.title("AUTHENTICATION")
    with st.form("login"):
        n = st.text_input("IDENTIFIER")
        e = st.text_input("CREDENTIAL")
        if st.form_submit_button("CONNECT"):
            if "@" in e and n:
                st.session_state.user_name, st.session_state.user_email, st.session_state.signed_in = n, e, True
                st.rerun()
    st.stop()

# --- 5. TERMINAL ---
st.title("COMMAND_LINE_INTERFACE")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Input query..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Noir Safety Settings
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
        st.error(f"TERMINAL_FAILURE: {e}")
